from flask import Flask, render_template, request
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType
from tools.frontend_helper import get_model, initialize_db_client
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import os

app = Flask(__name__)
_ = initialize_db_client()
model = get_model(model_name="sentence-transformers/all-MiniLM-L6-v2", max_seq_length=384)

load_dotenv()
api_key = os.getenv("API_KEY", None)
ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
project_id = os.getenv("PROJECT_ID", None)
environment = os.getenv("ENVIRONMENT", "local")

if api_key is None or ibm_cloud_url is None or project_id is None:
    print(
        "Ensure you copied the .env file that you created earlier into the same directory as this notebook")
else:
    creds = {
        "url": ibm_cloud_url,
        "apikey": api_key
    }

@app.route('/')
def index():
    # This handles the GET request for the index route
    return render_template('index.html')

@app.route('/milvusquery', methods=['POST'])
def milvusquery():
    print("hello")
    data = request.json  # or request.form for form data
    # print(type(data))
    print(data)
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


    results = {"results": concatenated_docs}
    return results


@app.route('/model_response', methods=['POST'])
def model_response():
    data = request.json  # or request.form for form data
    print(type(data))
    translated_question_english = data["query"]
    documents = data["documents"]

    model_params = {
        GenParams.DECODING_METHOD: 'greedy',
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.MAX_NEW_TOKENS: 300,
        # GenParams.RANDOM_SEED: 42,
        # GenParams.TEMPERATURE: 0.7,
        GenParams.REPETITION_PENALTY: 1,
    }
    model_llm = Model("meta-llama/llama-2-13b-chat", params=model_params, credentials=creds, project_id=project_id)

    knowledge_based_template = (
        open("assets/llama-2-prompt-template.txt",
            encoding="utf8").read().format(
        )
    )

    custom_prompt = PromptTemplate(template=knowledge_based_template,
                                input_variables=["context", "question"])

    formated_prompt = custom_prompt.format(question=translated_question_english,
                                            context=documents)
    response = model_llm.generate_text(formated_prompt)
    results = {"results": response}
    return results


# @app.route('/translate', methods=['POST'])
# def model_response():
#     data = request.json  # or request.form for form data
#     print(type(data))
#     translated_question_english = data["query"]
#     documents = data["documents"]
#     print("translated query", translated_question_english)
#     query_encode = [list(i) for i in model.encode([translated_question_english])]
#     # print(utility.list_collections())
#     collection = Collection('promotion_watsonxassitant_demo')
#     collection.load()
#     documents = collection.search(data=query_encode, anns_field="embeddings", param={"metric":"IP","offset":0},
#                     output_fields=["new_translated_docs", "page_content", "sources", "pagesno"], limit=4)
#     print("no. of retrieved docs", len(documents[0]))

#     concatenated_docs = ""
#     i = 1

#     for doc in documents[0]:
#         concatenated_docs += f'Document {i}\n'
#         concatenated_docs += f'Text:\n{doc.new_translated_docs}\n\n'
#         concatenated_docs += f'Sources: {doc.sources}\n'
#         concatenated_docs += f'Page Number: {doc.pagesno}\n\n'
#         i += 1


#     results = {"results": f"Received data modified: {concatenated_docs}"}
#     return results

if __name__ == '__main__':
    app.run(debug=True)


