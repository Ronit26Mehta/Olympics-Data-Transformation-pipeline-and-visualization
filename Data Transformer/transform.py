from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg
import dask.dataframe as dd
import pandas as pd
import mysql.connector
import pickle  # To save dataframes for the dashboard

# MySQL connection settings
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ronit",
    "database": "olp"
}

# Initialize PySpark
spark = SparkSession.builder \
    .appName("Olympics Big Data Processing") \
    .getOrCreate()

# Dask Data Extraction and Preprocessing
def fetch_data_with_dask():
    """
    Fetch all data from MySQL using Dask and preprocess it.
    """
    try:
        # Connect to MySQL and fetch data
        db = mysql.connector.connect(**MYSQL_CONFIG)
        query = "SELECT * FROM olympics_data"
        df = pd.read_sql(query, db)
        db.close()

        # Convert to Dask DataFrame
        dask_df = dd.from_pandas(df, npartitions=4)

        # Preprocess: drop null values
        dask_df = dask_df.dropna()

        print("Data fetched and preprocessed using Dask.")
        return dask_df
    except Exception as e:
        print(f"Error fetching data with Dask: {str(e)}")
        return None

# PySpark Data Analytics
def spark_transformations(dask_df):
    """
    Perform PySpark transformations and analytics.
    """
    try:
        # Convert Dask DataFrame to Pandas for Spark compatibility
        pandas_df = dask_df.compute()

        # Load Pandas DataFrame into Spark
        spark_df = spark.createDataFrame(pandas_df)

        # Analytics
        medal_count = spark_df.groupBy("Country", "Year") \
            .agg(count("Medal").alias("Total_Medals")) \
            .orderBy(col("Total_Medals").desc())

        avg_age_by_sport = spark_df.groupBy("Sport") \
            .agg(avg("Age").alias("Average_Age")) \
            .orderBy(col("Average_Age"))

        medal_distribution = spark_df.groupBy("Medal") \
            .agg(count("Medal").alias("Count")) \
            .orderBy(col("Count").desc())
        print("=== Total Medals by Country and Year ===")
        medal_count.show()

        print("=== Average Age Distribution by Sport ===")
        avg_age_by_sport.show()

        print("=== Medal Count Distribution by Type ===")
        medal_distribution.show()

        # Convert results back to Pandas for Dash/Plotly compatibility
        return {
            "medal_count": medal_count.toPandas(),
            "avg_age_by_sport": avg_age_by_sport.toPandas(),
            "medal_distribution": medal_distribution.toPandas()
        }
    except Exception as e:
        print(f"Error during PySpark transformations: {str(e)}")
        return None

# Main Execution
if __name__ == "__main__":
    # Step 1: Fetch and preprocess data using Dask
    dask_df = fetch_data_with_dask()
    if dask_df is None:
        print("Data extraction failed. Exiting.")
    else:
        # Step 2: Perform PySpark analytics
        analytics_results = spark_transformations(dask_df)

        if analytics_results:
            print("Analytics completed. Saving results for the dashboard...")

            # Save the results to a file for the dashboard
            with open("analytics_results.pkl", "wb") as f:
                pickle.dump(analytics_results, f)

            print("Results saved successfully.")
        else:
            print("Analytics failed.")
