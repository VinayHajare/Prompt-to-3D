import streamlit as st
import pyvista as pv
import stpyvista as stpv
from PIL import Image
import os
import io

from prompt_enhancer import PromptEnhancer
from txt2img_pipeline import generate_image
from img2_3d_pipeline import image_to_3d, extract_glb 
from util import render_glb 

st.title("Asset Generator")
st.markdown("Enter a text prompt or upload an image to generate your 3D asset.")

# --- First Row: Input Section (Two Columns) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Generate from Prompt")
    user_prompt = st.text_input("Enter your prompt", placeholder="e.g., A 3D render of a magical sword")
    if st.button("Generate 2D Image from Prompt"):
        if user_prompt:
            st.info("Processing your prompt...")
            # Call Prompt Enhancer
            enhancer = PromptEnhancer()
            try:
                enhanced_prompt, selected_model = enhancer.enhance_prompt(user_prompt)
                st.write("**Enhanced Prompt:**", enhanced_prompt)
                st.write("**Selected Model:**", selected_model)
            except Exception as e:
                st.error(f"Error enhancing prompt: {e}")
            
            # Call Txt2Img pipeline
            try:
                generated_image = generate_image(enhanced_prompt, selected_model)
                generated_image_path = os.path.join(st.session_state.temp_dir, "generated_image.png")
                generated_image.save(generated_image_path)
                
                if generated_image_path and os.path.exists(generated_image_path):
                    st.session_state.generated_image_path = generated_image_path
                    st.image(generated_image_path, caption="Generated 2D Image", use_column_width=True)
                else:
                    st.error("Failed to generate image from prompt.")
            except Exception as e:
                st.error(f"Error in Txt2Img pipeline: {e}")
        else:
            st.error("Please enter a prompt.")

with col2:
    st.subheader("Or Upload an Image")
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        # Read the uploaded file and save it as a image
        uploaded_image_path = os.path.join(st.session_state.temp_dir, "uploaded_image.png")
        img_bytes = uploaded_image.read()
        img = Image.open(io.BytesIO(img_bytes))
        img.save(uploaded_image_path)
        
        st.session_state.uploaded_image_path = uploaded_image_path
        st.image(uploaded_image_path, caption="Uploaded Image", use_container_width=True)

# --- Second Row: 3D Model Section ---
st.markdown("---")
st.subheader("3D Model Preview & Download")

if st.button("Generate 3D Model"):
    image_source = st.session_state.generated_image_path or st.session_state.uploaded_image_path
    if image_source:
        with st.spinner("Generating 3D Model... Please wait."):
            try:
                image = Image.open(image_source)
                state, video_path = image_to_3d(image=image, seed=0)
                st.session_state.generated_model_state = state
                st.session_state.video_path = video_path
                if os.path.exists(video_path):
                    with open(video_path, 'rb') as f:
                        video_bytes = f.read()
                    st.session_state.video_bytes = video_bytes
                    
            except Exception as e:
                st.error(f"Error generating 3D model: {e}")
    else:
        st.error("No image source available for 3D model generation.")

# Display 3D model outputs if available
if st.session_state.video_bytes:
    st.video(st.session_state.video_bytes, format="video/mp4")
    st.success("3D model generated!")
    
    # GLB Extraction Settings
    with st.expander("GLB Extraction Settings", expanded=True):
        mesh_simplify = st.slider("Simplify", 0.9, 0.98, 0.95, 0.01)
        texture_size = st.slider("Texture Size", 512, 2048, 1024, 512)
        if st.button("Extract GLB", key="extract_glb", type="secondary"):
            if st.session_state.generated_model_state:
                with st.spinner("Extracting GLB..."):
                    try:
                        glb_path = extract_glb(st.session_state.generated_model_state, mesh_simplify, texture_size)
                        st.session_state.glb_path = glb_path
                    except Exception as e:
                        st.error(f"Error extracting GLB: {e}")
            else:
                st.error("No 3D model state available for GLB extraction.")

# Display GLB if available
if st.session_state.glb_path:
    try:
        render_glb(st.session_state.glb_path)
        st.success("GLB file extracted!")
        with open(st.session_state.glb_path, "rb") as f:
            st.download_button("Download GLB", f, file_name="sample.glb", mime="model/gltf-binary")
        st.success("GLB file ready for download!")
    except Exception as e:
        st.error(f"Error rendering GLB: {e}")
        print(f"Error rendering GLB: {e}")