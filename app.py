import streamlit as st

# Initialize session state variables
if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = None
if "generated_image_path" not in st.session_state:
    st.session_state.generated_image_path = None
if "uploaded_image_path" not in st.session_state:
    st.session_state.uploaded_image_path = None
if "generated_model_state" not in st.session_state:
    st.session_state.generated_model_state = None
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "glb_path" not in st.session_state:
    st.session_state.glb_path = None
if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None

from util import start_session, end_session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Start session
start_session()

from img2_3d_pipeline import initialize_pipeline

# Initialize the pipeline
initialize_pipeline()

# Set page configuration
st.set_page_config(page_title="3D Asset Generator", page_icon="🎨", layout="wide")

# Set page logo
st.logo(image="assets/logo.png", icon_image="assets/logo.png")


# Sidebar with branding
with st.sidebar:
    st.title("3D Asset Generator 🎨")
    st.caption("Create 3D assets from text or images")
    st.markdown("Created with ❤️ by [VinayHajare](https://github.com/VinayHajare)")
    st.markdown("---")
    

# Define pages
home_page = st.Page("0_home.py", title="Home", icon="🏠")
generator_page = st.Page("1_generate_assets.py", title="Generator", icon="🎨")

# Set up navigation
page = st.navigation(pages=[home_page, generator_page])
page.run()

# Clean up the temp directory
end_session()