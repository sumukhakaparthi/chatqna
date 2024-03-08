#Imports
import os
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
from pinecone import Pinecone
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
import google.generativeai as genai
from code.utils import *
from dotenv import load_dotenv
load_dotenv()



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

@app.get("/confirm_login", tags=['Login'],
            description= "Run this endpoint to confirm your login status")
async def confirm_login(current_user=Depends(get_current_user)):
    return {"message": "Auth Success | Welcome, user!"}

@app.get("/")
async def root():
    return {"message":"Server OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



