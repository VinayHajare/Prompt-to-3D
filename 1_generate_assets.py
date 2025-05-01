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
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                generated_image.save(img_byte_arr, format='PNG')
                st.session_state.generated_image_bytes = img_byte_arr.getvalue()
                st.image(st.session_state.generated_image_bytes, caption="Generated 2D Image", use_container_width=True)
            except Exception as e:
                st.error(f"Error in Txt2Img pipeline: {e}")
        else:
            st.error("Please enter a prompt.")

with col2:
    st.subheader("Or Upload an Image")
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        # Store uploaded image as bytes
        img_bytes = uploaded_image.read()
        st.session_state.uploaded_image_bytes = img_bytes
        st.image(img_bytes, caption="Uploaded Image", use_container_width=True)

# --- Second Row: 3D Model Section ---
st.markdown("---")
st.subheader("3D Model Preview & Download")

if st.button("Generate 3D Model"):
    image_bytes = st.session_state.get('generated_image_bytes') or st.session_state.get('uploaded_image_bytes')
    if image_bytes:
        with st.spinner("Generating 3D Model... Please wait."):
            try:
                # Convert bytes to PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                state, video_path = image_to_3d(image=image, seed=0)
                st.session_state.generated_model_state = state
                # Read video as bytes
                if os.path.exists(video_path):
                    with open(video_path, 'rb') as f:
                        st.session_state.video_bytes = f.read()
                else:
                    st.error("Video file not found.")
            except Exception as e:
                st.error(f"Error generating 3D model: {e}")
    else:
        st.error("No image source available for 3D model generation.")

# Display 3D model video if available
if st.session_state.get('video_bytes'):
    st.video(st.session_state.video_bytes, format="video/mp4")
    st.success("3D model generated!")
    
    # GLB Extraction Settings
    with st.expander("GLB Extraction Settings", expanded=True):
        mesh_simplify = st.slider("Simplify", 0.9, 0.98, 0.95, 0.01)
        texture_size = st.slider("Texture Size", 512, 2048, 1024, 512)
        if st.button("Extract GLB", key="extract_glb", type="secondary"):
            if st.session_state.get('generated_model_state'):
                with st.spinner("Extracting GLB..."):
                    try:
                        # Extract GLB to a temporary file
                        glb_path = extract_glb(st.session_state.generated_model_state, mesh_simplify, texture_size)
                        # Read GLB as bytes
                        with open(glb_path, 'rb') as f:
                            st.session_state.glb_bytes = f.read()
                    except Exception as e:
                        st.error(f"Error extracting GLB: {e}")
            else:
                st.error("No 3D model state available for GLB extraction.")

# Display GLB if available
if st.session_state.get('glb_bytes'):
    try:
        # Write GLB bytes to a temporary file for rendering
        temp_glb_path = os.path.join(st.session_state.temp_dir, "temp_sample.glb")
        with open(temp_glb_path, "wb") as f:
            f.write(st.session_state.glb_bytes)
        render_glb(temp_glb_path)
        st.success("GLB file extracted!")
        # Provide download button for GLB
        st.download_button(
            label="Download GLB",
            data=st.session_state.glb_bytes,
            file_name="sample.glb",
            mime="model/gltf-binary"
        )
        st.success("GLB file ready for download!")
        # Clean up temporary GLB file
        if os.path.exists(temp_glb_path):
            os.remove(temp_glb_path)
    except Exception as e:
        st.error(f"Error rendering GLB: {e}")
