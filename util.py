import os
import shutil
import streamlit as st
import pyvista as pv
from stpyvista.panel_backend import stpyvista


def end_session():
    # Clean up temporary directory only if it exists
    if hasattr(st.session_state, 'temp_dir') and os.path.exists(st.session_state.temp_dir):
        shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

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
