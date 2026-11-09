# Project execution tracker — updated November 9, 2026

| Workstream | Actual status | Evidence / remaining gate |
|---|---|---|
| GitHub repository and source registry | DONE | README, metadata/source_inventory.csv |
| Python ETL and discovery automation | DONE for five sources | WDS manifest SHA256, CSV staging and GitHub Actions runs |
| Retail product source extracts | DATA READY | 144 rows, 2 leaf groups, split NAPCS vintages; cross-vintage audit remains |
| CPI price-index data | DATA READY | 360 rows, 5 official vectors, 72 months each |
| Food availability | DATA READY WITH GAPS | 24 rows; 2024 missing in 3 usable liquid series; bottled water unavailable |
| Manufacturing Ontario / Québec | DATA READY | 144 rows, NAICS 31211, unadjusted; includes ice |
| Python tests | PASS on recent runs | Curated-data test newly added; continue verifying on main |
| MySQL DDL/views/procedure | PASS (GitHub Actions MySQL 8) | Original validation run 42567637131; code updated to preserve US partner states; rerun CI with current schema |
| MySQL loaded market data | NOT YET | Needs MySQL connection, staging ingestion, review and validation |
| Industry-trade full-table 12-10-0176-01 | DEFERRED | Official ZIP exceeds 600 MB safety limit; no large-file commit |
| HS country/commodity imports + exports | **2202 TRADE FLOWS READY** | 24,634 source observations, 72 months per HS6/flow, 216 monthly HS trade balances; still need 2201 and 2009 |
| Power BI M queries (domestic + both trade flows) | READY TO USE | Four domestic .pq queries plus one combined six-source CIMT trade .pq; Power BI Desktop required |
| Complete six-page .pbix | NOT YET | Requires Power BI Desktop and additional reviewed measures and HS trade |
| Final business recommendations | PARTIAL HS2202 TRADE INSIGHTS | Now import/export/balance verified; broader product coverage, HS comparability review and final PBIX needed |

**Do not misread 'DATA READY' as 'database loaded' or 'Power BI completed'.** These are separate milestones, and future findings depend on the data remaining comparable.
