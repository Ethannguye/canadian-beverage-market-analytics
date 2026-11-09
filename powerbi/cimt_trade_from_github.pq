// Power Query M. New Source > Blank Query > Advanced Editor.
// Rename query "CIMTTrade". Five Imports + five Total exports files, all official.
// NEVER also load the older CIMTImports query into the same model (duplicate import facts).
let
  Parse = (content as binary, flow as text) as table =>
    let
      Raw = Csv.Document(content, [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
      RemovedFirstTitle = Table.Skip(Raw,1),
      Header = Table.PromoteHeaders(RemovedFirstTitle,[PromoteAllScalars=true]),
      WithPeriodDate = Table.AddColumn(Header,"PeriodDate",each try Date.FromText([Period]) otherwise null,type date),
      Filtered = Table.SelectRows(WithPeriodDate,each [PeriodDate] <> null
                  and Date.Year([PeriodDate])>=2020 and Date.Year([PeriodDate])<=2025),
      Typed = Table.TransformColumnTypes(Filtered,{
         {"Period",type text},{"Commodity",type text},{"Province",type text},
         {"Country",type text},{"State",type text},{"Value ($)",type number},
         {"Quantity",type number},{"Unit of measure",type text}
      }),
      YearAdded = Table.AddColumn(Typed,"Year",each Date.Year([PeriodDate]),Int64.Type),
      CodeAdded = Table.AddColumn(YearAdded,"HSCode",
          each Text.Start(Text.Replace(Text.BeforeDelimiter([Commodity]," -"),".",""),6),type text),
      Categorized = Table.AddColumn(CodeAdded,"ProductGroup",each
          if [HSCode]="220110" then "Unsweetened mineral and aerated waters"
          else if [HSCode]="220190" then "Other waters plus ice and snow"
          else if [HSCode]="220210" then "Sweetened/flavoured waters"
          else if [HSCode]="220291" then "Non-alcoholic beer"
          else if [HSCode]="220299" then "Other non-alcoholic beverages"
          else "Unclassified",type text),
      FlowAdded = Table.AddColumn(Categorized,"TradeFlow",each flow,type text),
      Renamed = Table.RenameColumns(FlowAdded,{
          {"Country","PartnerCountry"},{"State","PartnerState"},
          {"Province","ReportingGeography"},{"Value ($)","ValueCAD"},
          {"Quantity","QuantityLitres"}})
    in
      Renamed,
  Origin = "https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/",
  Import110 = Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/I2201.10.csv"),"Import"),
  Import190 = Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/I2201.90.csv"),"Import"),
  Export110 = Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/E2201.10.csv"),"Export"),
  Export190 = Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/E2201.90.csv"),"Export"),
  Import210 = Parse(Web.Contents(Origin & "2202.10.csv"),"Import"),
  Import291 = Parse(Web.Contents(Origin & "2202.91.csv"),"Import"),
  Import299 = Parse(Web.Contents(Origin & "2202.99.csv"),"Import"),
  Export210 = Parse(Web.Contents(Origin & "E2202.10.csv"),"Export"),
  Export291 = Parse(Web.Contents(Origin & "E2202.91.csv"),"Export"),
  Export299 = Parse(Web.Contents(Origin & "E2202.99.csv"),"Export"),
  Combined = Table.Combine({Import110,Import190,Import210,Import291,Import299,Export110,Export190,Export210,Export291,Export299})
in
  Combined
