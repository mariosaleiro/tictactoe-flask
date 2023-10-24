from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Flask from Turbine Kreuzberg"

@app.route("/about")
def about():
    return "Hello About"