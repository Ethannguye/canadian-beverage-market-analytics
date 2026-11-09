# Where your help becomes useful

At this stage, four source-attributed CSV datasets are committed to GitHub and can be imported directly by the provided Power Query scripts. The two unmet external-action steps are:

1. **CIMT export:** Please use the [official CIMT tool](https://www150.statcan.gc.ca/n1/en/catalogue/71-607-X2021004) to export authentic Canadian HS trade for imports, at least HS **2202**, 2020–2025, by partner country if available, and upload the original CSV or Excel file to this chat. The full industry table `12-10-0176-01` exceeds the 600 MB download cap and is not an acceptable replacement for HS-by-partner data. Full requirements: `docs/cimt_export_guide.md`.
2. **Windows Power BI Desktop:** When convenient, open `powerbi/QUICKSTART_CSV.md` and load the four queries. Save the resulting .pbix and share it for QA. The CSV route does not require setting up MySQL.

No passwords or GitHub tokens should be shared. Do not upload a file created by manually typing guessed market values. The next technical work for this project is to validate and map the partner trade exports, complete MySQL fact loading, and build all six dashboard pages.
