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

#====================================================
#PREDICTIONS
#=====================================================
col1,col2=st.columns(2)

#------WATER QUALITY------
with col1:
  st.subheader(" Water Quality")

  if predict_btn:
    input_wq=pd.DataFrame([[pH, turbidity,tds,temp,cond]],columns=water_features)
    result=wq_encoder.inverse_transform(wq_model.predict(input_wq))[0]
    
    if result=="Unsafe":
      st.error("Water Quality: UNSAFE")
      st.session_state.water_recovered = False
      
      if not st.sesion_state.water_alert_sent:
        send_telegram_alert("WATER QUALITY UNSAFE \nImmediate action required.")
        st.session_state.water_alert_sent=True
        st.session_state.alert_log.append(
          {"Type": "Water Unsafe","Risk": "MEDIUM"}
        )
        
    else:
      st.success("Water Quality :SAFE)

      if st.session_state.water_alert_sent and not st.session_state.water_recovered:
        send_telegram_alert("WATER QUALITY NORMAL \nWater is Safe again.")
        st.session_state.water_recovered=True
        st.session_state.water_alert_sent=False


#--------LEAK DETECTION----------
with col2:
  st.subheader("Leak Detection")

if predict_btn:
  input_leak=pd.DataFrame([[flow,pressure]],columns=leak_features)
  result=leak_encoder.inverse_transform(leak_model.predict(input_leak))[0]
  risk=calculate_leak_risk(flow,pressure)

  if result=="Leak":
    st.error(f" Leak Detected | Risk:{risk}")
    st.session_state_.leak_recovered= False

    if not st.session_state.leak_alert_sent:
      send_telegram_alert(
        f" PIPELINE LEAK ALERT\n Flow : {Flow} L/min\nPressure: {pressure}bar\nRisk: {risk}"
      )
      st.session_state.leak_alert_sent=True
      st.session_state.alert_log.append(
        {"Type": "Leak","Risk":risk}
      )

  else:
    st.success("No Leak Detected")

    if(st.session_state.leak_alert_sent and not st.session_state.leak_recovered:
      send_telegram_alert("PIPELINE STATUS NORMAL\nLeak resolved")
      st.session_state.leak_recovered =True
      st.session_state.leak_alert_sent=False



#==========================================================
#ALERT HISTORY
#==========================================================
st.subheader("Alert History")
st.dataframe(pd.DataFrame(st.session_state.alert_log))

#==============================================================
#JUDGE EXPLANATION
#===============================================================
st.subheader("Explanation About it")
st.info("""
Our AI-based smart water monitoring system detects unsafe water
and pipeline leaks using machine learning models.

When a problem occurs, a real-time alert is sent using a free
Telegram-based notification system. To avoid alert flooding,
alerts are sent only once per incident.

When the issue is resolved, the system automatically sends a recovery 
alert indicating that conditions are back to normal.

Each alert is classified by risk level and stored in a dashboard
for monitoring and future analysis. The system works on existing
pipelines without infrastructure changes.
""")
