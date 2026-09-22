---
applyTo: "airflow/dags/**/*.py"
---
# Airflow DAG kuralları (Airflow 2.10, TaskFlow API)
- `@dag` / `@task` dekoratörleri; klasik Operator sadece gerektiğinde (Bash, Sensor).
- ZORUNLU DAG argümanları: sabit `start_date` (asla `datetime.now()`), `catchup=False`, `max_active_runs=1`, `default_args={'retries': 3, 'retry_delay': timedelta(minutes=5), 'retry_exponential_backoff': True}`.
- Sensor'larda `mode='reschedule'`, `poke_interval`, `timeout` zorunlu.
- Tarih her zaman `{{ ds }}` / `data_interval_start` context'inden gelir; Python `date.today()` kullanılmaz (backfill'i bozar).
- Her task idempotent: aynı `ds` için ikinci çalıştırma veri katlamaz (önce DELETE / upsert).
- Bağlantılar `Connection` (conn_id='telco_pg'), ayarlar `Variable`; koda gömülü host/şifre yok.
- Branch sonrası birleşme task'ında `trigger_rule='none_failed_min_one_success'`.
- Her task'a `doc_md`; DAG'a `doc_md` + `tags`.
- dbt komutları: `dbt --project-dir /opt/airflow/dbt/telco_dw --profiles-dir /opt/airflow/dbt`.