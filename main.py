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
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, sec.username)
    correct_password = secrets.compare_digest(credentials.password, sec.password)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return credentials.username

#Defining the API endpoint
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
            data.PaymentMethod = 4
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
            data.PaymentMethod,  # Assume the model expects encoded categories for PaymentMethod
            data.MonthlyCharges,
            data.TotalCharges
        ]]
        
        # Make prediction
        prediction = model.predict(data)
        
        # Return prediction result
        return {"prediction": int(prediction[0])}
    
    except Exception as e:
        logging.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during prediction")
    
    
    

