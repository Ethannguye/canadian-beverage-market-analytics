// Power Query M: Ontario and Quebec manufacturing shipments from official Statistics Canada.
let
    Source=Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/curated/manufacturing_soft_drinks_2020_2025.csv"),
        [Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]
    ),
    Promoted=Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Types=Table.TransformColumnTypes(Promoted,{
        {"reference_period",type text},{"year",Int64.Type},{"province",type text},
        {"naics_code",type text},{"industry_name",type text},
        {"source_vector",type text},{"shipments_cad_thousands",type number},
        {"adjustment",type text},{"source_table",type text}
    }),
    PeriodDate=Table.AddColumn(Types,"PeriodDate",each Date.FromText([reference_period]&"-01"),type date),
    CADMillions=Table.AddColumn(PeriodDate,"shipments_cad_millions",each [shipments_cad_thousands]/1000,type number)
in
    CADMillions
