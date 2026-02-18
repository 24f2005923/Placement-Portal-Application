from flask import Flask
import sqlite3

app = Flask(__name__)
app.secret_key = "placement_secret_key"

@app.route("/")
def home():
    return "Placement Portal Running Successfully!"

if __name__ == "__main__":
    app.run(debug=True)
