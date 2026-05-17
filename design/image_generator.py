"""
Luymas AI - Image Generator Module
Generates images using FLUX.1 Pro, Stable Diffusion 3, or Z-Image Turbo
"""

import asyncio
import base64
import io
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("luymas.design.image_generator")


class ImageModel(Enum):
    """Available image generation models."""
    FLUX_1_PRO = "flux-1-pro"
    STABLE_DIFFUSION_3 = "stable-diffusion-3"
    Z_IMAGE_TURBO = "z-image-turbo"
    FLUX_2 = "flux-2"


class ImageSize(Enum):
    """Preset image sizes."""
    ICON = (64, 64)
    THUMBNAIL = (256, 256)
    CARD = (512, 512)
    BANNER = (1024, 256)
    HERO = (1024, 512)
    FULL_HD = (1920, 1080)
    SQUARE = (1024, 1024)
    PORTRAIT = (768, 1024)

    @property
    def dimensions(self) -> Tuple[int, int]:
        return self.value


class ImageStyle(Enum):
    """Style presets for image generation."""
    PHOTO_REALISTIC = "photorealistic"
    ILLUSTRATION = "illustration"
    MINIMALIST = "minimalist"
    FLAT_DESIGN = "flat-design"
    GRADIENT = "gradient"
    ISOMETRIC = "isometric"
    NEUMORPHIC = "neumorphic"
    GLASSMORPHISM = "glassmorphism"
    RETRO = "retro"
    FUTURISTIC = "futuristic"


@dataclass
class GenerationRequest:
    """Request for image generation."""
    prompt: str
    negative_prompt: str = ""
    model: ImageModel = ImageModel.Z_IMAGE_TURBO
    size: ImageSize = ImageSize.CARD
    style: Optional[ImageStyle] = None
    num_images: int = 1
    seed: Optional[int] = None
    quality: float = 0.9  # 0.0 to 1.0
    output_dir: str = "design/assets"
    filename_prefix: str = "luymas"


