import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

load_dotenv()

# Initialize Flask app and database connection
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Swagger setup
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"  # This will host the OpenAPI spec
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Weather API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Weather Data model for /api/weather
class WeatherData(db.Model):
    __tablename__ = "weather_data"
    weather_station_id = db.Column(db.String, primary_key=True)
    record_date = db.Column(db.Date, primary_key=True)
    max_temperature = db.Column(db.Float)
    min_temperature = db.Column(db.Float)
    precipitation = db.Column(db.Float)


# Yearly Statistics model for /api/weather/stats
class WeatherYearlyStatistics(db.Model):
    __tablename__ = "weather_yearly_statistics"
    weather_station_id = db.Column(db.String, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    avg_max_temperature = db.Column(db.Float)
    avg_min_temperature = db.Column(db.Float)
    total_precipitation = db.Column(db.Float)


# Helper function for pagination
def paginate(query, page, per_page):
    return query.paginate(page=page, per_page=per_page, error_out=False)


# /api/weather endpoint
@app.route("/api/weather", methods=["GET"])
def get_weather():
    station_id = request.args.get("station_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = WeatherData.query

    if station_id:
        query = query.filter_by(weather_station_id=station_id)

    if start_date:
        query = query.filter(WeatherData.record_date >= start_date)

    if end_date:
        query = query.filter(WeatherData.record_date <= end_date)

    weather_data = paginate(query, page, per_page)

    result = [
        {
            "station_id": data.weather_station_id,
            "date": data.record_date,
            "max_temp": data.max_temperature,
            "min_temp": data.min_temperature,
            "precipitation": data.precipitation,
        }
        for data in weather_data.items
    ]

    return jsonify(
        {
            "weather_data": result,
            "total": weather_data.total,
            "pages": weather_data.pages,
            "current_page": weather_data.page,
        }
    )


# /api/weather/stats endpoint
@app.route("/api/weather/stats", methods=["GET"])
def get_weather_stats():
    station_id = request.args.get("station_id")
    year = request.args.get("year", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = WeatherYearlyStatistics.query

    if station_id:
        query = query.filter_by(weather_station_id=station_id)

    if year:
        query = query.filter_by(year=year)

    weather_stats = paginate(query, page, per_page)

    result = [
        {
            "station_id": data.weather_station_id,
            "year": data.year,
            "avg_max_temp": data.avg_max_temperature,
            "avg_min_temp": data.avg_min_temperature,
            "total_precipitation": data.total_precipitation,
        }
        for data in weather_stats.items
    ]

    return jsonify(
        {
            "weather_stats": result,
            "total": weather_stats.total,
            "pages": weather_stats.pages,
            "current_page": weather_stats.page,
        }
    )


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
