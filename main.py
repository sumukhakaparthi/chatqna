#Imports
import os
import sys
import logging
from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
import uvicorn
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
import queue
import redis
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
import google.generativeai as genai
from code.utils import *
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(filename='rag.log', level=logging.DEBUG)

#importing variables
FIREBASE_WEB_API_KEY = os.environ.get("fbapiKey")
rest_api_url = os.environ.get("fb_auth_rest_api_url")
rest_api_url_bearer = os.environ.get("fb_auth_rest_api_url_bearer")

firebaseConfig = {
    'apiKey': os.getenv('fbapiKey'),
    'authDomain': os.getenv('fbauthDomain'),
    'projectId': os.getenv('fbprojectId'),
    'storageBucket': os.getenv('fbstorageBucket'),
    'messagingSenderId': os.getenv('fbmessagingSenderId'),
    'appId': os.getenv('fbappId'),
    'measurementId': os.getenv('fbmeasurementId'),
    'databaseURL':os.getenv('fbdatabaseURL')
    }

#Initialization

## Init - FastAPI
app = FastAPI(
    title="RAG Chat"
)

@app.get("/")
async def root():
    return {"message":"Server OK"}

## Init - PineCone
pc = Pinecone(
    api_key=os.environ.get('pinecone_secret')
    )

## Init - Redis
r = redis.Redis(
    host=os.getenv('Redis_host'), 
    port=os.getenv('Redis_port'),
    username=os.getenv('Redis_uname'), # use your Redis user. More info https://redis.io/docs/management/security/acl/
    password=os.getenv('Redis_api_key'), # use your Redis password
    #ssl=True,ssl_certfile="./redis_user.crt",ssl_keyfile="./redis_user_private.key",ssl_ca_certs="./redis_ca.pem",
)

## Init - Langfuse
langfuse = Langfuse(
  secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
  public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
  host=os.getenv('LANGFUSE_HOST')
)

## Init - Firebase
if not firebase_admin._apps:
    print("Firebase app not initialized")
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


firebase = pyrebase.initialize_app(firebaseConfig)

## Init - ChatGAI
llm = ChatGoogleGenerativeAI(model="gemini-pro",
                             google_api_key=os.getenv("maker_suit_api"))

@app.get("/confirm_login", tags=['Login'],
            description= "Run this endpoint to confirm your login status")
async def confirm_login(current_user=Depends(get_current_user)):
    logging.info(f"{current_user['email']} has logged in")
    return {"message": f"Auth Success | Welcome, {current_user['email']}!"}

@app.get("/get_bearer_token", tags=['Login'],
            description= "Run this endpoint to get bearer token")
async def get_bearer_token(current_user=Depends(bearer_token_output)):
    return current_user['access_token']

@app.post("/orchestration/get_answers_to_query", tags=['Orchestration'])
async def get_answers_to_query(query: str, current_user=Depends(bearer_token_auth)):
    #add observabilty and collect user usage data
    get_response = llm.invoke(query)
    return get_response

@app.post("/orchestration/query_vector_db", tags=['Orchestration'])
async def query_vector_db(current_user=Depends(bearer_token_auth)):
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



