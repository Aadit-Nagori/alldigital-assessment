from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
import passwords as sec

client = TestClient(app)

# Test the prediction endpoint
def test_predict_valid_input():
    response = client.post(
        "/predict",
        json={
            "SeniorCitizen": True,
            "Partner": False,
            "Tenure": 24,
            "OnlineSecurity": True,
            "OnlineBackup": False,
            "TechSupport": False,
            "StreamingTV": True,
            "PaymentMethod": "Credit card",
            "MonthlyCharges": 75.50,
            "TotalCharges": 1800.75
        },
        auth=(sec.username, sec.password) 
    )
    
    # Assert that the status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response contains a prediction
    assert "prediction" in response.json()

# Test invalid credentials for authentication
def test_predict_invalid_auth():
    response = client.post(
        "/predict",
        json={
            "SeniorCitizen": True,
            "Partner": False,
            "Tenure": 24,
            "OnlineSecurity": True,
            "OnlineBackup": False,
            "TechSupport": False,
            "StreamingTV": True,
            "PaymentMethod": "Credit card",
            "MonthlyCharges": 75.50,
            "TotalCharges": 1800.75
        },
        #Invalid credentials
        auth=("wronguser", "wrongpassword")  
    )
    
    # Assert that the status code is 401 (Unauthorized)
    assert response.status_code == 401
    # Assert the response message for invalid authentication
    assert response.json()["detail"] == "Incorrect username or password"

# Test validation for an invalid payment method
def test_predict_invalid_payment_method():
    response = client.post(
        "/predict",
        json={
            "SeniorCitizen": True,
            "Partner": False,
            "Tenure": 24,
            "OnlineSecurity": True,
            "OnlineBackup": False,
            "TechSupport": False,
            "StreamingTV": True,
            "PaymentMethod": "Invalid method",  # Invalid payment method
            "MonthlyCharges": 75.50,
            "TotalCharges": 1800.75
        },
        auth=(sec.username, sec.password) 
    )
    
    # Assert that the status code is 400 (Bad Request)
    assert response.status_code == 400
    # Assert that the error message is correct
    assert response.json()["detail"] == "Invalid PaymentMethod"
    


# Test missing fields (input validation)
def test_predict_missing_field():
    response = client.post(
        "/predict",
        json={
            "SeniorCitizen": True,
            "Partner": False,
            "Tenure": 24,
            "OnlineSecurity": True,
            "TechSupport": False,
            "StreamingTV": True,
            "PaymentMethod": "Credit card",
            "MonthlyCharges": 75.50
            # Missing "TotalCharges" field
        },
        auth=(sec.username, sec.password) 
    )
    
    # Assert that the status code is 422 (Unprocessable Entity)
    assert response.status_code == 422

