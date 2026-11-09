// Power Query M: load a verified five-series CPI dataset, no MySQL required.
let
    Source = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/curated/cpi_beverages_2020_2025.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Promoted, {
        {"reference_period", type text},{"year",Int64.Type},{"geography",type text},
        {"product_category",type text},{"source_vector",type text},
        {"cpi_index",type number},{"base_year",type text},{"source_table",type text}
    }),
    PeriodDate=Table.AddColumn(Types, "PeriodDate",
        each Date.FromText([reference_period] & "-01"),type date)
in
    PeriodDate
