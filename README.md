# 🌤️ Air Quality Data Pipeline with Apache Airflow

This project implements a complete end-to-end data pipeline that collects air quality data from the [IQAir API](https://www.iqair.com/), stores it in a PostgreSQL database, and visualizes it with Tableau. The pipeline is orchestrated using Apache Airflow, containerized with Docker Compose, and automated via GitHub Actions with a self-hosted runner.

---

## 🚀 Project Overview

- ⏱️ **Scheduler**: Apache Airflow orchestrates the ETL process hourly (configurable)
- ☁️ **Data Source**: IQAir API providing real-time air quality metrics in **Bangkok, Thailand**, including:
  - AQI (US/China), PM2.5, temperature, humidity, wind, pressure
- 🗃️ **Data Sink**: PostgreSQL database for structured data storage
- 🔁 **Automation**: CI/CD using GitHub Actions + self-hosted runner to auto-deploy DAGs
- 📊 **Visualization**: Data available for BI tools like Tableau or Looker Studio

---

## 🧰 Tech Stack

| Tool               | Purpose                                      |
|--------------------|----------------------------------------------|
| Python             | API extraction and data processing           |
| Apache Airflow     | Workflow orchestration and DAG scheduling    |
| PostgreSQL         | Relational database to store time-series data|
| Docker Compose     | Local orchestration of containers            |
| GitHub Actions     | CI/CD pipeline for automatic DAG deployment  |
| Tableau            | BI dashboard for visualizing air quality     |

---

## 🔧 How It Works

1. **Extract**  
   An Airflow DAG fetches air quality data from IQAir API (Bangkok) every hour.

2. **Transform**  
   The API response is parsed and transformed into a flat, normalized schema.

3. **Load**  
   Data is inserted into a `air_quality` table in PostgreSQL.

4. **Deploy**  
   Upon any push to the `dags/` folder, GitHub Actions automatically:
   - Copies the DAG into the Airflow container
   - Restarts the scheduler for immediate DAG reload

5. **Visualize**  
   Data is connected to Tableau or Looker Studio for dashboarding.

---

## 🗃️ Database Schema

```sql
CREATE TABLE air_quality (
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
```

---

## 📂 Project Structure

```
air-quality-airflow/
├── dags/
│   └── iqair_air_quality_dag.py
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── deploy.yml
├── README.md
```

---

## 🔁 CI/CD Pipeline

- Trigger: `push` to `main` branch under `dags/`
- Runner: GitHub Actions with self-hosted runner on local machine
- Tasks:
  1. Checkout latest code
  2. Copy DAGs to Airflow webserver container
  3. Restart scheduler to reload updated DAGs

```bash
docker cp dags/. airflow-webserver:/opt/airflow/dags/
docker restart airflow-scheduler
```

> This ensures zero manual deployment steps – every DAG update is automatically applied.

---

## 📸 Sample Output

> _(Include screenshots below – Airflow UI, DAG Graph, or Tableau dashboard)_

- Airflow DAG graph view
- PostgreSQL sample records
- Tableau dashboard of AQI trends

---

## 🚀 Getting Started Locally

```bash
# Start all containers
docker-compose up -d

# Airflow Web UI
http://localhost:8080
# Login: airflow / airflow
```

---

## 📊 Visualization Preview (Tableau)

> [Insert dashboard screenshot or Tableau Public link here if available]

---

## 📌 Notes

- IQAir API used in the free tier (limited by request volume)
- Airflow version: 2.8.1
- PostgreSQL version: 13
- Schedule interval: customizable (default is hourly, can change to cron like `'25 * * * *'`)

---

## 🧑‍💻 Author

**Photsawat Buanuam**  
📫 [LinkedIn](https://www.linkedin.com/in/photsawat-buanuam)  
📁 GitHub: [Photsawat-hub](https://github.com/Photsawat-hub)

---

## 🏷️ Tags

`#Airflow` `#DataPipeline` `#CI/CD` `#GitHubActions`  
`#PostgreSQL` `#Python` `#Docker` `#IQAirAPI` `#Tableau`