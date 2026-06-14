import requests
import pandas as pd
from sqlalchemy import create_engine

BLS_API_KEY = "api_key"
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost:5432/bls_db"

series_ids = ["LASST210000000000003", # Kentucky unemployment rate
    "LASST210000000000004", # Kentucky employment level
    "LASST210000000000005", # Kentucky labor force
    "SMU21311403000000001", # Louisville manufacturing employment
    "SMU21311406500000001", # Louisville private education and health services employment
    "SMU21311404300000001", # Louisville transportation, warehousing, and utilities employment
    "SMU21311404200000001", # Louisville retail trade employment
    "SMU21311409000000001"]  # Louisville government employment

# Connecting IDs from each BLS series to the tables in PostgreSQL
series_metadata = {"LASST210000000000003": {"metric_id": 1, "geography_id": 2, "industry_id": None, "demographic_id": 1},
    "LASST210000000000004": {"metric_id": 2, "geography_id": 2, "industry_id": None, "demographic_id": 1},
    "LASST210000000000005": {"metric_id": 3, "geography_id": 2, "industry_id": None, "demographic_id": 1},
    "SMU21311403000000001": {"metric_id": 2, "geography_id": 1, "industry_id": 1, "demographic_id": 1},
    "SMU21311406500000001": {"metric_id": 2, "geography_id": 1, "industry_id": 2, "demographic_id": 1},
    "SMU21311404300000001": {"metric_id": 2, "geography_id": 1, "industry_id": 3, "demographic_id": 1},
    "SMU21311404200000001": {"metric_id": 2, "geography_id": 1, "industry_id": 4, "demographic_id": 1},
    "SMU21311409000000001": {"metric_id": 2, "geography_id": 1, "industry_id": 5, "demographic_id": 1}}

start_year = "2020"
end_year = "2024"

url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

payload = {
    "seriesid": series_ids,
    "startyear": start_year,
    "endyear": end_year,
    "registrationkey": BLS_API_KEY
}

#Extracting data from the BLS API
try:
    response = requests.post(url, json=payload)
    response.raise_for_status() #Raises an error if the request fails
    data = response.json()

except Exception as error:
    print(f"API extraction failed: {error}")
    raise

#Checking if API was successfully requested
if data["status"] != "REQUEST_SUCCEEDED":
    raise Exception(f"API request failed: {data.get('message')}")

series_rows = []
observation_rows = []

#Transforming JSON into normalized rows
try:
    for series in data["Results"]["series"]:
        series_id = series["seriesID"]

        metadata = series_metadata[series_id]

        series_rows.append({
            "series_id": series_id,
            "metric_id": metadata["metric_id"],
            "geography_id": metadata["geography_id"],
            "industry_id": metadata["industry_id"],
            "demographic_id": metadata["demographic_id"]})
        
        for obs in series["data"]:
            observation_rows.append({
                "series_id": series_id,
                "year": int(obs["year"]),
                "period": obs["period"],
                "value": float(obs["value"])})

    df_series = pd.DataFrame(series_rows).drop_duplicates() #Converting to DataFrames and dropping duplicates
    df_observations = pd.DataFrame(observation_rows)
    #Dropping uplicate records so the same monthly observation is not loaded more than once (incremental loading strategy)
    df_observations = df_observations.drop_duplicates(subset=["series_id", "year", "period"])

except Exception as error:
    print(f"Data transformation failed: {error}")
    raise

# Data validation and quality checks
try:
    if df_series.empty:
        raise Exception("Series dataframe is empty.")

    if df_observations.empty:
        raise Exception("Observations dataframe is empty.")

    if df_series["series_id"].isnull().any():
        raise Exception("Series ID contains null values.")

    if df_observations["series_id"].isnull().any():
        raise Exception("Series ID contains null values.")

    if df_observations["year"].isnull().any():
        raise Exception("Year contains null values.")

    if df_observations["period"].isnull().any():
        raise Exception("Period contains null values.")

    duplicates = df_observations.duplicated(subset=["series_id", "year", "period"]).sum()

    if duplicates > 0:
        raise Exception("Duplicate observation records were found.")
        
    if (df_observations["value"] < 0).any(): #unemployment rates are reported as percentages and cannot be negative
        raise Exception("Observation values cannot be negative.")
    
    if len(df_observations) == 0:
        raise Exception("No observation records were returned.") #Checking that records were successfully returned from the API

    print(f"Observation record count: {len(df_observations)}")

except Exception as error:
    print(f"Data validation failed: {error}")
    raise
print("Data validated successfully.")

#Derived Metrics
df_analytics["unemployment_rate_change"] = (df_analytics["value"].diff()) #month-over-month change in unemployment rate
df_analytics["highest_unemployment_rate"] = (df_analytics["value"].cummax()) #highest unemployment rate
df_analytics["lowest_unemployment_rate"] = (df_analytics["value"].cummin()) #lowest unemployment rate

#Exporting to CSV to import into Power BI
try:
    df_analytics = df_observations.merge(
        df_series,
        on="series_id",
        how="left")

    # Creating a date column for Power BI
    df_analytics["month"] = df_analytics["period"].str.replace("M", "", regex=False)
    df_analytics["date"] = pd.to_datetime(
        df_analytics["year"].astype(str) + "-" +
        df_analytics["month"] + "-01")

    df_analytics.to_csv("bls_analytics_dataset.csv", index=False)
    print("CSV created.")

except Exception as error:
    print(f"Analytics dataset creation failed: {error}")
    raise

#Loading data into PostgreSQL
try:
    engine = create_engine(DATABASE_URL)
    
    df_series.to_sql(
        "series",
        engine,
        if_exists="append",
        index=False)
    
    df_observations.to_sql(
        "observations",
        engine,
        if_exists="append",
        index=False)
    
    print("Data loaded into PostgreSQL successfully.")

except Exception as error:
    print(f"Database failed to load: {error}")
    raise
