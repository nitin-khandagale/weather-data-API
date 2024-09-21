import logging
import os
from datetime import datetime

import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("weather_ingestion.log"),  # Write to file
        logging.StreamHandler(),  # Print to console
    ],
)


# Database connection setup using environment variables
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


# Function to ingest a single weather data file
def ingest_weather_data(file_path, connection):
    log_message(f"Starting ingestion for file: {file_path}")

    # Read the file into a DataFrame
    df = pd.read_csv(
        file_path,
        delimiter="\t",
        names=["date", "max_temp", "min_temp", "precipitation"],
    )

    # Clean the data (handle missing values)
    df.replace(-9999, None, inplace=True)

    # Extract weather station id from the filename
    weather_station_id = os.path.basename(file_path).split(".")[0]

    cursor = connection.cursor()

    # Prepare insert statement with duplicate checking
    insert_query = """
        INSERT INTO weather_data (weather_station_id, record_date, max_temperature, min_temperature, precipitation)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (weather_station_id, record_date) DO NOTHING;
    """

    records_ingested = 0

    # Loop through the DataFrame and insert each record
    for _, row in df.iterrows():
        cursor.execute(
            insert_query,
            (
                weather_station_id,
                datetime.strptime(str(row["date"]), "%Y%m%d").date(),
                row["max_temp"] / 10.0 if row["max_temp"] is not None else None,
                row["min_temp"] / 10.0 if row["min_temp"] is not None else None,
                row["precipitation"] / 10.0
                if row["precipitation"] is not None
                else None,
            ),
        )
        records_ingested += cursor.rowcount

    # Commit the transaction
    connection.commit()
    cursor.close()

    log_message(
        f"Finished ingestion for file: {file_path}. Records ingested: {records_ingested}"
    )
    return records_ingested


# Main function to ingest all weather data files
def ingest_all_weather_data(data_dir):
    start_time = datetime.now()
    log_message(f"Starting ingestion of weather data from directory: {data_dir}")

    connection = get_db_connection()

    total_records = 0

    # Loop over all files in the directory
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(data_dir, file_name)
            total_records += ingest_weather_data(file_path, connection)

    connection.close()

    end_time = datetime.now()
    log_message(f"Finished ingestion. Total records ingested: {total_records}")
    log_message(f"Time taken: {end_time - start_time}")


# Run the ingestion
if __name__ == "__main__":
    data_directory = "wx_data"
    ingest_all_weather_data(data_directory)
