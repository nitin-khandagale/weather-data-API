import logging
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("weather_analysis.log"),  # Write to file
        logging.StreamHandler(),  # Print to console
    ],
)


# Connect to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# Function to log messages
def log_message(message, level=logging.INFO):
    logging.log(level, message)


# Function to calculate yearly statistics for a weather station
def calculate_yearly_statistics(connection):
    log_message("Starting yearly statistics calculation")

    cursor = connection.cursor()

    # Query to get all weather data
    query = """
        SELECT weather_station_id, 
               EXTRACT(YEAR FROM record_date) AS year, 
               max_temperature, 
               min_temperature, 
               precipitation
        FROM weather_data
        WHERE max_temperature IS NOT NULL 
          OR min_temperature IS NOT NULL 
          OR precipitation IS NOT NULL;
    """

    cursor.execute(query)

    # Load query results into a pandas DataFrame
    df = pd.DataFrame(
        cursor.fetchall(),
        columns=["weather_station_id", "year", "max_temp", "min_temp", "precipitation"],
    )

    # Convert necessary columns to float types
    df["max_temp"] = df["max_temp"].astype(float)
    df["min_temp"] = df["min_temp"].astype(float)
    df["precipitation"] = df["precipitation"].astype(float)

    # Group by weather_station_id and year to calculate statistics
    yearly_stats = (
        df.groupby(["weather_station_id", "year"])
        .agg(
            {
                "max_temp": lambda x: x.dropna().mean()
                / 10.0,  # Convert tenths of a degree Celsius to Celsius
                "min_temp": lambda x: x.dropna().mean() / 10.0,
                "precipitation": lambda x: x.dropna().sum()
                / 100.0,  # Convert tenths of a millimeter to centimeters
            }
        )
        .reset_index()
    )

    # Insert the calculated statistics into the new table
    insert_query = """
        INSERT INTO weather_yearly_statistics (weather_station_id, year, avg_max_temperature, avg_min_temperature, total_precipitation)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (weather_station_id, year) DO NOTHING;
    """

    records_inserted = 0
    for _, row in yearly_stats.iterrows():
        cursor.execute(
            insert_query,
            (
                row["weather_station_id"],
                int(row["year"]),
                row["max_temp"] if pd.notnull(row["max_temp"]) else None,
                row["min_temp"] if pd.notnull(row["min_temp"]) else None,
                row["precipitation"] if pd.notnull(row["precipitation"]) else None,
            ),
        )
        records_inserted += cursor.rowcount

    connection.commit()
    cursor.close()

    log_message(
        f"Yearly statistics calculated and stored. Records inserted: {records_inserted}"
    )


# Run the analysis
if __name__ == "__main__":
    connection = get_db_connection()
    calculate_yearly_statistics(connection)
    connection.close()
