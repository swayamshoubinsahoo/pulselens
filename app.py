import os
import time
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

st.set_page_config(
    page_title="PulseLens AI - Multimodal Tele-Triage",
    page_icon="🩺",
    layout="wide",
)

# --- Sidebar for API Key & Settings ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("Enter your **Google AI Studio API Key** below to power the triage model.")
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        placeholder="AIzaSy...",
        help="Get a free key from https://aistudio.google.com/app/apikey"
    )
    
    if user_api_key:
        st.success("API Key detected! Ready to analyze.", icon="✅")
    else:
        st.warning("Please paste your Gemini API key to proceed.", icon="⚠️")

    st.markdown("---")
    st.markdown("### About PulseLens AI")
    st.caption("A multimodal tele-triage assistant designed to bridge rural primary care gaps by converting visual data and symptoms into actionable SOAP reports.")

st.title("🩺 PulseLens AI: Multimodal Tele-Triage Assistant")
st.caption("AI-driven clinical pre-screening, risk stratification, and SOAP record generator.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Patient Symptoms & Profile")
    age = st.number_input("Patient Age", min_value=1, max_value=120, value=25)
    gender = st.selectbox("Biological Sex", ["Male", "Female", "Other"])
    symptoms = st.text_area(
        "Reported Symptoms & Duration",
        placeholder="e.g., Red itchy rash appearing on right arm over the past 2 days, mild local swelling...",
        height=140,
    )

    st.subheader("2. Clinical Visual Input")
    input_method = st.radio("Choose Input Method:", ["Upload Image", "Use Camera"], horizontal=True)

    image_file = None
    if input_method == "Upload Image":
        image_file = st.file_uploader("Upload visual evidence (wound, rash, trauma)", type=["jpg", "jpeg", "png"])
    else:
        image_file = st.camera_input("Capture image directly")

    if image_file:
        img = Image.open(image_file)
        st.image(img, caption="Intake Image", use_container_width=True)

    analyze_btn = st.button("🚀 Run Triage Analysis", type="primary", use_container_width=True)

with col2:
    st.subheader("3. Triage Report & SOAP Summary")

    if analyze_btn:
        if not user_api_key:
            st.error("Please enter your Gemini API Key in the left sidebar first.")
        elif not symptoms and not image_file:
            st.warning("Please enter patient symptoms or provide an image.")
        else:
            with st.spinner("Analyzing via Gemini Multimodal Engine..."):
                client = genai.Client(api_key=user_api_key)
                contents = []
                if image_file:
                    contents.append(Image.open(image_file))

                prompt = f"""
                You are PulseLens AI, an expert clinical triage assistant. Analyze this case:
                - Patient Age: {age}
                - Gender: {gender}
                - Symptoms & History: {symptoms if symptoms else 'Visual intake provided primarily.'}

                Provide a structured clinical triage report following this exact format:

                ### 🚨 Triage Urgency Tier
                State one: [IMMEDIATE / SEMI-URGENT / ROUTINE PRIMARY CARE]
                Provide a 2-sentence rationale for this rating.

                ### 📋 Visual & Clinical Observations
                - Observable signs (erythema, swelling, lesions, trauma markers).

                ### 🩺 Standardized SOAP Note Summary
                * **S (Subjective):** Patient symptom history and intake notes.
                * **O (Objective):** Visual evidence findings and physical presentation.
                * **A (Assessment):** Top 3 differential diagnostic possibilities (ranked).
                * **P (Plan):** Next triage steps, recommended clinical tests, and red-flag alerts.

                ### ⚠️ Clinical Disclaimer
                PulseLens AI is a pre-screening decision support tool. It does not replace certified physician evaluation.
                """
                contents.append(prompt)

                # Retry up to 3 times if server returns 503 high demand
                response_text = None
                last_err = None

                for attempt in range(1, 4):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=contents,
                        )
                        response_text = response.text
                        break
                    except Exception as err:
                        last_err = str(err)
                        time.sleep(2)  # wait 2 seconds and retry

                if response_text:
                    st.success("Triage Assessment Completed")
                    st.markdown(response_text)
                else:
                    st.error(f"Error executing analysis: {last_err}")
    else:
        st.info("Fill out symptoms or load an image on the left, then click 'Run Triage Analysis'.")