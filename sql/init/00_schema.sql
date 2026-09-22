-- Bronze (raw): kaynaktan geldiği gibi, tipler gevşek. Kirli olması NORMAL.
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS quarantine;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE raw.subscribers (
  subscriber_id    bigint,
  msisdn           text,          -- format karışık: +905..., 05..., 905..., 5...
  plan_id          text,
  status           text,          -- ACTIVE / active / Aktif / SUSPENDED / CHURNED / churned
  activation_date  date,
  city             text,
  segment          text
);

CREATE TABLE raw.cdr_events (
  event_id      text,             -- TEKİL DEĞİL: kaynak ~%2 duplicate gönderir
  msisdn        text,
  event_type    text,             -- voice/sms/data + casing varyantları + %0.3 geçersiz
  event_ts      timestamp,        -- UTC, olayın zamanı
  duration_sec  integer,
  bytes         bigint,
  cell_id       text,
  country_code  text,
  ingested_at   timestamp         -- UTC, warehouse'a giriş; event_ts'ten 0-72 saat sonra
);

CREATE TABLE raw.recharges (
  recharge_id   bigint,
  msisdn        text,
  amount_try    numeric(10,2),
  channel       text,             -- APP / WEB / DEALER / BANK / IVR
  recharge_ts   timestamp
);

CREATE TABLE raw.campaigns (
  campaign_id     text,
  name            text,
  start_date      date,
  end_date        date,
  target_segment  text
);

CREATE TABLE raw.campaign_responses (
  response_id   bigint,
  campaign_id   text,
  msisdn        text,
  responded_at  timestamp,
  accepted      boolean
);

CREATE TABLE raw.plan_changes (
  msisdn       text,
  old_plan_id  text,
  new_plan_id  text,
  changed_at   timestamp
);

CREATE TABLE raw.plans (
  plan_id      text,
  plan_name    text,
  plan_family  text,
  monthly_fee  numeric(10,2)
);

CREATE TABLE raw.corporate_accounts (
  account_id         text,
  parent_account_id  text,
  account_name       text,
  msisdn             text
);