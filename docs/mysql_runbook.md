# MySQL runbook (MySQL Workbench / MySQL 8+)

1. Install MySQL 8 and `pip install -r requirements.txt`.
2. Open `sql/01_schema.sql` in MySQL Workbench and execute it **once**.
3. Review `data/processed/<PID>_staging.csv` and its profile JSON.
4. Set credentials through environment variables (never commit a password):
   ```bash
   export MYSQL_HOST=localhost
   export MYSQL_PORT=3306
   export MYSQL_DATABASE=canadian_beverage_market
   export MYSQL_USER=root
   export MYSQL_PASSWORD='your-local-password'
   python etl/load_mysql.py --tables 32100054
   ```
5. Run `sql/02_load.sql`. Inspect the candidate query and the StatCan metadata and source dimension definitions.
6. **Approve individual VERIFIED series only.** Example syntax is provided in 02_load.sql.
7. Execute `CALL sp_materialize_approved_facts();` after approval.
8. Run `sql/03_validation.sql`, then `sql/04_analytical_views.sql`.

**Important:** 01_schema.sql contains foreign-key creation for the fact tables. Recreating the entire schema by rerunning the file may raise duplicate constraint errors on existing tables; for repeat schema setup use a fresh empty database or a migration. Do not DROP the database to clear data unless you intentionally want to lose all loaded rows.

The `fact_...` tables retain **value_as_published**, `unit_label` and `scalar_factor` separately. Convert to dollars or litres only after verifying source definitions. CPI should never be summed.

## Current deliberate limits
- The pipeline stages data; it does not auto-approve a single beverage category.
- Retail 2020–2022 and 2023–2025 remain separate vintages.
- Country-level HS commodity imports require a verified CIMT export.
- Views may return zero rows until review and approval are completed.
