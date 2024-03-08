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
from pinecone import Pinecone
from langfuse.callback import CallbackHandler
import google.generativeai as genai
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
pc = Pinecone(api_key=os.environ.get('CUSTOM_VAR'))

## Init - Firebase
if not firebase_admin._apps:
    print("Firebase app not initialized")
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


firebase = pyrebase.initialize_app(firebaseConfig)
security = HTTPBearer()


async def get_current_user(token: str = Depends(security)):                  
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate your Bearer credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    return {"message": "Auth Success | Welcome, user!"}

@app.get("/")
async def root():
    return {"message":"Server OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



