\echo 'Loading raw tables from /data ...'
COPY raw.subscribers        FROM '/data/raw_subscribers.csv'        CSV HEADER;
COPY raw.cdr_events         FROM '/data/raw_cdr_events.csv'         CSV HEADER;
COPY raw.recharges          FROM '/data/raw_recharges.csv'          CSV HEADER;
COPY raw.campaigns          FROM '/data/raw_campaigns.csv'          CSV HEADER;
COPY raw.campaign_responses FROM '/data/raw_campaign_responses.csv' CSV HEADER;
COPY raw.plan_changes       FROM '/data/raw_plan_changes.csv'       CSV HEADER;
COPY raw.plans              FROM '/data/raw_plans.csv'              CSV HEADER;
COPY raw.corporate_accounts FROM '/data/raw_corporate_accounts.csv' CSV HEADER;
ANALYZE;
\echo 'Row counts:'
SELECT 'subscribers' t, count(*) FROM raw.subscribers
UNION ALL SELECT 'cdr_events', count(*) FROM raw.cdr_events
UNION ALL SELECT 'recharges', count(*) FROM raw.recharges
UNION ALL SELECT 'plan_changes', count(*) FROM raw.plan_changes;