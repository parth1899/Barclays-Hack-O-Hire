"""ETL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/121zT6Yciyi7VlUowbdsmgbR-zz7qo7b3
"""


from yahoo_fin.stock_info import get_data
import pandas as pd
import yahoo_fin.stock_info as si
from yahoo_fin.stock_info import get_quote_table
from pyspark.sql import SparkSession
from pymongo import MongoClient

from typing import Dict
import yfinance as yf


def get_ticker_metadata(ticker: str) -> Dict[str, str]:
    result = {"company_name": "not_found",
              "market_cap": "not_found"}
    try:
        info = yf.Ticker(ticker).info
        if info:
            if 'longName' in info:
                result["company_name"] = info['longName']
            if "marketCap" in info:
                result["market_cap"] = str(round((info['marketCap']/1000000000), 2))
    except Exception as e:
        print(e)

    return result

tickerCommunications = ["GOOG","META","VZ","CHTR","ADTN","HIVE","AUDC","ALLT","AVNW","ATEN","AMPG","AKTS","ANDR","CUDA","BOSC","HEAR","NOK","CIEN","INFN","CALX","SATS","COMM","KN","CMTL","CLRO","TCCO","OCC","CRNT","CLFD","ZSTN","FEIM","ELST","FKWL","GILT","HLIT","MFON","QCOM","MSI","NTGR","KVHI","VSAT","VIAV","RITT","MITL","NTIP","WSTL"]
tickerIndustrial = ["CAT","GE","UNP","ETN","ARLP","AOS","AMSC","AIN","HOLI","ASM","AIT","AUMN","APWC","AUSI","AGIN","ABKI","ASPW","AMNL","AMLM","BTU","BHP","B","BGC","BLDP","BDC","BVN","SVBL","BW","EMR","FAST","CMCT","CLF","PH","MNR","CCJ","MSM","TRNO","MTRN","CMP","LEU","DNN","TRS","FELE","CHNR","PZG","LIME","SXI"]
tickerEstate = ["PLD","SPG","WELL","PSA","BAM","ALEX","NEN","GRBK","XIN","JOE","MLP","CTO","FOR","LGIH","INN","MMI","STRS","IRS","TPL","ROII","PRSI","PPCQ"]
tickerHealth=["LLY","UNH","JNJ","MRK","AET","AFL","AIZ","AMED","ADUS","FMS","ACHC","AFAM","PAHC","AMS","AMEH","CVS","ESRX","CI","CNC","CNO","SBRA","CHE","GLRE","PRA","CPSI","DVA","DOC","DIGP","EIG","EVH","UNH","GEO","UNM","HCP","HUM","OHI","HR","MOH","NHI","HSTM","INOV","STRM","UHT","MRGE","HQY","PFHO","VTR","LTC","MPW","VEEV","OMCL","TDOC"]
tickerTechnology = ["NVDA","DLO","YMM","GTLB","AMGN","ACN","ADSK","ACAD","ARRY","FOLD","ACOR","ACIW","AGIO","AVXL","ALNY","LIFE","ADXS","ACM","AGEN","SAIC","ANTH","AMPE","ARWR","AKBA","AEZS","ACST","AMBS","ARDX","ANIK","ATNM","ANIP","DGLY","ADMA","JAGX","HMNY","AMRC","ABIO","TEAM","ADAP","ALDX","ABUS","AXON","ASND","AFMD","AFFY","DYSL","AERG","SIGL","ALSE","ARNI","PSSR","CRYO","IBM","BIIB","BDSI","GALE","BMRN","KERX","PACB","BLCM","PBYI","EBS","BLUE","BCRX","NWBO","SGMO","BMI","TECH","NAVB","CALA","CANF","PLX"]

sector_mapping = {}
for ticker in tickerCommunications:
    sector_mapping[ticker] = "Communications"
for ticker in tickerIndustrial:
    sector_mapping[ticker] = "Industrial"
for ticker in tickerEstate:
    sector_mapping[ticker] = "Real Estate"
for ticker in tickerHealth:
    sector_mapping[ticker] = "Healthcare"
for ticker in tickerTechnology:
    sector_mapping[ticker] = "Technology"

def get_sector(ticker):
    return sector_mapping.get(ticker)

data_list_communications = [pd.DataFrame(get_data(ticker, index_as_date=True, start_date="01/01/2006", end_date="01/01/2024", interval="1d")) for ticker in tickerCommunications]

data_communications = pd.concat(data_list_communications)
data_communications['Date'] = data_communications.index

# data_communications['Date'] = data_communications.index
# data_communications.set_index("Date", inplace=True)

data_communications["Sector"] = data_communications["ticker"].apply(get_sector)
data_communications.dropna(inplace=True)

for ticker in tickerCommunications:
    market_cap = get_ticker_metadata(ticker)['market_cap']
    data_communications.loc[data_communications['ticker'] == ticker, 'Capital'] = market_cap
    if(market_cap != 'not_found'):
      if float(market_cap) > 10 :
          data_communications.loc[data_communications['ticker'] == ticker, 'CategoryId'] = 3
      elif 2 < float(market_cap) < 10:
          data_communications.loc[data_communications['ticker'] == ticker, 'CategoryId'] = 2
      elif float(market_cap) < 2:
          data_communications.loc[data_communications['ticker'] == ticker, 'CategoryId'] = 1

data_list_industry = [pd.DataFrame(get_data(ticker, index_as_date=True,start_date="01/01/2006", end_date="01/01/2024", interval="1d")) for ticker in tickerIndustrial]

data_industry = pd.concat(data_list_industry)
data_industry['Date'] = data_industry.index
#data_industry.set_index("Date", inplace=True)

