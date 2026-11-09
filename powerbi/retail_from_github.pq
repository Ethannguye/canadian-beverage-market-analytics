// Power Query (M) for Power BI Desktop > Get Data > Blank Query > Advanced Editor.
// Source: reviewed small curated CSV in the public GitHub repository (updated via commits).
let
    Source = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/curated/retail_beverage_2020_2025.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Promoted, {
        {"reference_period", type text}, {"year", Int64.Type},
        {"product_group", type text}, {"napcs_code", type text},
        {"classification_vintage", type text}, {"source_vector", type text},
        {"value_cad_thousands", type number}, {"source_table", type text},
        {"comparability_segment", type text}
    }),
    PeriodDate = Table.AddColumn(Types, "PeriodDate",
        each Date.FromText([reference_period] & "-01"), type date),
    CADMillions = Table.AddColumn(PeriodDate, "sales_cad_millions",
        each [value_cad_thousands] / 1000, type number)
in
    CADMillions
