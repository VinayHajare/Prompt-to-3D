import os
import shutil
import streamlit as st
import pyvista as pv
from stpyvista.panel_backend import stpyvista

def start_session():
    # Create a temp directory to session data
    TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
    os.makedirs(TMP_DIR, exist_ok=True)
    st.session_state.temp_dir = TMP_DIR
    
def end_session():
    # Clean up the temp directory
    shutil.rmtree(st.session_state.temp_dir)

def render_glb(path: str) -> None:
    """ 
    Render a GLB file using PyVista and stpyvista.
    This function will display the GLB file in the Streamlit app using PyVista and stpyvista.
    Args:
        path (str): path to the GLB file.
    """
    st.header("🏗️ Rendering GLB Model", anchor=False, divider="rainbow")
    
    plotter = pv.Plotter(border=False, window_size=[500, 400], off_screen=True)
    plotter.background_color = "#f0f8ff"
    
    plotter.import_gltf(path)
    
    plotter.view_zy()
    stpyvista(plotter)