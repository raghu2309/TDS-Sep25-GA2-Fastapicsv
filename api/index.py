# api/index.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Dict, Any, Optional

# --- 1. Load Data ---
# Load the CSV data into a pandas DataFrame. 
# This must be adjusted to find the CSV file relative to the execution context.
# Assuming 'q-fastapi.csv' is in the project root directory, we use the relative path.
try:
    # Use ../ to step up one directory if the script is run from the 'api' folder
    # or ensure the path is correct for your environment. If running from the root, use just 'q-fastapi.csv'.
    # For a Vercel deployment, the file should be in the root and this path should work.
    df = pd.read_csv('q-fastapi.csv') 
    
    # Convert DataFrame to a list of dictionaries (records) for JSON serialization
    ALL_STUDENTS_DATA = df.to_dict(orient='records')
except FileNotFoundError:
    # Handle error in a way that the server can still start
    print("FATAL ERROR: 'q-fastapi.csv' not found. Check file path in Vercel or local environment.")
    ALL_STUDENTS_DATA = []

# --- 2. FastAPI Application Setup ---
app = FastAPI()

# --- 3. CORS Middleware ---
# Enable CORS for all origins, allowing GET requests from any frontend/client.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- 4. API Endpoint ---
@app.get("/api", response_model=List[Dict[str, Any]])
def get_students(
    class_filter: Optional[List[str]] = Query(None, alias="class")
) -> List[Dict[str, Any]]:
    """
    Returns student data, optionally filtered by class.
    """

    # If no 'class' filter is provided (e.g., /api)
    if not class_filter:
        return ALL_STUDENTS_DATA
    
    # If a filter is provided (e.g., /api?class=1A or /api?class=1A&class=1B)
    
    # Filter the original DataFrame based on the 'class' column
    # Create a DataFrame from the in-memory list to re-filter and maintain order
    temp_df = pd.DataFrame(ALL_STUDENTS_DATA)
    
    # Filter the DataFrame: keep rows where the 'class' value is in the user's filter list
    filtered_df = temp_df[temp_df['class'].isin(class_filter)]
    
    # Convert the filtered DataFrame back to a list of dictionaries and return
    return filtered_df.to_dict(orient='records')

# --- 5. Root Endpoint (Keeping the Vercel-friendly root) ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Data API. Access /api to retrieve data."}
