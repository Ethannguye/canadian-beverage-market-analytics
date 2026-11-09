// Power Query (M) for Power BI Desktop > Get Data > Blank Query > Advanced Editor.
let
    Source = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/curated/food_availability_2020_2025.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Promoted, {
        {"year", Int64.Type}, {"product", type text},
        {"source_vector", type text}, {"unit_of_measure", type text},
        {"value", type number}, {"value_status", type text},
        {"source_table", type text}
    })
in
    Types
