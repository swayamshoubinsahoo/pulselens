# PulseLens: Multimodal Tele-Triage Assistant

PulseLens AI is an intelligent clinical decision-support co-pilot designed to decentralize pre-screening and clinical documentation for rural, primary care, and resource-limited clinics.

## Key Features
- Multimodal Intake: Analyzes patient narratives alongside clinical visual evidence (dermatology, lesions, wounds, trauma).
- Automated Risk Stratification: Instantly categorizes cases into urgency tiers (Immediate, Semi-Urgent, Routine Primary Care).
- Standardized SOAP Generation: Synthesizes Subjective, Objective, Assessment, and Plan notes to eliminate routine paperwork.
- Edge & Web Ready: Built with a lightweight, browser-accessible architecture suitable for low-bandwidth environments.

## Architecture & Tech Stack
- AI Engine: Google Gemini Multimodal API (gemini-3.8-flash)
- Framework: Streamlit (Python)
- Vision & Media: Pillow (PIL)
- Configuration: Python-Dotenv

## Quickstart & Local Setup

1. Clone the Repository:
git clone https://github.com/swayamshoubinsahoo/pulselens-ai.git
cd pulselens-ai

2. Install Dependencies:
pip install -r requirements.txt

3. Configure API Credentials:
Create a .env file in the root directory:
GEMINI_API_KEY=your_actual_gemini_api_key_here

4. Launch Application:
streamlit run app.py

The application will open at http://localhost:8501.

## Clinical Disclaimer
PulseLens AI is designed strictly as an automated triage co-pilot and clinical pre-screening tool. It does not replace definitive medical diagnosis by a licensed physician.
