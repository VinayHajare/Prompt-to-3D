import os
from huggingface_hub import InferenceClient
from typing import Optional

class PromptEnhancer:
    def __init__(self, llm="Qwen/Qwen2.5-7B-Instruct"):
        """
        A module to enhance user prompts for generating high-quality 3D images and select the most appropriate model based on the enhanced prompt.
        
        :param llm (str): The name of the LLM model to use for enhancing prompts. Default is "Qwen/Qwen2.5-7B-Instruct".
        """
        self.llm = InferenceClient(
            model=llm,
            provider="together",
            token=os.getenv("HF_TOKEN")
        )
        
        self.models = {
            "black-forest-labs/FLUX.1-dev": {
                "description": """
                    FLUX.1 [dev] is a high-performance variant of the FLUX.1 model family, designed for professional use cases. It excels in generating highly detailed and stylistically diverse images with strong prompt adherence and scene complexity.
                    Strengths:
                        - Produces high-quality, detailed images.
                        - Strong in prompt understanding and implementation.
                        - Capable of handling complex and diverse visual styles.
                        - Developed by the original creators of Stable Diffusion, ensuring strong foundational capabilities.
                """,
                "trigger_word": "None"
            },
            "goofyai/3D_Render_for_Flux": {
                "description": """
                    A fine-tuned version of FLUX.1 specifically optimized for 3D rendering tasks. It is tailored to generate realistic and accurate 3D models and scenes.
                    Strengths:
                        - Excellent for creating photorealistic 3D images.
                        - Capable of rendering precise geometric details and textures.
                        - Ideal for architectural visualization, product design, and 3D art creation.
                        - Combines the strengths of FLUX.1 with specialized 3D capabilities.
                """,
                "trigger_word": "3D render"
            },
            "gokaygokay/Flux-Game-Assets-LoRA-v2": {
                "description": """
                    A LoRA (Low-Rank Adaptation) adapter built on FLUX.1, designed specifically for generating game assets, including characters, environments, and props.
                    Strengths:
                        - Specializes in creating game-like aesthetics and fantasy settings.
                        - Generates ready-to-use textures and materials for game development.
                        - Supports a wide range of fantasy and sci-fi themes.
                        - Optimized for speed and quality in game asset creation.
                """,
                "trigger_word": "wbgmsst,"
            },
            "strangerzonehf/Flux-Isometric-3D-LoRA": {
                "description": """
                    A LoRA adapter for FLUX.1 focused on generating isometric 3D perspectives, ideal for creating flat, top-down, or side-view images.
                    Strengths:
                        - Excels in producing isometric-style images for games, maps, and diagrams.
                        - Capable of generating precise and symmetrical 3D scenes.
                        - Ideal for architectural, engineering, and game design projects requiring isometric views.
                        - Combines FLUX.1's strengths with specialized geometric rendering capabilities.
                """,
                "trigger_word": "Isometric 3D"
            },
            "strangerzonehf/Flux-NFT-Art99-LoRA": {
                "description": """
                    A LoRA adapter for FLUX.1 designed to generate unique NFT art. It focuses on creating digital art pieces with modern, colorful, and blockchain-inspired aesthetics.
                    Strengths:
                        - Specializes in generating vibrant, digital NFT art.
                        - Capable of creating unique styles tailored to the NFT community.
                        - Supports blockchain-inspired themes and visual effects.
                        - Ideal for artists focused on digital collectibles and modern art trends.
                """,
                "trigger_word": "NFT Art 99"
            },
        }
        
        self.prompt_template = """
        You are an expert in generating high-quality 3D images with a white background, tailored for assets and 3D models creation.
        Your task is to enhance a user's prompt to make it more effective for generating such images and to select the most appropriate model from a provided list based on the enhanced prompt.

        ## Guidelines

        1. **Select the Best Model**:
           - By default, choose 'black-forest-labs/FLUX.1-dev' for general 3D image generation unless specific keywords indicate otherwise.
           - Choose 'goofyai/3D_Render_for_Flux' if the prompt includes keywords like '3D render', 'photorealistic', 'architecture', 'product design'.
           - Choose 'gokaygokay/Flux-Game-Assets-LoRA-v2' if the prompt includes keywords like 'game', 'fantasy', 'sci-fi', 'assets'.
           - Choose 'strangerzonehf/Flux-Isometric-3D-LoRA' if the prompt includes keywords like 'isometric', 'top-down', 'side-view'.
           - Choose 'strangerzonehf/Flux-NFT-Art99-LoRA' if the prompt includes keywords like 'NFT', 'digital art', 'blockchain'.

        2. **Enhance the Prompt**:
           - Create a detailed and specific prompt for a high-quality 3D image with a white background.
           - Include details like perspective, lighting, object dimensions, and specific features to improve clarity and quality.
           - If the selected model has a trigger word (other than 'None'), incorporate it naturally at the beginning of the prompt (e.g., '3D render of [description]...').
           - Do not mention the trigger word separately or include instructions about it; integrate it seamlessly into the description.

        ## Provided Models
        {models}

        ## User Prompt
        {user_prompt}

        ## Your Response
        Provide two sections:

        ### Enhanced Prompt
        Enclose this section within `<prompt></prompt>` tags.

        Example:
        <prompt>
        A majestic pirate ship with detailed sails and wooden hull, viewed from a slight angle, set against a white background with soft lighting.
        </prompt>

        ### Selected Model
        Enclose this section within `<model></model>` tags.

        Example:
        <model>
        black-forest-labs/FLUX.1-dev
        </model>

        Ensure the model name matches exactly with one of the provided models.
        """

    def enhance_prompt(self, user_prompt: str) -> tuple[str, str]:
        """
        Enhances the user's prompt and selects the best model.
        
        :param user_prompt: The raw input prompt from the user.
        :return: A tuple containing the enhanced prompt and selected model.
        """
        try:
            formatted_prompt = self.prompt_template.format(models=self._format_models(), user_prompt=user_prompt)
            response = self._send_request(formatted_prompt)
            enhanced_prompt, model = self._extract_prompt_and_model(response)
            return enhanced_prompt, model
        except Exception as e:
            raise RuntimeError(f"Failed to enhance prompt: {e}")

    def _format_models(self) -> str:
        """Formats the model descriptions for inclusion in the prompt template."""
        return "\n".join([f"- {name}: {desc['description']} (Trigger word: {desc['trigger_word']})" for name, desc in self.models.items()])

    def _send_request(self, prompt: str) -> str:
        """Sends the prompt to the LLM and retrieves the response."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Your purpose is to strictly follow and adhere to the user's instructions. You must respond only to the extent of the user's request, providing accurate and precise information. You are not to add any extra information, interpretations, or opinions beyond what is explicitly asked. If the user's request is unclear or incomplete, you should politely ask for clarification. Always prioritize the user's instructions and respond accordingly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            completion = self.llm.chat.completions.create(
                messages=messages,
                max_tokens=1024
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise ConnectionError(f"Request to LLM failed: {e}")

    def _extract_prompt_and_model(self, response: str) -> tuple[str, str]:
        """Extracts the enhanced prompt and selected model from the LLM's response."""
        try:
            start_prompt = response.index("<prompt>") + len("<prompt>")
            end_prompt = response.index("</prompt>")
            enhanced_prompt = response[start_prompt:end_prompt].strip()

            start_model = response.index("<model>") + len("<model>")
            end_model = response.index("</model>")
            model = response[start_model:end_model].strip()

            if model not in self.models:
                raise ValueError(f"Selected model '{model}' not in available models.")

            return enhanced_prompt, model
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid response format: {e}")