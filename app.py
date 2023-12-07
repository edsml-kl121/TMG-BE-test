from flask import Flask, render_template, request
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from tools.frontend_helper import get_model, initialize_db_client

app = Flask(__name__)
_ = initialize_db_client()
model = get_model(model_name="sentence-transformers/all-MiniLM-L6-v2", max_seq_length=384)

@app.route('/')
def index():
    # This handles the GET request for the index route
    return render_template('index.html')

@app.route('/data', methods=['POST'])
def data():
    data = request.json  # or request.form for form data
    print(type(data))
    translated_question_english = data["query"]
    print("translated query", translated_question_english)
    query_encode = [list(i) for i in model.encode([translated_question_english])]
    # print(utility.list_collections())
    collection = Collection('promotion_watsonxassitant_demo')
    collection.load()
    documents = collection.search(data=query_encode, anns_field="embeddings", param={"metric":"IP","offset":0},
                    output_fields=["new_translated_docs", "page_content", "sources", "pagesno"], limit=4)
    print("no. of retrieved docs", len(documents[0]))

    concatenated_docs = ""
    i = 1

    for doc in documents[0]:
        concatenated_docs += f'Document {i}\n'
        concatenated_docs += f'Text:\n{doc.new_translated_docs}\n\n'
        concatenated_docs += f'Sources: {doc.sources}\n'
        concatenated_docs += f'Page Number: {doc.pagesno}\n\n'
        i += 1


    results = {"results": f"Received data modified: {concatenated_docs}"}
    return results

if __name__ == '__main__':
    app.run(debug=True)


