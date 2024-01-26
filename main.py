from datetime import datetime

from fastapi.responses import StreamingResponse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote
import pymongo
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


app = FastAPI(
    title="Polish Reverse Calculator",
    contact={
        "email":"raphaelabizmil@gmail.com"
    }
)


origins = [
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_npi(expression):
    stack = []

    def operation(op, operand1, operand2):
        if op == '+':
            return operand1 + operand2
        elif op == '-':
            return operand1 - operand2
        elif op == '*':
            return operand1 * operand2
        elif op == '/':
            return operand1 / operand2
    
    tokens = unquote(expression).split()

    for token in tokens:
        if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
            stack.append(int(token))
        else:
            operand2 = stack.pop()
            operand1 = stack.pop()
            resultat = operation(token, operand1, operand2)
            stack.append(resultat)

    return save_to_mongodb(unquote(expression),stack[0])

def save_to_mongodb(expression,result):
    try:
        mongo_uri = os.getenv('MONGO_URI')
        client = pymongo.MongoClient(mongo_uri)
        db = client['ayomi']
        operation_collection = db['operation']
        dict ={
            "date":datetime.now(),
            "expression":expression,
            "result":result
        }
        operation_collection.insert_one(dict)
        return result
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def get_data_to_csv():
    try:
        mongo_uri = os.getenv('MONGO_URI')
        client = pymongo.MongoClient(mongo_uri)
        db = client['ayomi']
        operation_collection = db['operation']
        df = pd.DataFrame(list(operation_collection.find()))
        return df.to_csv()
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.post("/evaluate")
def evaluate_expression(expression:str):
    try:
        result = calculate_npi(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/download")
def download_csv():
    filename = "extract_"+str(datetime.now())
    return StreamingResponse(
    iter(get_data_to_csv()),
    media_type='text/csv',
    headers={"Content-Disposition":
             f"attachment;filename={filename}.csv"})
