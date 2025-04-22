import os
from typing import Optional
from huggingface_hub import InferenceClient
from PIL import Image

def generate_image(
    prompt: str,
    model_id: str,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 50,
    height: int = 1024,
    width: int = 1024
) -> Image:
    """
    Generate an image from a text prompt using the specified model via the Hugging Face Inference API.

    Args:
        prompt (str): The text prompt to generate the image from, typically enhanced with a trigger word if required.
        model_id (str): The Hugging Face model ID (e.g., 'black-forest-labs/FLUX.1-dev' or 'goofyai/3D_Render_for_Flux').
        guidance_scale (float, optional): The guidance scale for controlling adherence to the prompt. Defaults to 7.5.
        num_inference_steps (int, optional): The number of inference steps for diffusion. Defaults to 10.
        height (int, optional): The height of the generated image in pixels. Defaults to 1024.
        width (int, optional): The width of the generated image in pixels. Defaults to 1024.

    Returns:
        PIL.Image: The generated image object ready for display or further processing.

    Raises:
        RuntimeError: If image generation fails due to API errors, network issues, or invalid parameters.
    """
    try:
        # Initialize the InferenceClient with the serverless HF Inference API
        client = InferenceClient(
            provider="hf-inference",
            token=os.getenv("HF_TOKEN")
        )

        # Generate the image using the specified model and parameters
        image = client.text_to_image(
            prompt=prompt,
            model=model_id,
            #guidance_scale=guidance_scale,
            #num_inference_steps=num_inference_steps,
            #height=height,
            #width=width
        )

        # Return the first (and typically only) image from the list
        return image

    except Exception as e:
        raise RuntimeError(f"Image generation failed: {str(e)}")
