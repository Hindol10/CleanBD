from flask import Flask, render_template, request, send_from_directory
import sqlite3
import os
import random

def fake_ai_predict(filename):

    options = [
        "Plastic Waste",
        "Garbage",
        "Blocked Drain",
        "Water Pollution",
        "Open Burning"
    ]

    return random.choice(options)
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Create Database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image TEXT,
    pollution_type TEXT,
    description TEXT,
    lat REAL,
    lng REAL
)
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/submit", methods=["POST"])
def submit():
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    image = request.files["image"]
    description = request.form["description"]

    filename = image.filename

    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    # 🤖 AI prediction
    ai_result = fake_ai_predict(filename)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
INSERT INTO reports (image, pollution_type, description, lat, lng)
VALUES (?, ?, ?, ?, ?)
""", (filename, ai_result, description, lat, lng))

    conn.commit()
    conn.close()

    return f"""
    <h1>🤖 AI Detected: {ai_result}</h1>
    <a href='/dashboard'>Go to Dashboard</a>
    """


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports")
    reports = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        reports=reports
    )



@app.route("/map")
def map_page():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports")
    reports = cursor.fetchall()

    conn.close()

    return render_template("map.html", reports=reports)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)