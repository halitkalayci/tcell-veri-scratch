#!/usr/bin/env python3
import subprocess, sys

def ok(m):   print(f"  ✅ {m}")
def bad(m):  print(f"  ❌ {m}")
def run(cmd):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except Exception: return None

print("telco-dw — ortam kontrolü\n")
v = sys.version_info
(ok if v >= (3, 10) else bad)(f"Python {v.major}.{v.minor}  (>=3.10 gerekli)")

for tool, cmd in [("docker", ["docker", "--version"]),
                  ("docker compose", ["docker", "compose", "version"]),
                  ("git", ["git", "--version"]),
                  ("dbt", ["dbt", "--version"])]:
    r = run(cmd)
    if r and r.returncode == 0:
        lines = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        ver = next((l for l in lines if "installed" in l), lines[0]) if lines else ""
        ok(f"{tool}: {ver.replace('- installed:', '').strip()}")
    else:
        bad(f"{tool} bulunamadı")

r = run(["docker", "exec", "telco_pg", "psql", "-U", "telco", "-d", "telco_dw", "-tAc",
         "select count(*) from raw.cdr_events"])
if r and r.returncode == 0:
    ok(f"Postgres (telco_pg) ayakta, raw.cdr_events satır: {r.stdout.strip()}")
else:
    bad("Postgres (telco_pg) yanıt vermiyor — sıra: "
        "1) python ..\\generate_data.py --quick --out data  "
        "2) docker compose up -d  (veri yokken kaldırdıysan: docker compose down -v)")

try:
    import psycopg2  # noqa: F401
    ok("psycopg2 kurulu")
except ImportError:
    bad("psycopg2 yok  ->  pip install psycopg2-binary  (Gün 2 / Airflow ve consumer için)")
