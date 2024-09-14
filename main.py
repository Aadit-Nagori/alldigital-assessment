from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import joblib
import logging
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

import secrets
import passwords as sec

#Initializing the API
app = FastAPI()

#Setting up the security
security = HTTPBasic()

#making sure the API is only accessible via HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

#loading the model
model = joblib.load("logistic_regression_model.pkl")

#setting up logging and logging the API usage
logging.basicConfig(filename="api_usage.log",level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')


#Defining the input schema
'''
This class defines the input schema for the API endpoint.
The input schema is defined using Pydantic's BaseModel class.
The input schema includes the optimal fields found during the feature engineering process.
'''
class ModelInput(BaseModel):
    SeniorCitizen: bool
    Partner: bool
    Tenure: int
    OnlineSecurity: bool
    OnlineBackup: bool
    TechSupport: bool
    StreamingTV: bool
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

        
        
#Authentication function
'''
This function checks the username and password provided by the user against the correct username and password.
If the username and password are correct, the function returns the username.
If the username and password are incorrect, the function raises an HTTPException with status code 401 (Unauthorized).
'''
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, sec.username)
    correct_password = secrets.compare_digest(credentials.password, sec.password)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return credentials.username

#Defining the API endpoint
'''
This endpoint is used to make predictions using the trained model.
The endpoint takes the input data as a JSON object and the username and password for authentication.
The endpoint first checks the authentication credentials using the get_current_username function.
If the authentication is successful, the endpoint processes the input data, makes a prediction using the model, and returns the prediction.
If there is an error during the prediction process, the endpoint logs the error and returns an HTTP 500 error.
If the payment method provided in the input data is invalid, the endpoint raises an HTTP 400 error.
'''
@app.post("/predict")
def predict(data: ModelInput, username: str = Depends(get_current_username)):
    
    try:
        # Log API usage
        logging.info(f"User {username} accessed the /predict endpoint with data {data}")
        
        #converting payment method to encoded categories
        if data.PaymentMethod == "Bank transfer":
            data.PaymentMethod = 0
        elif data.PaymentMethod == "Credit card":
            data.PaymentMethod = 1
        elif data.PaymentMethod == "Electronic check":
            data.PaymentMethod = 2
        elif data.PaymentMethod == "Mailed check":
            data.PaymentMethod = 3
        else:
            raise HTTPException(status_code=400, detail="Invalid PaymentMethod")
        
        # Convert the input into the format expected by the model
        data = [[
                int(data.SeniorCitizen),
                int(data.Partner),
                data.Tenure,
                int(data.OnlineSecurity),
                int(data.OnlineBackup),
                int(data.TechSupport),
                int(data.StreamingTV),
                data.PaymentMethod,  
                data.MonthlyCharges,
                data.TotalCharges
            ]]
        
        # Make prediction
        prediction = model.predict(data)
        
        # Return prediction result
        return {"prediction": int(prediction[0])}
    
    # Re-raise HTTPExceptions so they are returned as-is
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during prediction")
    
    
    

