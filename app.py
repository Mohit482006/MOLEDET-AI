import streamlit as st
import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

#===========================================================
#Telegram config (Free Alert)
#========================================================
Bot_token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
chat_id="34323XXXXX"

def send_telegram_alert(message):
  url=f"https://api.telegram.org/bot{Bot_token}/sendMessage"
  payload={"Chat_id" : chat_id , "text" : message}
  requests.post(url,data=payload)


#====================================================
#STREAMLIT CONFIG
#=====================================================

st.set_page_config(page_title = "Smart Water", layout="wide")
st.title("💧 Smart Water Monitoring System")
st.write("Water Quality Prediction + Pipeline Leak Detection")

#============================================
#SESSION STATE
#===========================================
  
