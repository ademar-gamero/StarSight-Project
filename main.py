from flask import Flask
app = Flask(__name__)

@app.route("/")
def main_menu():
    return "<h1> StarSight Application </h1>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
