import os
import time
from PIL import Image
from dotenv import load_dotenv
import streamlit as st
from google import genai

load_dotenv()

st.set_page_config(
    page_title="PulseLens - Clinical Tele-Triage",
    page_icon="🩺",
    layout="wide",
)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("Enter your **Google AI Studio API Key** below:")
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        placeholder="AIzaSy...",
    )
    st.markdown("---")
    st.markdown("### About PulseLens")
    st.caption(
        "Tele-triage pipeline translating patient demographics, clinical observations, "
        "and symptom imagery into standardized SOAP notes."
    )

client = None
if user_api_key:
    try:
        client = genai.Client(api_key=user_api_key)
    except Exception as e:
        st.sidebar.error(f"Client initialization error: {e}")

st.title("🩺 PulseLens: Remote Clinical Tele-Triage")
st.markdown("Automated patient triage note extraction and SOAP synthesis.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Patient Profile & Demographics")
    
    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        patient_age = st.number_input("Patient Age", min_value=0, max_value=120, value=25, step=1)
    with demo_col2:
        patient_sex = st.selectbox("Biological Sex", ["Select", "Male", "Female", "Other / Intersex"])

    st.markdown("**Symptoms & Intake Notes**")
    symptoms = st.text_area(
        "Enter symptoms, duration, and patient context:",
        placeholder="e.g., Red itchy rash appearing on right arm over the past 2 days, mild local swelling...",
        height=130,
        label_visibility="collapsed",
    )

    st.subheader("2. Clinical Visual Input")
    input_method = st.radio("Choose Input Method:", ["Upload Image", "Use Camera"], horizontal=True)

    img = None
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader("Upload visual evidence (wound, rash, trauma)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Clinical Image", use_container_width=True)
    else:
        camera_file = st.camera_input("Capture clinical evidence")
        if camera_file:
            img = Image.open(camera_file)
            st.image(img, caption="Captured Clinical Image", use_container_width=True)

    run_btn = st.button("🚀 Run Triage Analysis", type="primary", use_container_width=True)

with col2:
    st.subheader("3. Triage Report & SOAP Assessment")
    
    if run_btn:
        if not user_api_key:
            st.error("Please provide a Gemini API Key in the sidebar to proceed.")
            st.stop()

        if not symptoms and not img:
            st.warning("Please provide clinical symptoms or an image before running the assessment.")
            st.stop()

        prompt = """
### Role & Objective
You are an expert clinical triage assistant. Analyze the patient demographics, reported symptoms, and visual imagery.
Synthesize findings into an objective, standardized medical summary:

### 🚨 Triage Urgency Tier
State one: [IMMEDIATE / SEMI-URGENT / ROUTINE PRIMARY CARE]
Provide a concise 2-sentence rationale for this triage acuity rating based on the patient profile.

### 👁️ Visual & Clinical Observations
- Observable signs (erythema, lesion morphology, trauma indicators, swelling).

### 📋 Standardized SOAP Note Summary
* **S (Subjective):** Patient age, biological sex, reported symptoms, onset, and duration.
* **O (Objective):** Visual presentation markers and observable abnormalities.
* **A (Assessment):** Top 3 differential diagnostic considerations (ranked).
* **P (Plan):** Immediate triage guidance, recommended confirmatory workups, and critical red flags requiring emergency care.

### ⚠️ Clinical Disclaimer
PulseLens is a decision-support and triage preparation tool. It does not replace definitive medical evaluation by a licensed healthcare professional.
"""

        contents = []
        patient_profile_str = f"Patient Demographics: Age {patient_age}, Sex: {patient_sex}\n"
        if symptoms:
            patient_profile_str += f"Reported Symptoms & History: {symptoms}\n"
        
        contents.append(patient_profile_str)
        
        if img:
            contents.append(img)
            
        contents.append(prompt)

        response_text = None
        last_err = None

        with st.spinner("Discovering available models and evaluating patient profile..."):
            # Dynamically discover all supported models for this specific API key
            discovered_models = []
            try:
                for m in client.models.list():
                    methods = getattr(m, "supported_generation_methods", []) or getattr(m, "supported_methods", []) or []
                    name = getattr(m, "name", "")
                    if "generateContent" in methods or not methods:
                        # Normalize model name format
                        clean_name = name.replace("models/", "") if name else ""
                        if clean_name:
                            discovered_models.append(clean_name)
            except Exception as e:
                last_err = f"Model discovery error: {e}"

            # Fallback list if discovery returned empty
            if not discovered_models:
                discovered_models = ["gemini-1.5-flash-001", "gemini-1.5-pro-001", "gemini-1.0-pro"]

            # Sort so flash/pro models come first
            def model_priority(m_name):
                if "flash" in m_name:
                    return 0
                if "pro" in m_name:
                    return 1
                return 2

            models_to_run = sorted(discovered_models, key=model_priority)

            # Iterate through the dynamically discovered models
            for model_name in models_to_run:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                    )
                    if response and response.text:
                        response_text = response.text
                        break
                except Exception as err:
                    last_err = str(err)
                    time.sleep(0.5)

        if response_text:
            st.success("Triage Assessment Completed")
            st.markdown(response_text)
        else:
            st.error(f"Execution failed across all models: {last_err}")
    else:
        st.info("Fill out patient demographics and symptoms or load an image on the left, then click 'Run Triage Analysis'.")