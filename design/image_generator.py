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
    DALL_E_3 = "dall-e-3"


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
        # ✅ Réel — Read API keys from environment variables with explicit naming
        self.api_keys = api_keys or {
            "flux": os.environ.get("FLUX_API_KEY", ""),
            "stability": os.environ.get("STABILITY_API_KEY", ""),
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "replicate": os.environ.get("REPLICATE_API_TOKEN", ""),
        }
        self.output_dir = Path("design/assets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ollama_client = None
        # ✅ Réel — Cache for diffusers pipelines to avoid reloading
        self._diffusers_pipeline = None
        self._diffusers_model_id = None

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
            elif request.model == ImageModel.DALL_E_3:
                result = await self._generate_via_api(request, enhanced_prompt, "dall-e-3")
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
                    # ✅ Réel — Ollama Python client API call
                    response = await client.generate(
                        model="z-image-turbo",
                        prompt=prompt,
                    )
                    if hasattr(response, 'images') and response.images:
                        img_data = base64.b64decode(response.images[0])
                        filename = f"{request.filename_prefix}_{i}_{int(asyncio.get_event_loop().time())}.png"
                        filepath = self.output_dir / filename
                        filepath.write_bytes(img_data)  # ✅ Réel — Écrit le fichier sur disque
                        generated_paths.append(str(filepath))
                    elif hasattr(response, 'response'):
                        # Text response instead of image - model doesn't support image gen
                        logger.warning(f"Model returned text instead of image: {response.response[:100]}")
                else:
                    # ✅ Réel — Ollama HTTP API fallback
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        payload = {
                            "model": "z-image-turbo",
                            "prompt": prompt,
                            "stream": False,
                        }
                        if request.seed is not None:
                            payload["options"] = {"seed": request.seed}

                        # ✅ Réel — POST to Ollama /api/generate endpoint
                        async with session.post(
                            f"{self.ollama_host}/api/generate",
                            json=payload
                        ) as resp:
                            if resp.status != 200:
                                error_text = await resp.text()
                                logger.error(f"Ollama API error (HTTP {resp.status}): {error_text[:200]}")
                                continue
                            data = await resp.json()
                            if "images" in data and data["images"]:
                                img_data = base64.b64decode(data["images"][0])
                                filename = f"{request.filename_prefix}_{i}_{int(asyncio.get_event_loop().time())}.png"
                                filepath = self.output_dir / filename
                                filepath.write_bytes(img_data)  # ✅ Réel — Écrit le fichier sur disque
                                generated_paths.append(str(filepath))
                            elif "error" in data:
                                logger.error(f"Ollama error: {data['error']}")
                            else:
                                logger.warning(f"Ollama returned no images. Keys: {list(data.keys())}")
            except Exception as e:
                logger.error(f"Failed to generate image {i}: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used="z-image-turbo",
            prompt=prompt,
        )

    async def _generate_via_api(self, request: GenerationRequest, prompt: str, model: str) -> GenerationResult:
        """Generate image using real external API endpoints."""
        import aiohttp
        import time as _time
        generated_paths = []

        # ── Route to the correct real API based on model ──
        if model == "flux-1-pro":
            result = await self._generate_via_together(request, prompt, model="black-forest-labs/FLUX.1-pro")
            return result
        elif model == "flux-2":
            # ✅ Réel — FLUX.2 via Together AI
            result = await self._generate_via_together(request, prompt, model="black-forest-labs/FLUX.2-dev")
            return result
        elif model == "sd3":
            result = await self._generate_via_stability(request, prompt)
            return result
        elif model == "dall-e-3":
            result = await self._generate_via_openai(request, prompt)
            return result
        else:
            logger.warning(f"Unknown API model: {model}. Falling back to Ollama.")
            return await self._generate_via_ollama(request, prompt)

    async def _generate_via_together(self, request: GenerationRequest, prompt: str, model: str) -> GenerationResult:
        """✅ Réel — Generate image via Together AI API (FLUX.1 Pro / FLUX.2)."""
        import aiohttp
        import time as _time
        generated_paths = []

        api_key = self.api_keys.get("flux", "") or os.environ.get("TOGETHER_API_KEY", "")
        if not api_key:
            logger.warning("⚠️ Together AI (FLUX) non configuré. Utilisez le Settings pour configurer les tokens.")
            return await self._generate_via_ollama(request, prompt)

        try:
            async with aiohttp.ClientSession() as session:
                # ✅ Réel — Together AI /v1/images/generations endpoint
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "width": request.size.dimensions[0],
                    "height": request.size.dimensions[1],
                    "n": request.num_images,
                    "response_format": "b64_json",
                }
                if request.seed is not None:
                    payload["seed"] = request.seed

                async with session.post(
                    "https://api.together.xyz/v1/images/generations",
                    json=payload,
                    headers=headers
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Together AI API error (HTTP {resp.status}): {error_text[:300]}")
                        return GenerationResult(
                            images=[], model_used=model, prompt=prompt,
                            metadata={"error": f"Together AI HTTP {resp.status}: {error_text[:200]}"}
                        )
                    data = await resp.json()
                    # ✅ Réel — Decode base64 response and save to disk
                    for i, img_entry in enumerate(data.get("data", [])):
                        b64_str = img_entry.get("b64_json", "")
                        if not b64_str:
                            # Some responses may use url instead
                            img_url = img_entry.get("url", "")
                            if img_url:
                                async with session.get(img_url) as img_resp:
                                    if img_resp.status == 200:
                                        img_bytes = await img_resp.read()
                                        filename = f"{request.filename_prefix}_{i}_{int(_time.time())}.png"
                                        filepath = self.output_dir / filename
                                        filepath.write_bytes(img_bytes)  # ✅ Réel — Sauvegarde sur disque
                                        generated_paths.append(str(filepath))
                            continue
                        img_data = base64.b64decode(b64_str)
                        filename = f"{request.filename_prefix}_{i}_{int(_time.time())}.png"
                        filepath = self.output_dir / filename
                        filepath.write_bytes(img_data)  # ✅ Réel — Sauvegarde sur disque
                        generated_paths.append(str(filepath))
        except Exception as e:
            logger.error(f"Together AI image generation failed: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used=model,
            prompt=prompt,
        )

    async def _generate_via_stability(self, request: GenerationRequest, prompt: str) -> GenerationResult:
        """✅ Réel — Generate image via Stability AI API (Stable Diffusion 3)."""
        import aiohttp
        import time as _time
        generated_paths = []

        api_key = self.api_keys.get("stability", "")
        if not api_key:
            logger.warning("⚠️ Stability AI non configuré. Utilisez le Settings pour configurer les tokens.")
            return await self._generate_via_ollama(request, prompt)

        try:
            async with aiohttp.ClientSession() as session:
                # ✅ Réel — Stability AI v2beta /stable-image/generate/sd3 endpoint
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "image/*",
                }
                # Stability AI uses multipart/form-data for SD3
                form_data = aiohttp.FormData()
                form_data.add_field("prompt", prompt)
                form_data.add_field("output_format", "png")
                form_data.add_field("width", str(request.size.dimensions[0]))
                form_data.add_field("height", str(request.size.dimensions[1]))
                if request.negative_prompt:
                    form_data.add_field("negative_prompt", request.negative_prompt)
                if request.seed is not None:
                    form_data.add_field("seed", str(request.seed))

                async with session.post(
                    "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                    data=form_data,
                    headers=headers
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"Stability AI API error (HTTP {resp.status}): {error_text[:300]}")
                        return GenerationResult(
                            images=[], model_used="stable-diffusion-3", prompt=prompt,
                            metadata={"error": f"Stability AI HTTP {resp.status}: {error_text[:200]}"}
                        )
                    # ✅ Réel — Response is raw image bytes when Accept: image/*
                    img_bytes = await resp.read()
                    filename = f"{request.filename_prefix}_0_{int(_time.time())}.png"
                    filepath = self.output_dir / filename
                    filepath.write_bytes(img_bytes)  # ✅ Réel — Sauvegarde sur disque
                    generated_paths.append(str(filepath))
        except Exception as e:
            logger.error(f"Stability AI image generation failed: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used="stable-diffusion-3",
            prompt=prompt,
        )

    async def _generate_via_openai(self, request: GenerationRequest, prompt: str) -> GenerationResult:
        """✅ Réel — Generate image via OpenAI DALL-E API."""
        import aiohttp
        import time as _time
        generated_paths = []

        api_key = self.api_keys.get("openai", "")
        if not api_key:
            logger.warning("⚠️ OpenAI (DALL-E) non configuré. Utilisez le Settings pour configurer les tokens.")
            return await self._generate_via_ollama(request, prompt)

        try:
            async with aiohttp.ClientSession() as session:
                # ✅ Réel — OpenAI /v1/images/generations endpoint
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                # DALL-E 3 size must be one of: 1024x1024, 1024x1792, 1792x1024
                width, height = request.size.dimensions
                dall_e_sizes = [(1024, 1024), (1024, 1792), (1792, 1024)]
                # Pick the closest supported size
                closest = min(dall_e_sizes, key=lambda s: abs(s[0] - width) + abs(s[1] - height))
                size_str = f"{closest[0]}x{closest[1]}"

                payload = {
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": min(request.num_images, 1),  # DALL-E 3 only supports n=1
                    "size": size_str,
                    "quality": "hd" if request.quality >= 0.9 else "standard",
                    "response_format": "b64_json",
                }

                async with session.post(
                    "https://api.openai.com/v1/images/generations",
                    json=payload,
                    headers=headers
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        logger.error(f"OpenAI DALL-E API error (HTTP {resp.status}): {error_text[:300]}")
                        return GenerationResult(
                            images=[], model_used="dall-e-3", prompt=prompt,
                            metadata={"error": f"OpenAI HTTP {resp.status}: {error_text[:200]}"}
                        )
                    data = await resp.json()
                    # ✅ Réel — Decode base64 response and save to disk
                    for i, img_entry in enumerate(data.get("data", [])):
                        b64_str = img_entry.get("b64_json", "")
                        if b64_str:
                            img_data = base64.b64decode(b64_str)
                            filename = f"{request.filename_prefix}_{i}_{int(_time.time())}.png"
                            filepath = self.output_dir / filename
                            filepath.write_bytes(img_data)  # ✅ Réel — Sauvegarde sur disque
                            generated_paths.append(str(filepath))
                        else:
                            # URL-based response fallback
                            img_url = img_entry.get("url", "")
                            if img_url:
                                async with session.get(img_url) as img_resp:
                                    if img_resp.status == 200:
                                        img_bytes = await img_resp.read()
                                        filename = f"{request.filename_prefix}_{i}_{int(_time.time())}.png"
                                        filepath = self.output_dir / filename
                                        filepath.write_bytes(img_bytes)  # ✅ Réel — Sauvegarde sur disque
                                        generated_paths.append(str(filepath))
        except Exception as e:
            logger.error(f"OpenAI DALL-E image generation failed: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used="dall-e-3",
            prompt=prompt,
        )

    async def _generate_via_diffusers(self, request: GenerationRequest, prompt: str) -> GenerationResult:
        """✅ Réel — Generate image locally using the diffusers library."""
        import time as _time
        generated_paths = []

        try:
            from diffusers import StableDiffusionPipeline  # ✅ Réel — Import diffusers
        except ImportError:
            try:
                from diffusers import FluxPipeline as StableDiffusionPipeline  # ✅ Réel — Flux pipeline fallback
            except ImportError:
                logger.warning(
                    "⚠️ diffusers library not installed. Install with: pip install diffusers torch"
                )
                return GenerationResult(
                    images=[], model_used="diffusers-local", prompt=prompt,
                    metadata={"error": "diffusers library not installed"}
                )

        try:
            import torch  # ✅ Réel — PyTorch for GPU/CPU inference
        except ImportError:
            logger.warning(
                "⚠️ PyTorch not installed. Install with: pip install torch"
            )
            return GenerationResult(
                images=[], model_used="diffusers-local", prompt=prompt,
                metadata={"error": "PyTorch not installed"}
            )

        # Select model based on request
        if request.model == ImageModel.FLUX_1_PRO or request.model == ImageModel.FLUX_2:
            model_id = "black-forest-labs/FLUX.1-dev"
            try:
                from diffusers import FluxPipeline
                pipeline_cls = FluxPipeline
            except ImportError:
                logger.warning("FluxPipeline not available in diffusers. Falling back to StableDiffusion.")
                model_id = "stabilityai/stable-diffusion-3-medium"
                pipeline_cls = StableDiffusionPipeline
        elif request.model == ImageModel.STABLE_DIFFUSION_3:
            model_id = "stabilityai/stable-diffusion-3-medium"
            pipeline_cls = StableDiffusionPipeline
        else:
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            pipeline_cls = StableDiffusionPipeline

        # ✅ Réel — Load or reuse cached pipeline
        if self._diffusers_pipeline is None or self._diffusers_model_id != model_id:
            logger.info(f"Loading diffusers model: {model_id} (this may take a while on first run)")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            self._diffusers_pipeline = pipeline_cls.from_pretrained(
                model_id,
                torch_dtype=dtype,
            )
            self._diffusers_pipeline.to(device)  # ✅ Réel — Déplace le modèle sur GPU/CPU
            self._diffusers_model_id = model_id

        # ✅ Réel — Generate images with the pipeline
        for i in range(request.num_images):
            try:
                generator = None
                if request.seed is not None:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    generator = torch.Generator(device=device).manual_seed(request.seed + i)

                gen_kwargs = {
                    "prompt": prompt,
                    "num_inference_steps": 30 if request.quality >= 0.9 else 20,
                    "generator": generator,
                }
                if request.negative_prompt and hasattr(self._diffusers_pipeline, 'call_parameters'):
                    gen_kwargs["negative_prompt"] = request.negative_prompt

                image_result = self._diffusers_pipeline(**gen_kwargs)
                image = image_result.images[0]  # ✅ Réel — Image PIL obtenue du modèle

                filename = f"{request.filename_prefix}_{i}_{int(_time.time())}.png"
                filepath = self.output_dir / filename
                image.save(str(filepath))  # ✅ Réel — Sauvegarde l'image sur disque
                generated_paths.append(str(filepath))
            except Exception as e:
                logger.error(f"Diffusers failed for image {i}: {e}")

        return GenerationResult(
            images=generated_paths,
            model_used=f"diffusers/{model_id}",
            prompt=prompt,
        )

    async def generate_local(self, request: GenerationRequest) -> GenerationResult:
        """Generate image locally using diffusers (no API key needed)."""
        import time
        start_time = time.time()
        enhanced_prompt = self._build_prompt(request)
        logger.info(f"Generating image locally with diffusers: {enhanced_prompt[:100]}...")
        result = await self._generate_via_diffusers(request, enhanced_prompt)
        result.generation_time = time.time() - start_time
        return result

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