data_industry["Sector"] = data_industry["ticker"].apply(get_sector)
data_industry.dropna(inplace=True)

for ticker in tickerIndustrial:
    market_cap = get_ticker_metadata(ticker)['market_cap']
    data_industry.loc[data_industry['ticker'] == ticker, 'Capital'] = market_cap
    if(market_cap != 'not_found'):
      if float(market_cap) > 10 :
          data_industry.loc[data_industry['ticker'] == ticker, 'CategoryId'] = 3
      elif 2 < float(market_cap) < 10:
          data_industry.loc[data_industry['ticker'] == ticker, 'CategoryId'] = 2
      elif float(market_cap) < 2:
          data_industry.loc[data_industry['ticker'] == ticker, 'CategoryId'] = 1

pd.set_option('display.float_format', lambda x: '%.6f' % x)

data_list_estate = [pd.DataFrame(get_data(ticker, index_as_date=True,start_date="01/01/2006", end_date="01/01/2024", interval="1d")) for ticker in tickerEstate]
data_estate = pd.concat(data_list_estate)
data_estate['Date'] = data_estate.index
#data_estate.set_index("Date", inplace=True)

data_estate["Sector"] = data_estate["ticker"].apply(get_sector)
data_estate.dropna(inplace=True)

for ticker in tickerEstate:
    market_cap = get_ticker_metadata(ticker)['market_cap']
    data_estate.loc[data_estate['ticker'] == ticker, 'Capital'] = market_cap
    if(market_cap != 'not_found'):
      if float(market_cap) > 10 :
          data_estate.loc[data_estate['ticker'] == ticker, 'CategoryId'] = 3
      elif 2 < float(market_cap) < 10:
          data_estate.loc[data_estate['ticker'] == ticker, 'CategoryId'] = 2
      elif float(market_cap) < 2:
          data_estate.loc[data_estate['ticker'] == ticker, 'CategoryId'] = 1
data_estate.dropna(inplace=True)

data_list_health = [pd.DataFrame(get_data(ticker, index_as_date=True,start_date="01/01/2006", end_date="01/01/2024", interval="1d")) for ticker in tickerHealth]

data_health = pd.concat(data_list_health)
data_health['Date'] = data_health.index
#data_health.set_index("Date", inplace=True)

data_health["Sector"] = data_health["ticker"].apply(get_sector)
data_health.dropna(inplace=True)

for ticker in tickerHealth:
    market_cap = get_ticker_metadata(ticker)['market_cap']
    data_health.loc[data_health['ticker'] == ticker, 'Capital'] = market_cap
    if(market_cap != 'not_found'):
      if float(market_cap) > 10 :
          data_health.loc[data_health['ticker'] == ticker, 'CategoryId'] = 3
      elif 2 < float(market_cap) < 10:
          data_health.loc[data_health['ticker'] == ticker, 'CategoryId'] = 2
      elif float(market_cap) < 2:
          data_health.loc[data_health['ticker'] == ticker, 'CategoryId'] = 1
data_health.dropna(inplace=True)

data_list_tech = [pd.DataFrame(get_data(ticker, index_as_date=True,start_date="01/01/2006", end_date="01/01/2024", interval="1d")) for ticker in tickerTechnology]

data_tech = pd.concat(data_list_tech)
data_tech['Date'] = data_tech.index
#data_tech.set_index("Date", inplace=True)

data_tech["Sector"] = data_tech["ticker"].apply(get_sector)
data_tech.dropna(inplace=True)

for ticker in tickerTechnology:
    market_cap = get_ticker_metadata(ticker)['market_cap']
    data_tech.loc[data_tech['ticker'] == ticker, 'Capital'] = market_cap
    if(market_cap != 'not_found'):
      if float(market_cap) > 10 :
          data_tech.loc[data_tech['ticker'] == ticker, 'CategoryId'] = 3
      elif 2 < float(market_cap) < 10:
          data_tech.loc[data_tech['ticker'] == ticker, 'CategoryId'] = 2
      elif float(market_cap) < 2:
          data_tech.loc[data_tech['ticker'] == ticker, 'CategoryId'] = 1
data_tech.dropna(inplace=True)

combined_data = pd.concat([data_communications, data_industry,data_health,data_estate,data_tech], ignore_index=True)

combined_data["mid"] = (combined_data['high'] + combined_data['low']) / 2

desired_columns = ['Date','ticker', 'Sector', 'volume','Capital', 'low','high', 'mid', 'open',   'close', 'adjclose','CategoryId']
combined_data = combined_data.reindex(columns=desired_columns)

combined_data = combined_data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'adjclose': 'Adj Close',
    'volume': 'Volume',
    'ticker': 'Ticker',
    'Capital': 'Capital',
    'CategoryId': 'CategoryId',
    'mid': 'Average'
})

combined_data.dropna(inplace=True)

combined_data["Capital"] = combined_data["Capital"].astype(float)
combined_data.drop(columns=["Adj Close"])

combined_data

"""combined_data.info()"""

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("TradingData") \
    .getOrCreate()

# Convert the list of dictionaries to a Spark DataFrame
df = spark.createDataFrame(combined_data)

# Print the number of rows in the DataFrame
print("Number of rows in the DataFrame:", df.count())

# Convert DataFrame back to a list of dictionaries
formatted_data_list = [row.asDict() for row in df.collect()]



df.show()

# Create a MongoDB client
client = MongoClient("mongodb+srv://sanjayparth22:sanjayP37@cluster0.r9enpld.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Access the database
db = client["Hackathon"]

# Access the collection
collection = db["Stock-Data-Final"]

collection.insert_many(formatted_data_list)