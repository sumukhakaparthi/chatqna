from fastapi import FastAPI
import uvicorn
import json
from fastapi import HTTPException
from pydantic import SecretStr, EmailStr
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Firebase Bearer Token Generator"
)

#importing variables
FIREBASE_WEB_API_KEY = os.environ.get("fbapiKey")
rest_api_url = os.environ.get("fb_auth_rest_api_url")
rest_api_url_bearer = os.environ.get("fb_auth_rest_api_url_bearer")



@app.post("/generate_token")
async def sign_in_with_email_and_password(email:EmailStr , 
                                          password:SecretStr):
    
    '''
    This function signsin a user on Firebase with email and password and returns Bearer token with other info.

    Args:
        email (EmailStr): The email of the user.
        password (SecretStr): The password of the user.

    Returns:
        dict: A dictionary containing the user's information.
    '''
    
    try:
        r = requests.post(rest_api_url,
                        params={"key": FIREBASE_WEB_API_KEY},
                        data=json.dumps({
                                    "email": email,
                                    "password": password.get_secret_value(),
                                    "returnSecureToken": True
                                }))
        if r.status_code == 200:
            try:
                b = requests.post(rest_api_url_bearer,
                        params={"key": FIREBASE_WEB_API_KEY},
                        data=json.dumps({
                                    'grant_type': 'refresh_token',  
                                    'refresh_token': r.json()['refreshToken']
                                    }))
                if b.status_code == 200:
                    json_final = b.json()
                else:
                    raise HTTPException(status_code=b.status_code, detail=b.json())
            except Exception as e:
                raise e
        else:
            raise HTTPException(status_code=r.status_code, detail=r.json())
    except Exception as e:
        raise e


    return json_final

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)