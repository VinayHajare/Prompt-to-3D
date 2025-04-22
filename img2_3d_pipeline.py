import os
import shutil
import numpy as np
import imageio
import torch
from typing import Tuple
from PIL import Image
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.representations import Gaussian, MeshExtractResult
from trellis.utils import render_utils, postprocessing_utils
from easydict import EasyDict as edict
import tempfile
import streamlit as st

# Configuration
MAX_SEED = np.iinfo(np.int32).max
TMP_DIR = st.session_state.temp_dir
os.environ['SPCONV_ALGO'] = 'native'

# Initialize pipeline (to be called once in the main app)
pipeline = None

def initialize_pipeline():
    """
    Initialize the Trellis pipeline for image to 3D conversion.

    Returns:
        None: The function initializes the pipeline and sets it to the global variable.
    """
    global pipeline
    if pipeline is None:
        pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
        pipeline.cuda()
        try:
            pipeline.preprocess_image(Image.fromarray(np.zeros((512, 512, 3), dtype=np.uint8)))  # Preload rembg
        except:
            pass
    return pipeline

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess the input image.
    Args:
        image (Image.Image): The input image to preprocess.
    Returns:
        Image.Image: The preprocessed image.
    """
    return pipeline.preprocess_image(image)

def pack_state(gs: Gaussian, mesh: MeshExtractResult) -> dict:
    """
    Pack the Gaussian and mesh states into a dictionary.
    Args:
        gs (Gaussian): The Gaussian object.
        mesh (MeshExtractResult): The mesh object.
    Returns:
        dict: A dictionary containing the packed states.
    """
    return {
        'gaussian': {
            **gs.init_params,
            '_xyz': gs._xyz.cpu().numpy(),
            '_features_dc': gs._features_dc.cpu().numpy(),
            '_scaling': gs._scaling.cpu().numpy(),
            '_rotation': gs._rotation.cpu().numpy(),
            '_opacity': gs._opacity.cpu().numpy(),
        },
        'mesh': {
            'vertices': mesh.vertices.cpu().numpy(),
            'faces': mesh.faces.cpu().numpy(),
        },
    }

def unpack_state(state: dict) -> Tuple[Gaussian, edict]:
    """
    Unpack the state dictionary into Gaussian and mesh objects.
    Args:
        state (dict): A dictionary containing packed states.
    Returns:
        Tuple[Gaussian, edict]: A tuple containing the Gaussian object and mesh object.
    """
    gs = Gaussian(
        aabb=state['gaussian']['aabb'],
        sh_degree=state['gaussian']['sh_degree'],
        mininum_kernel_size=state['gaussian']['mininum_kernel_size'],
        scaling_bias=state['gaussian']['scaling_bias'],
        opacity_bias=state['gaussian']['opacity_bias'],
        scaling_activation=state['gaussian']['scaling_activation'],
    )
    gs._xyz = torch.tensor(state['gaussian']['_xyz'], device='cuda')
    gs._features_dc = torch.tensor(state['gaussian']['_features_dc'], device='cuda')
    gs._scaling = torch.tensor(state['gaussian']['_scaling'], device='cuda')
    gs._rotation = torch.tensor(state['gaussian']['_rotation'], device='cuda')
    gs._opacity = torch.tensor(state['gaussian']['_opacity'], device='cuda')
    
    mesh = edict(
        vertices=torch.tensor(state['mesh']['vertices'], device='cuda'),
        faces=torch.tensor(state['mesh']['faces'], device='cuda'),
    )
    return gs, mesh

def get_seed(randomize_seed: bool, seed: int) -> int:
    """
    Get the random seed.
    Args:
        randomize_seed (bool): Whether to randomize the seed.
        seed (int): The seed value.
    Returns:
        int: The random seed value.
    """
    return np.random.randint(0, MAX_SEED) if randomize_seed else seed

def image_to_3d(
    image: Image.Image,
    seed: int = 0,
    ss_guidance_strength: float = 7.5,
    ss_sampling_steps: int = 12,
    slat_guidance_strength: float = 3.0,
    slat_sampling_steps: int = 12
) -> Tuple[dict, str]:
    """
    Convert an image to a 3D model.
    Args:
    
        image (Image.Image): The input image to convert.
        seed (int): The random seed for generation.
        ss_guidance_strength (float): Strength for sparse structure guidance.
        ss_sampling_steps (int): Number of sampling steps for sparse structure.
        slat_guidance_strength (float): Strength for slat guidance.
        slat_sampling_steps (int): Number of sampling steps for slat.
    Returns:
        Tuple[dict, str]: A tuple containing the state dictionary and the video path.
    """

    outputs = pipeline.run(
        image,
        seed=seed,
        formats=["gaussian", "mesh"],
        preprocess_image=True,
        sparse_structure_sampler_params={
            "steps": ss_sampling_steps,
            "cfg_strength": ss_guidance_strength,
        },
        slat_sampler_params={
            "steps": slat_sampling_steps,
            "cfg_strength": slat_guidance_strength,
        },
    )
    video = render_utils.render_video(outputs['gaussian'][0], num_frames=120)['color']
    video_geo = render_utils.render_video(outputs['mesh'][0], num_frames=120)['normal']
    video = [np.concatenate([video[i], video_geo[i]], axis=1) for i in range(len(video))]
    video_path = os.path.join(TMP_DIR, 'sample.mp4')
    imageio.mimsave(video_path, video, fps=15)
    state = pack_state(outputs['gaussian'][0], outputs['mesh'][0])
    torch.cuda.empty_cache()
    return state, video_path

def extract_glb(
    state: dict,
    mesh_simplify: float = 0.95,
    texture_size: int = 1024
) -> str:
    """
    Extract a GLB file from the 3D model state.
    Args:
        state (dict): The state dictionary containing the 3D model data.
        mesh_simplify (float): The simplification factor for the mesh.
        texture_size (int): The size of the texture.
    Returns:
        str: The path to the generated GLB file.
    """
    gs, mesh = unpack_state(state)
    glb = postprocessing_utils.to_glb(gs, mesh, simplify=mesh_simplify, texture_size=texture_size, verbose=False)
    glb_path = os.path.join(TMP_DIR, 'sample.glb')
    glb.export(glb_path)
    torch.cuda.empty_cache()
    return glb_path