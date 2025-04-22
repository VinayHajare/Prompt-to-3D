import streamlit as st

# Welcome section
st.title("Welcome to 3D Asset Generator 🎨")
st.write("Create 3D assets effortlessly from text prompts or images!")

# Layout for video and features
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.header("See It in Action")
    st.video("assets/teaser.mp4", muted=True,loop=True, autoplay=True)  
    st.caption("Watch how easy it is to create stunning 3D assets.")

with col2:
    st.header("What Can You Do?")
    st.markdown("""
    - **Create Assets**: Generate 3D models for games, VR, or 3D printing.
    - **Design Models**: Build prototypes for architectural or product design.
    """)
    if st.button("Get Started", key="home_button", type="primary"):
        st.switch_page("1_generate_assets.py")

# Feedback section
with st.expander("Have Feedback?"):
    with st.form("feedback_form"):
        name = st.text_input("Your Name")
        feedback = st.text_area("Your Feedback")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Thanks for your feedback!")
        #TODO: Send feedback to a email
        
        