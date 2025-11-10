from flask import Flask, render_template, request, jsonify
import json
import csv
import os
from datetime import datetime

app = Flask(__name__)

# ---------- Load Security Variables ----------
with open("security.json", "r") as f:
    vars = json.load(f)

# ---------- JSON Storage ----------
stored_data = {}

# ---------- CSV Setup for Queries ----------
if not os.path.exists("queries.csv"):
    with open("queries.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Full Name", "Email", "Serial Number", "Issue Type", "Message"])

# ---------- Routes ----------

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Upload Patient JSON Data
@app.route('/patient-data1', methods=['GET', 'POST'])
def patient_d():
    global stored_data

    if request.method == "GET":
        if not stored_data:
            return jsonify({"message": "No JSON uploaded yet"}), 200
        return jsonify({"stored_data": stored_data}), 200

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    try:
        stored_data = json.load(file)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON - {e}"}), 400

    print("Stored JSON:", stored_data)
    return jsonify({"stored": stored_data}), 200


# Get value from JSON by key
@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    global stored_data
    if not stored_data:
        return jsonify({"error": "No JSON uploaded yet"}), 400

    if key in stored_data:
        return jsonify({key: stored_data[key]}), 200
    else:
        return jsonify({"error": f"Key '{key}' not found"}), 404


# Return security string
@app.route('/s1')
def get_string():
    return f"{vars['stored_user_enc']}{vars['stored_pass_enc']}{vars['stored_mac_enc']}"


# Query Page
@app.route("/query")
def query_page():
    return render_template("index1.html")


# Contact Page
@app.route("/contact")
def contact_page():
    return render_template("contact.html")


# Submit Query (from Contact Form)
@app.route("/submit_query", methods=["POST"])
def submit_query():
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    serial_number = request.form.get("serial_number", "")
    issue_type = request.form.get("issue_type")
    message = request.form.get("message")

    # Save to CSV
    with open("queries.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), full_name, email, serial_number, issue_type, message])

    return '''
    <script>
        alert(" Your query has been submitted successfully!");
        window.location.href = "/contact";
    </script>
    '''


# Optional route for developer to view queries
@app.route("/view_queries")
def view_queries():
    with open("queries.csv", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        data = list(reader)
    html = "<h2>Submitted Queries</h2><table border=1 cellpadding=6>"
    for row in data:
        html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
    html += "</table>"
    return html


# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
