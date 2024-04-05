import os
from flask import Flask, render_template, request

app = Flask(__name__)
@app.route('/question_guideline', methods=['POST'])
def question_guide_line():
    data = request.json
    question_to_be_guide = data["wide_question"]
    results = {"results": ["List all existing data", "Give me the number of sales", "Give me the December most sold out item", question_to_be_guide]}
    return results

@app.route('/question_to_sql', methods=['POST'])
def question_to_sql():
    data = request.json
    question_to_sql = data["scoped_question"]

    results = {"results": "SELECT SUM(REVENUE) FROM TRANSACTION WHERE REVENUE_TYPE='JEWERY';"}
    return results


if __name__ == '__main__':
    app.run(debug=True, port=8001, host="0.0.0.0")
