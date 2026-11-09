// Power Query (M): use official CIMT raw CSVs checked into GitHub; original State preserved.
// New Source -> Blank Query -> Advanced Editor. Rename query CIMTImports.
// Source files have a "Imports" title and footer, not just a CSV header.
let
  Parse = (content as binary) as table =>
    let
      Raw=Csv.Document(content,[Delimiter=",",Columns=8,Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
      RemovedTitle=Table.Skip(Raw,1),
      Header=Table.PromoteHeaders(RemovedTitle,[PromoteAllScalars=true]),
      DateAdded=Table.AddColumn(Header,"PeriodDate",each try Date.FromText([Period]) otherwise null,type date),
      DataOnly=Table.SelectRows(DateAdded, each [PeriodDate] <> null and
                Date.Year([PeriodDate])>=2020 and Date.Year([PeriodDate])<=2025),
      Typed=Table.TransformColumnTypes(DataOnly,{{"Commodity",type text},{"Province",type text},
          {"Country",type text},{"State",type text},{"Value ($)",type number},
          {"Quantity",type number},{"Unit of measure",type text}}),
      Code=Table.AddColumn(Typed,"HSCode",each Text.Replace(Text.BeforeDelimiter([Commodity]," -"),".",""),type text),
      Group=Table.AddColumn(Code,"ProductGroup",each
          if [HSCode]="220210" then "Sweetened/flavoured waters"
          else if [HSCode]="220291" then "Non-alcoholic beer"
          else if [HSCode]="220299" then "Other non-alcoholic beverages"
          else "Unclassified",type text),
      Flow=Table.AddColumn(Group,"TradeFlow",each "Import",type text),
      Renamed=Table.RenameColumns(Flow,{{"Country","PartnerCountry"},
          {"State","PartnerState"},{"Province","ReportingGeography"},
          {"Value ($)","ValueCAD"},{"Quantity","QuantityLitres"}})
    in
      Renamed,
  Import210=Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/2202.10.csv")),
  Import291=Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/2202.91.csv")),
  Import299=Parse(Web.Contents("https://raw.githubusercontent.com/Ethannguye/canadian-beverage-market-analytics/main/data/source_exports/cimt/2202.99.csv")),
  Combined=Table.Combine({Import210,Import291,Import299})
in
  Combined
