from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import psycopg2
import pandas as pd

API_KEY = '371dceb7-7931-4ac2-83ec-ef7e53d9f932'  
CITY = 'Bangkok'
STATE = 'Bangkok'
COUNTRY = 'Thailand'

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def fetch_data(**kwargs):
    url = f"http://api.airvisual.com/v2/city?city={CITY}&state={STATE}&country={COUNTRY}&key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()['data']
    kwargs['ti'].xcom_push(key='raw_data', value=data)

def transform_data(**kwargs):
    data = kwargs['ti'].xcom_pull(key='raw_data', task_ids='fetch_data')
    pollution = data['current']['pollution']
    weather = data['current']['weather']

    record = {
        'timestamp': pollution['ts'],
        'city': data['city'],
        'state': data['state'],
        'country': data['country'],
        'aqi_us': pollution['aqius'],
        'aqi_cn': pollution['aqicn'],
        'main_pollutant_us': pollution['mainus'],
        'main_pollutant_cn': pollution['maincn'],
        'temperature_c': weather['tp'],
        'pressure_hpa': weather['pr'],
        'humidity': weather['hu'],
        'wind_speed': weather['ws'],
        'wind_direction': weather['wd'],
        'weather_icon': weather['ic']
    }
    kwargs['ti'].xcom_push(key='transformed_data', value=record)

def load_to_postgres(**kwargs):
    record = kwargs['ti'].xcom_pull(key='transformed_data', task_ids='transform_data')

    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS air_quality (
            timestamp TIMESTAMP,
            city TEXT,
            state TEXT,
            country TEXT,
            aqi_us INTEGER,
            aqi_cn INTEGER,
            main_pollutant_us TEXT,
            main_pollutant_cn TEXT,
            temperature_c INTEGER,
            pressure_hpa INTEGER,
            humidity INTEGER,
            wind_speed REAL,
            wind_direction INTEGER,
            weather_icon TEXT
        );
    """)

    cur.execute("""
        INSERT INTO air_quality (
            timestamp, city, state, country,
            aqi_us, aqi_cn, main_pollutant_us, main_pollutant_cn,
            temperature_c, pressure_hpa, humidity,
            wind_speed, wind_direction, weather_icon
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        record['timestamp'],
        record['city'],
        record['state'],
        record['country'],
        record['aqi_us'],
        record['aqi_cn'],
        record['main_pollutant_us'],
        record['main_pollutant_cn'],
        record['temperature_c'],
        record['pressure_hpa'],
        record['humidity'],
        record['wind_speed'],
        record['wind_direction'],
        record['weather_icon']
    ))

    conn.commit()
    cur.close()
    conn.close()

with DAG(
    dag_id='iqair_air_quality_pipeline',
    default_args=default_args,
    start_date=datetime(2025, 5, 20),
    schedule_interval='25 * * * *',
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True,
    )

    t3 = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_to_postgres,
        provide_context=True,
    )

    t1 >> t2 >> t3