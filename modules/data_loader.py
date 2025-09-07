import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@st.cache_data(ttl=3600)
def load_data():
    """
    Loads and preprocesses data from CSV files.
    This function is cached to improve performance.
    """
    # Get URLs from environment variables or Streamlit secrets
    try:
        data_url = os.getenv('DATA_CSV_URL') or st.secrets.get('DATA_CSV_URL')
        list_url = os.getenv('COMMO_LIST_CSV_URL') or st.secrets.get('COMMO_LIST_CSV_URL')
    except:
        data_url = os.getenv('DATA_CSV_URL')
        list_url = os.getenv('COMMO_LIST_CSV_URL')
    
    # Fallback to local files if URLs not available
    data_path = os.path.join("data", "Data.csv") if not data_url else data_url
    list_path = os.path.join("data", "Commo_list.csv") if not list_url else list_url

    try:
        df_data = pd.read_csv(data_path)
        df_list = pd.read_csv(list_path)

        # --- PREPROCESSING ---
        # 1. Clean column names by stripping whitespace
        df_data.columns = [col.strip() for col in df_data.columns]
        df_list.columns = [col.strip() for col in df_list.columns]

        # 2. KEY FIX: Clean the 'Commodities' column in BOTH dataframes immediately upon loading
        if 'Commodities' in df_data.columns:
            df_data['Commodities'] = df_data['Commodities'].astype(str).str.strip()
        if 'Commodities' in df_list.columns:
            df_list['Commodities'] = df_list['Commodities'].astype(str).str.strip()

        # 3. Clean 'Price' column
        if 'Price' in df_data.columns:
            df_data['Price'] = df_data['Price'].astype(str).str.replace(',', '').str.strip()
            df_data['Price'] = pd.to_numeric(df_data['Price'], errors='coerce')

        # 4. Convert 'Date' column to datetime objects
        if 'Date' in df_data.columns:
            df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')
        
        # 5. Drop rows where essential data is missing
        df_data.dropna(subset=['Date', 'Commodities', 'Price'], inplace=True)
        df_list.dropna(subset=['Commodities'], inplace=True)

        return df_data, df_list
    except Exception as e:
        st.error(f"Error loading data: {str(e)}. Check network connection or local file paths.")
        return None, None

@st.cache_data(ttl=3600)
def load_steel_data():
    """
    Loads steel production data from Google Drive.
    This function is cached to improve performance.
    """
    try:
        steel_url = os.getenv('STEEL_DATA_CSV_URL') or st.secrets.get('STEEL_DATA_CSV_URL')
    except:
        steel_url = os.getenv('STEEL_DATA_CSV_URL')
    
    if not steel_url:
        st.warning("Steel data URL not configured in environment variables.")
        return None
        
    try:
        df_steel = pd.read_csv(steel_url)
        
        # Clean column names by stripping whitespace
        df_steel.columns = [col.strip() for col in df_steel.columns]
        
        # Convert Date column to datetime if it exists
        if 'Date' in df_steel.columns:
            df_steel['Date'] = pd.to_datetime(df_steel['Date'], errors='coerce')
        
        # Drop rows where essential data is missing
        df_steel.dropna(subset=['en_OrganName'], inplace=True)
        
        return df_steel
    except Exception as e:
        st.error(f"Error loading steel data: {str(e)}. Check network connection.")
        return None

@st.cache_data(ttl=3600) 
def load_all_data():
    """
    Loads all data files and returns them as a tuple.
    Returns: (df_data, df_list, df_steel)
    """
    df_data, df_list = load_data()
    df_steel = load_steel_data()
    
    return df_data, df_list, df_steel