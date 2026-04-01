import streamlit as st
import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

#===========================================================
#Telegram config (Free Alert)
#========================================================
Bot_token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
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
for key in ["leak_alert_sent", "water_alert_sent","leak_recovered","alert_log" ]:
  if key not in st.session_state:
    st.session_state[key] = [] if key == "alert_log" else False


#========================================
# LOAD DATA 
#======================================
@st.cache_data
def load_data():
  return
pd.read_csv("smart_water_sample_dataset.csv")
df=load_data()

#===============================================
#TRAIN MODELS
#===============================================
wq_encoder = LabelEncoder()
leak_encoder = LabelEncoder()

df["WQ_encoded"] = wq_encoder.fit_transform(df["WaterQuality_Label"])
df["Leak_encoded"] = leak_encoder.fit_transform(df["Leak_Label"])

water_features = ["pH","Turbidity_NTU","TDS_ppm","Temperature_C","Conductivity_uS_cm"]

leak_features = ["FlowRate_L_min","Pressure_bar"]

X_wq=df[water_features]
y_wq=df["WQ_encoded"]
X_leak=df[leak_features]
y_leak=df["Leak_encoded"]

Xw_train,Xw_test, yw_train,yw_test=train_test_split(X_wq,y_wq,test_size=0.2, random state=42)
Xl_train,Xl_test,yl_train,yl_test =train_test_split(X_leak,y_leak,test_size=0.2, random_state=42)

wq_model= RandomForestClassifier(n_estimators=200,random_state=42)
leak_model= RandomForestClassifier(n_estimators=200,random_state=42)

wq_model.fit(Xw_train,yw_train)
leak_model.fit(Xl_train,yl_train)

#====================================================
#RISK LEVEL FUNCTION
#==================================================
def calculate_leak_risk(flow,pressure):
  if pressure < 1.0 or flow > 90:
    return "HIGH"
  elif pressure < 1.8 or flow >60:
    return "MEDIUM"
  else:
    return "LOW"

#=======================================================
#SIDEBAR INPUTS
#======================================================
st.sidebar.header("📥 Enter Sensor Values")

pH = st.sidebar.number_input("pH", 0.0,14.0,7.2)
turbidity = st.sidebar_number_input("Turbidity (NTU)",0.0,50.0,3.0)
tds = st.sidebar_number_input("TDS (ppm)",0,2000,350)
temp = st.sidebar_number_input("Temperature (°C)",0.0,60.0,28.0)
cond = st.sidebar_number_input("Conductivity (µS/cm)",0,5000,800)
flow = st.sidebar_number_input("Flow Rate (L/min)",0.0,200.0,30.0)
pressure = st.sidebar_number_input("Pressure (bar)",0.0,10.0,2.5)
predict_btn = st.sidebar.button("🔍 Predict")




  
