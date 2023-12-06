from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    # This handles the GET request for the index route
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    # This handles the POST request for the /data route
    return "I am connected to the Flask app"

if __name__ == '__main__':
    app.run(debug=True)
