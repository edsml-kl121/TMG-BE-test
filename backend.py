from dotenv import load_dotenv
import os
# from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import (HuggingFaceHubEmbeddings,
                                  HuggingFaceInstructEmbeddings,
                                  SentenceTransformerEmbeddings)
from langchain.vectorstores import FAISS, Chroma, Milvus
from pymilvus import connections
import requests

# importing Custom package
# from tools.translation import translate_large_text, translate_to_thai
from tools.backend_helper import read_pdfs, listing_docs, manage_collection
from tools.frontend_helper import get_model
connections.connect("default", host="158.175.177.136", port="8080", secure=True, server_pem_path="./cert.pem", server_name="localhost",user="root",password="4XYg2XK6sMU4UuBEjHq4EhYE8mSFO3Qq")

print("Chunking docs")
base_folder_path = 'assets/pdfs'
translated_docs = read_pdfs(listing_docs(base_folder_path))
# embeddings = HuggingFaceHubEmbeddings(repo_id="sentence-transformers/all-MiniLM-L6-v2")

# print(translated_docs)
print("initializing milvus")
# Usage in main application
if __name__ == "__main__":
    collection_name = "promotion_watsonxassitant_demo"
    collection = manage_collection(collection_name)
    print("initialized new collection")

new_translated_docs, page_contents, pagesno, sources = read_pdfs(listing_docs(base_folder_path))

print(page_contents)
print(sources)

print("ingesting into Milvus - start")
model = get_model(model_name="sentence-transformers/all-MiniLM-L6-v2", max_seq_length=384)
embeds = [list(embed) for embed in model.encode(new_translated_docs)]
collection.insert([new_translated_docs, page_contents, embeds, pagesno, sources])
collection.create_index(field_name="embeddings",\
                        index_params={"metric_type":"IP","index_type":"IVF_FLAT","params":{"nlist":16384}})

print("ingesting into Milvus - completed")

# utility.drop_collection(collection_name)
# print("dropped collection")
