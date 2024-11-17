import os
import random
import pandas as pd
import mysql.connector
from flask import Flask, request, jsonify
from faker import Faker
from datetime import datetime
from threading import Thread

app = Flask(__name__)
fake = Faker()

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ronit",
    database="olp"
)

# Ensure table exists
def create_table_if_not_exists():
    """
    Ensures that the olympics_data table exists in the database.
    If not, it creates the table.
    """
    cursor = db.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS olympics_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Year INT,
        Type VARCHAR(10),
        Country VARCHAR(50),
        Athlete VARCHAR(100),
        Sport VARCHAR(50),
        Medal VARCHAR(10),
        Age INT
    );
    """
    cursor.execute(create_table_query)
    db.commit()
    cursor.close()

create_table_if_not_exists()

# List of countries and sports
COUNTRIES = [
    "USA", "China", "Russia", "Germany", "UK", "France", "Italy", "Australia",
    "Canada", "Japan", "India", "South Korea", "Brazil", "South Africa"
]

SUMMER_SPORTS = [
    "Athletics", "Swimming", "Gymnastics", "Cycling", "Basketball", "Tennis",
    "Rowing", "Weightlifting", "Boxing", "Soccer"
]

WINTER_SPORTS = [
    "Skiing", "Ice Hockey", "Figure Skating", "Snowboarding",
    "Curling", "Bobsleigh", "Speed Skating", "Biathlon"
]

MEDALS = ["Gold", "Silver", "Bronze", None]

OUTPUT_DIR = "output"

# List of actual Olympics years (summer and winter events)
OLYMPICS_YEARS = [
    1896, 1900, 1904, 1908, 1912, 1920, 1924, 1928, 1932, 1936, 1948, 1952, 1956, 1960,
    1964, 1968, 1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020
]

# Function to generate random Olympics data
def generate_olympics_data(year, olympics_type, num_entries=100):
    sports = SUMMER_SPORTS if olympics_type == "Summer" else WINTER_SPORTS
    data = []
    for _ in range(num_entries):
        athlete = fake.name()
        country = random.choice(COUNTRIES)
        sport = random.choice(sports)
        medal = random.choice(MEDALS)
        age = random.randint(18, 40)  # Logical age range for athletes
        data.append({
            "Year": year,
            "Type": olympics_type,
            "Country": country,
            "Athlete": athlete,
            "Sport": sport,
            "Medal": medal,
            "Age": age
        })
    return data

# Function to save data to MySQL
def save_to_mysql(data):
    cursor = db.cursor()
    query = """
    INSERT INTO olympics_data (Year, Type, Country, Athlete, Sport, Medal, Age)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = [(entry["Year"], entry["Type"], entry["Country"], entry["Athlete"], entry["Sport"], entry["Medal"], entry["Age"]) for entry in data]
    cursor.executemany(query, values)
    db.commit()
    cursor.close()

# Function to save or append data to CSV
def save_to_csv(data, year, olympics_type):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"{olympics_type}_{year}.csv")
    df = pd.DataFrame(data)
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)

# Continuous data generation
def continuous_data_generation():
    """
    Continuously generates and saves data for current year and type.
    """
    try:
        while True:
            year = random.choice(OLYMPICS_YEARS)  # Randomly pick a real Olympics year
            olympics_type = random.choice(["Summer", "Winter"])  # Randomly pick Summer or Winter
            data = generate_olympics_data(year, olympics_type, random.randint(50, 150))  # Randomize number of entries
            save_to_csv(data, year, olympics_type)
            save_to_mysql(data)
            print(f"Generated and saved data for {olympics_type} Olympics {year}")
    except Exception as e:
        print(f"Error in continuous data generation: {e}")

# Flask route to generate data manually
@app.route('/generate_data', methods=['GET'])
def generate_data():
    try:
        year = int(request.args.get('year', datetime.now().year))
        olympics_type = request.args.get('type', 'Summer').capitalize()
        num_entries = int(request.args.get('entries', 100))

        # Validate year
        if year not in OLYMPICS_YEARS:
            return jsonify({"error": "Year must be a valid Olympics year"}), 400

        # Generate data
        data = generate_olympics_data(year, olympics_type, num_entries)

        # Save data to CSV and MySQL
        save_to_csv(data, year, olympics_type)
        save_to_mysql(data)

        return jsonify({
            "message": f"Data generated for {olympics_type} Olympics {year}",
            "data": data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask route to fetch all data from MySQL
@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    """
    Fetch all data from the olympics_data table.
    Returns each row as a JSON object in a list.
    """
    try:
        query = "SELECT * FROM olympics_data"  # Fetch all rows
        cursor = db.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()  # Retrieve all rows
        cursor.close()

        return jsonify(results), 200  # Send data as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the background thread and Flask app
if __name__ == '__main__':
    # Start continuous data generation in the background
    background_thread = Thread(target=continuous_data_generation, daemon=True)
    background_thread.start()

    # Run the Flask app
    app.run(debug=True)
