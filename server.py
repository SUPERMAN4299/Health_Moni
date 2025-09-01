from flask import Flask, render_template
import json

app = Flask(__name__)

# Load JSON file once when server starts
with open("security.json", "r") as f:
    vars = json.load(f)

@app.route('/s')
def get_string():
    return f"{vars['stored_user_enc']}{vars['stored_pass_enc']}{vars['stored_mac_enc']}"

@app.route("/query")
def query():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
