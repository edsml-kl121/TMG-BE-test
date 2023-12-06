from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    # This handles the GET request for the index route
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    data = request.json  # or request.form for form data
    return f"Received data: {data}"

if __name__ == '__main__':
    app.run(debug=True)