@dataclass
class GenerationResult:
    """Result of image generation."""
    images: List[str] = field(default_factory=list)  # paths to generated images
    model_used: str = ""
    prompt: str = ""
    generation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ImageGenerator:
    """
    Generates images using local or API-based models.
    Supports FLUX.1 Pro, Stable Diffusion 3, and Z-Image Turbo via Ollama.
    """

    def __init__(self, ollama_host: str = "http://localhost:11434", api_keys: Optional[Dict[str, str]] = None):
        self.ollama_host = ollama_host
        self.api_keys = api_keys or {}
        self.output_dir = Path("design/assets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ollama_client = None

    async def _get_ollama_client(self):
        """Get or create Ollama client."""
        if self._ollama_client is None:
            try:
                import ollama
                self._ollama_client = ollama.AsyncClient(host=self.ollama_host)
            except ImportError:
                logger.warning("Ollama Python client not installed. Falling back to HTTP.")
                self._ollama_client = None
        return self._ollama_client

    def _build_prompt(self, request: GenerationRequest) -> str:
        """Build enhanced prompt with style and quality modifiers."""
        prompt_parts = [request.prompt]

        if request.style:
            style_modifiers = {
                ImageStyle.PHOTO_REALISTIC: "photorealistic, 8k, detailed, professional photography",
                ImageStyle.ILLUSTRATION: "digital illustration, artistic, creative, detailed",
                ImageStyle.MINIMALIST: "minimalist, clean, simple, elegant, white space",
                ImageStyle.FLAT_DESIGN: "flat design, no gradients, solid colors, modern",
                ImageStyle.GRADIENT: "gradient colors, smooth transitions, modern, vibrant",
                ImageStyle.ISOMETRIC: "isometric view, 3D perspective, clean lines",
                ImageStyle.NEUMORPHIC: "neumorphic design, soft shadows, embossed",
                ImageStyle.GLASSMORPHISM: "glassmorphism, frosted glass, blur, transparent",
                ImageStyle.RETRO: "retro style, vintage colors, nostalgic",
                ImageStyle.FUTURISTIC: "futuristic, cyberpunk, neon, high-tech",
            }
            modifier = style_modifiers.get(request.style, "")
            if modifier:
                prompt_parts.append(modifier)

        # Add quality modifier
        if request.quality >= 0.9:
            prompt_parts.append("masterpiece, best quality, highly detailed")
        elif request.quality >= 0.7:
            prompt_parts.append("high quality, detailed")

        return ", ".join(prompt_parts)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate image(s) based on request."""
        import time
        start_time = time.time()

        enhanced_prompt = self._build_prompt(request)
        logger.info(f"Generating image with {request.model.value}: {enhanced_prompt[:100]}...")

        try:
            if request.model == ImageModel.Z_IMAGE_TURBO:
                result = await self._generate_via_ollama(request, enhanced_prompt)
            elif request.model == ImageModel.FLUX_1_PRO:
                result = await self._generate_via_api(request, enhanced_prompt, "flux-1-pro")
            elif request.model == ImageModel.STABLE_DIFFUSION_3:
                result = await self._generate_via_api(request, enhanced_prompt, "sd3")
            elif request.model == ImageModel.FLUX_2:
                result = await self._generate_via_api(request, enhanced_prompt, "flux-2")
            else:
                result = await self._generate_via_ollama(request, enhanced_prompt)
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            result = GenerationResult(
                model_used=request.model.value,
                prompt=enhanced_prompt,
                metadata={"error": str(e)}
            )

        result.generation_time = time.time() - start_time
        return result

    async def _generate_via_ollama(self, request: GenerationRequest, prompt: str) -> GenerationResult:
        """Generate image using Ollama's image generation capability."""
        client = await self._get_ollama_client()
        generated_paths = []

        for i in range(request.num_images):
            try:
                if client:
                    response = await client.generate(
                        model="z-image-turbo",
                        prompt=prompt,
                    )
                    if hasattr(response, 'images') and response.images:
                        img_data = base64.b64decode(response.images[0])
                        filename = f"{request.filename_prefix}_{i}_{int(asyncio.get_event_loop().time())}.png"
                        filepath = self.output_dir / filename
                        filepath.write_bytes(img_data)
                        generated_paths.append(str(filepath))
                    elif hasattr(response, 'response'):
                        # Text response instead of image - model doesn't support image gen
                        logger.warning(f"Model returned text instead of image: {response.response[:100]}")
                else:
                    # Fallback to HTTP request
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "model": "z-image-turbo",
                            "prompt": prompt,
                            "stream": False,
                        }
                        if request.seed is not None:
                            payload["seed"] = request.seed

                        async with session.post(
                            f"{self.ollama_host}/api/generate",
                            json=payload
                        ) as resp:
                            data = await resp.json()
                            if "images" in data and data["images"]:
                                img_data = base64.b64decode(data["images"][0])
                                filename = f"{request.filename_prefix}_{i}_{int(asyncio.get_event_loop().time())}.png"
                                filepath = self.output_dir / filename
                                filepath.write_bytes(img_data)
                                generated_paths.append(str(filepath))
            except Exception as e:
                logger.error(f"Failed to generate image {i}: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used="z-image-turbo",
            prompt=prompt,
        )

    async def _generate_via_api(self, request: GenerationRequest, prompt: str, model: str) -> GenerationResult:
        """Generate image using external API (fallback)."""
        import aiohttp
        generated_paths = []

        # Check for API key
        api_key = self.api_keys.get(model, self.api_keys.get("default", ""))
        if not api_key:
            logger.warning(f"No API key for {model}. Falling back to Ollama.")
            return await self._generate_via_ollama(request, prompt)

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {api_key}"}
                payload = {
                    "prompt": prompt,
                    "negative_prompt": request.negative_prompt,
                    "width": request.size.dimensions[0],
                    "height": request.size.dimensions[1],
                    "num_images": request.num_images,
                }
                if request.seed is not None:
                    payload["seed"] = request.seed

                # This would connect to an actual API endpoint
                # Placeholder for FLUX.1 Pro / SD3 API integration
                async with session.post(
                    "https://api.example.com/v1/images/generate",
                    json=payload,
                    headers=headers
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for i, img_data in enumerate(data.get("images", [])):
                            filename = f"{request.filename_prefix}_{i}_{int(asyncio.get_event_loop().time())}.png"
                            filepath = self.output_dir / filename
                            if isinstance(img_data, str):
                                filepath.write_bytes(base64.b64decode(img_data))
                            generated_paths.append(str(filepath))
        except Exception as e:
            logger.error(f"API image generation failed: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used=model,
            prompt=prompt,
        )

    async def generate_batch(self, prompts: List[str], **kwargs) -> List[GenerationResult]:
        """Generate multiple images in batch."""
        tasks = []
        for prompt in prompts:
            request = GenerationRequest(prompt=prompt, **kwargs)
            tasks.append(self.generate(request))
        return await asyncio.gather(*tasks)

    async def generate_design_assets(self, project_name: str, style: ImageStyle = ImageStyle.FLAT_DESIGN) -> Dict[str, GenerationResult]:
        """Generate a complete set of design assets for a project."""
        assets = {}
        
        # Logo
        logo_request = GenerationRequest(
            prompt=f"Logo for {project_name}, professional, clean, modern",
            model=ImageModel.Z_IMAGE_TURBO,
            size=ImageSize.SQUARE,
            style=style,
            filename_prefix=f"{project_name}_logo",
        )
        assets["logo"] = await self.generate(logo_request)

        # Hero image
        hero_request = GenerationRequest(
            prompt=f"Hero banner for {project_name}, technology, innovation",
            model=ImageModel.Z_IMAGE_TURBO,
            size=ImageSize.HERO,
            style=style,
            filename_prefix=f"{project_name}_hero",
        )
        assets["hero"] = await self.generate(hero_request)

        # Favicon
        favicon_request = GenerationRequest(
            prompt=f"Favicon icon for {project_name}, simple, recognizable",
            model=ImageModel.Z_IMAGE_TURBO,
            size=ImageSize.ICON,
            style=style,
            filename_prefix=f"{project_name}_favicon",
        )
        assets["favicon"] = await self.generate(favicon_request)

        return assets

    def list_generated_images(self) -> List[str]:
        """List all generated images in the output directory."""
        return [str(p) for p in self.output_dir.glob("*.png")]
