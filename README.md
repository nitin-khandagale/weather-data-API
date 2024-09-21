# Weather Data API

This project provides a REST API for ingesting, storing, and analyzing weather data. The API exposes weather records and statistical data for various weather stations. The API is built using Flask, SQLAlchemy for database interactions, and Swagger for automatic API documentation.

## Features

- **Ingestion of Weather Data**: Parses raw weather data from text files and stores it in a PostgreSQL database.
- **REST API Endpoints**: Provides endpoints to fetch weather data and yearly weather statistics.
- **Filtering and Pagination**: Both weather data and stats endpoints support filtering by station ID, date range, and year, with results paginated.
- **Swagger Documentation**: Automatically generated API documentation with interactive endpoints.
- **Logging and Duplicate Prevention**: Uses Python logging and avoids inserting duplicate weather records during ingestion.

---

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Flask
- SQLAlchemy
- Swagger/OpenAPI for documentation
- dotenv for environment variables

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/weather-data-api.git
cd weather-data-api
```

### 2. Set Up the Virtual Environment

Create a virtual environment and activate it:

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

Make sure you have PostgreSQL installed. Create a new database:

```bash
# Access PostgreSQL prompt
psql -U postgres

# Create a new database
CREATE DATABASE weather_db;
```

Create a `.env` file in the root directory with your PostgreSQL credentials:

```bash
DB_HOST=localhost
DB_NAME=weather_db
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
```

### 5. Set Up the Database Tables

Run the migrations or manually create the database tables by running the following:

```bash
flask db upgrade
```

Alternatively, you can create the tables directly in the PostgreSQL database using the SQLAlchemy models provided in the code.

### 6. Ingest Weather Data

To ingest weather data from raw files, you can use the provided script.

```bash
python ingest_weather_data.py
```

This script will:

- Read the weather data files from the `wx_data/` directory.
- Check for duplicates before inserting records.
- Log start and end times along with the number of records ingested.

---

## Running the Flask API

### 1. Start the Flask Server

Run the following command to start the Flask application:

```bash
python app.py
```

The Flask application will start on `http://localhost:5000`.

### 2. Access the Swagger Documentation

You can explore the API interactively via Swagger at:

```bash
http://localhost:5000/swagger
```

---

## API Endpoints

### `/api/weather` - Get Weather Data

Returns paginated weather data with optional filters for station ID and date range.

- **Method**: `GET`
- **Parameters**:
  - `station_id` (string) - Filter by weather station ID.
  - `start_date` (string) - Filter by start date (YYYY-MM-DD).
  - `end_date` (string) - Filter by end date (YYYY-MM-DD).
  - `page` (integer) - Page number for pagination.
  - `per_page` (integer) - Number of results per page.
- **Example Request**:

  ```
  GET /api/weather?station_id=ABC&start_date=2010-01-01&end_date=2010-12-31&page=1&per_page=10
  ```

- **Example Response**:

  ```json
  {
    "weather_data": [
      {
        "station_id": "ABC",
        "date": "2010-01-01",
        "max_temp": 23.4,
        "min_temp": -5.0,
        "precipitation": 10.2
      },
      {
        "station_id": "ABC",
        "date": "2010-01-02",
        "max_temp": 22.1,
        "min_temp": -4.5,
        "precipitation": 5.4
      }
    ],
    "total": 100,
    "pages": 10,
    "current_page": 1
  }
  ```

### `/api/weather/stats` - Get Weather Statistics

Returns yearly statistics (average temperatures, total precipitation) for each weather station.

- **Method**: `GET`
- **Parameters**:
  - `station_id` (string) - Filter by weather station ID.
  - `year` (integer) - Filter by year.
  - `page` (integer) - Page number for pagination.
  - `per_page` (integer) - Number of results per page.
- **Example Request**:

  ```
  GET /api/weather/stats?station_id=XYZ&year=2010&page=1&per_page=10
  ```

- **Example Response**:

  ```json
  {
    "weather_stats": [
      {
        "station_id": "XYZ",
        "year": 2010,
        "avg_max_temp": 22.4,
        "avg_min_temp": -2.3,
        "total_precipitation": 152.6
      }
    ],
    "total": 1,
    "pages": 1,
    "current_page": 1
  }
  ```

---

## Data Models

### Weather Data Model

This table stores the raw weather data ingested from the files.

```python
class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    weather_station_id = db.Column(db.String, primary_key=True)
    record_date = db.Column(db.Date, primary_key=True)
    max_temperature = db.Column(db.Float)
    min_temperature = db.Column(db.Float)
    precipitation = db.Column(db.Float)
```

### Weather Yearly Statistics Model

This table stores the calculated yearly statistics for each weather station.

```python
class WeatherYearlyStatistics(db.Model):
    __tablename__ = 'weather_yearly_statistics'
    weather_station_id = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    avg_max_temperature = db.Column(db.Float)
    avg_min_temperature = db.Column(db.Float)
    total_precipitation = db.Column(db.Float)
```

---

## Ingestion Script

The `ingest_weather_data.py` script handles ingestion of weather data from the raw files into the PostgreSQL database. It also avoids duplicates and logs the number of records ingested.

### Running the Script

```bash
python ingest_weather_data.py
```

You can configure the weather data file paths in the script or place the files in the `wx_data/` directory.

---

## Logging

The application uses Python's built-in logging module to track:

- Ingestion start and end times.
- The number of records ingested.
- Any errors encountered.

Logs are printed to the console and can easily be redirected to a file.

---

## Testing the API

You can test the API using any HTTP client like `curl`, `Postman`, or the interactive Swagger UI.

### Example `curl` Request

```bash
curl "http://localhost:5000/api/weather?station_id=ABC&start_date=2010-01-01&end_date=2010-12-31&page=1"
```

---

## License

This project is licensed under the MIT License.


Feel free to modify the project to fit your needs! If you encounter any issues or have questions, please don't hesitate to open an issue or reach out.

--- 