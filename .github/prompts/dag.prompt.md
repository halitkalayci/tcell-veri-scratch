---
description: "Airflow DAG üret (airflow.instructions.md kurallarıyla)"
---
`airflow/dags/${input:dag_id}.py` DAG'ını yaz. airflow.instructions.md'deki ZORUNLU argümanların hepsi olmalı.

Görev: ${input:goal:DAG'ın işi (örn. günlük CDR yükleme + dbt run/test)}

- Task'lar atomik ve idempotent.
- Sensor varsa reschedule + timeout.
- Bitince `airflow dags test ${input:dag_id} 2026-09-01` komutunu çalıştırmak için gereken adımı söyle (container içinde).
- Sonda bir "operasyon kontrol listesi" yorum bloğu: catchup, start_date, retries, max_active_runs, connection kullanımı — her biri için ✓.