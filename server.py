from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)


with open("security.json", "r") as f:
    vars = json.load(f)

# json variable 
stored_data = {}

# Uploading
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
        stored_data = json.load(file)  # save in memory
    except Exception as e:
        return jsonify({"error": f"Invalid JSON - {e}"}), 400

    print(" Stored JSON:", stored_data)
    return jsonify({"stored": stored_data}), 200


@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    global stored_data
    if not stored_data:
        return jsonify({"error": "No JSON uploaded yet"}), 400
    
    if key in stored_data:
        return jsonify({key: stored_data[key]}), 200
    else:
        return jsonify({"error": f"Key '{key}' not found"}), 404


@app.route('/s1')
def get_string():
    return f"{vars['stored_user_enc']}{vars['stored_pass_enc']}{vars['stored_ip_enc']}"


@app.route("/query")
def query():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
