import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

from PIL import Image
from io import BytesIO

# ----------------------------- #
#      1. CONFIG & SETUP        #
# ----------------------------- #

st.set_page_config(
    page_title="Ghost-Trace: Forensic AI",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔎"
)

# Load API key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("🚨 API Key Error: Please set GEMINI_API_KEY in your .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=API_KEY)


# ----------------------------- #
#      2. CORE FUNCTION         #
# ----------------------------- #

def reconstruct_and_score(image: Image.Image):
    """Enhances blurry vehicle images + gives plate & score"""

    prompt = (
        "This is a blurry image from a hit-and-run scene. "
        "Act as a Forensic Reconstruction Agent. "
        "1. Generate a NEW high-resolution image where the license plate is perfectly clear. "
        "2. Provide the license plate number, confidence score, and 2-line justification."
    )

    response = genai.generate_content(
        model="gemini-1.5-flash",
        contents=[prompt, image]
    )

    # Extract text
    text_result = response.text

    # Try to extract enhanced image
    enhanced_image = None
    try:
        for part in response._result.candidates[0].content.parts:
            if hasattr(part, "inline_data"):
                enhanced_image = Image.open(BytesIO(part.inline_data.data))
    except:
        enhanced_image = None

    return enhanced_image, text_result


# ----------------------------- #
#        3. STREAMLIT UI        #
# ----------------------------- #

st.title("🚨 Ghost-Trace: AI Forensic Reconstruction Engine")
st.markdown("### Powered by Gemini Forensic Reconstruction")

st.divider()

# Layout
input_col, control_col = st.columns([2, 1])

with input_col:
    with st.container(border=True):
        st.subheader("1. Upload Evidence 📹")
        uploaded_file = st.file_uploader(
            "Upload blurry CCTV/Dashcam image",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            input_image = Image.open(uploaded_file)
            st.image(input_image, use_column_width=True, caption="Original Blurry Input")


with control_col:
    st.info("🎯 **Upload a blurry image to identify vehicle details using AI.**")

    if uploaded_file:
        if st.button("🚀 RUN GHOST-TRACE ANALYSIS", type="primary", use_container_width=True):

            st.subheader("2. Analysis Running...")
            with st.spinner("Reconstructing forensic image..."):
                enhanced_image, analysis_text = reconstruct_and_score(input_image)

            st.divider()
            st.success("✅ **TRACE COMPLETE!**")

            result_col, score_col = st.columns([1, 1])

            with result_col:
                st.subheader("Enhanced Reconstruction")
                if enhanced_image:
                    st.image(enhanced_image, use_column_width=True)
                else:
                    st.error("No enhanced image returned.")

            with score_col:
                st.subheader("Forensic Confidence Report")
                st.markdown(analysis_text)
                st.balloons()
