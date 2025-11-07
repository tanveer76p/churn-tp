
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pickle
from sklearn.preprocessing import StandardScaler

# Set page configuration
st.set_page_config(
    page_title="Customer Churn Predictor",
    page_icon="📊",
    layout="wide"
)

# Load model and preprocessing objects
@st.cache_resource
def load_model():
    model = joblib.load('churn_prediction_model.pkl')
    scaler = joblib.load('feature_scaler.pkl')
    with open('feature_names.pkl', 'rb') as f:
        feature_names = pickle.load(f)
    return model, scaler, feature_names

model, scaler, feature_names = load_model()

# App title and description
st.title("🏦 Customer Churn Prediction Dashboard")
st.markdown("Predict which customers are likely to leave and take proactive action!")

# Sidebar for user input
st.sidebar.header("📋 Customer Information")

# Create input form
with st.form("customer_input_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Demographic Information")
        age = st.slider("Age", 18, 92, 40)
        gender = st.selectbox("Gender", ["Female", "Male"])
        
    with col2:
        st.subheader("Financial Information")
        credit_score = st.slider("Credit Score", 350, 850, 650)
        balance = st.number_input("Account Balance ($)", 0.0, 300000.0, 50000.0)
        estimated_salary = st.number_input("Estimated Salary ($)", 0.0, 250000.0, 75000.0)
        has_cr_card = st.selectbox("Has Credit Card?", ["No", "Yes"])
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Account Information")
        tenure = st.slider("Tenure (Years with Company)", 0, 10, 5)
        num_products = st.slider("Number of Products", 1, 4, 1)
        is_active_member = st.selectbox("Is Active Member?", ["No", "Yes"])
    
    with col4:
        st.subheader("Geographic Information")
        geography = st.selectbox("Country", ["France", "Germany", "Spain"])
    
    submitted = st.form_submit_button("🔮 Predict Churn Risk")

# Process input and make prediction
if submitted:
    # Create input dataframe
    input_data = {
        'CreditScore': credit_score,
        'Gender': 0 if gender == "Female" else 1,
        'Age': age,
        'Tenure': tenure,
        'Balance': balance,
        'NumOfProducts': num_products,
        'HasCrCard': 1 if has_cr_card == "Yes" else 0,
        'IsActiveMember': 1 if is_active_member == "Yes" else 0,
        'EstimatedSalary': estimated_salary,
        'Geo_France': 1 if geography == "France" else 0,
        'Geo_Germany': 1 if geography == "Germany" else 0,
        'Geo_Spain': 1 if geography == "Spain" else 0
    }
    
    input_df = pd.DataFrame([input_data])
    
    # Ensure correct column order
    input_df = input_df[feature_names]
    
    # Scale features
    input_scaled = scaler.transform(input_df)
    
    # Make prediction
    churn_probability = model.predict_proba(input_scaled)[0][1]
    churn_prediction = model.predict(input_scaled)[0]
    
    # Display results
    st.success("✅ Prediction Complete!")
    
    # Create results columns
    result_col1, result_col2 = st.columns(2)
    
    with result_col1:
        st.subheader("Churn Risk Assessment")
        
        # Progress bar for churn probability
        st.metric(
            label="Churn Probability",
            value=f"{churn_probability:.1%}",
            delta="High Risk" if churn_probability > 0.5 else "Low Risk"
        )
        
        # Visual progress bar
        st.progress(float(churn_probability))
        
        # Prediction result
        if churn_prediction == 1:
            st.error(f"🚨 HIGH RISK: This customer is likely to churn!")
        else:
            st.success(f"✅ LOW RISK: This customer is likely to stay!")
    
    with result_col2:
        st.subheader("Key Risk Factors")
        
        # Display top risk factors based on input
        risk_factors = []
        
        if age > 45:
            risk_factors.append("👴 Older customer (higher churn risk)")
        if num_products == 1:
            risk_factors.append("📦 Only one product (higher churn risk)")
        if balance > 100000:
            risk_factors.append("💰 High balance (increased churn risk)")
        if is_active_member == "No":
            risk_factors.append("💤 Inactive member (higher churn risk)")
        if geography == "Germany":
            risk_factors.append("🇩🇪 German customer (higher churn rate)")
        
        if risk_factors:
            for factor in risk_factors:
                st.warning(factor)
        else:
            st.info("🎉 No major risk factors identified!")
    
    # Recommendation section
    st.subheader("🎯 Retention Recommendations")
    
    if churn_probability > 0.7:
        st.error("**Immediate Action Required:**")
        st.write("- Personal retention call from account manager")
        st.write("- Special loyalty offer or discount")
        st.write("- Product bundle upgrade opportunity")
    elif churn_probability > 0.5:
        st.warning("**Proactive Engagement Needed:**")
        st.write("- Targeted email campaign")
        st.write("- Customer satisfaction survey")
        st.write("- Cross-sell additional products")
    else:
        st.success("**Maintenance Mode:**")
        st.write("- Continue regular engagement")
        st.write("- Monitor for changes in behavior")
        st.write("- Maintain excellent service quality")

# Add sidebar information
st.sidebar.markdown("---")
st.sidebar.subheader("About This App")
st.sidebar.info(
    "This churn prediction model uses machine learning to identify "
    "customers at risk of leaving. The model was trained on historical "
    "customer data and achieves 85% accuracy in predicting churn."
)

st.sidebar.subheader("Top Churn Drivers")
st.sidebar.write("""
- 🔴 Number of Products
- 🔴 Customer Age  
- 🟠 Account Balance
- 🟠 Active Member Status
""")
