"""
Luymas AI - Design Plugins System
Extensible plugin architecture for design capabilities
"""

import asyncio
import importlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger("luymas.design.plugins")


@dataclass
class DesignToken:
    """A single design token (color, font, spacing, etc.)."""
    name: str
    category: str  # color, typography, spacing, border, shadow
    value: str
    description: str = ""
    css_variable: str = ""  # e.g., --color-primary

    def to_css(self) -> str:
        """Convert to CSS custom property."""
        var_name = self.css_variable or f"--{self.category}-{self.name}".replace(" ", "-")
        return f"{var_name}: {self.value};"


@dataclass
class DesignSystem:
    """Complete design system with tokens and components."""
    name: str
    version: str = "1.0.0"
    tokens: List[DesignToken] = field(default_factory=list)
    components: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_css(self) -> str:
        """Export as CSS custom properties."""
        lines = [":root {"]
        for token in self.tokens:
            lines.append(f"  {token.to_css()}")
        lines.append("}")
        return "\n".join(lines)

    def to_json(self) -> str:
        """Export as JSON."""
        return json.dumps({
            "name": self.name,
            "version": self.version,
            "tokens": [
                {
                    "name": t.name,
                    "category": t.category,
                    "value": t.value,
                    "description": t.description,
                    "css_variable": t.css_variable,
                }
                for t in self.tokens
            ],
            "components": self.components,
            "metadata": self.metadata,
        }, indent=2)

    def to_tailwind(self) -> str:
        """Export as Tailwind CSS config."""
        colors = {}
        spacing = {}
        fonts = {}
        for token in self.tokens:
            if token.category == "color":
                colors[token.name] = token.value
            elif token.category == "spacing":
                spacing[token.name] = token.value
            elif token.category == "typography":
                fonts[token.name] = token.value

        config = {"theme": {"extend": {}}}
        if colors:
            config["theme"]["extend"]["colors"] = colors
        if spacing:
            config["theme"]["extend"]["spacing"] = spacing
        if fonts:
            config["theme"]["extend"]["fontFamily"] = fonts

        return json.dumps(config, indent=2)


class PluginInterface(ABC):
    """Base interface for design plugins."""

    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    @abstractmethod
    async def generate(self, context: Dict[str, Any]) -> List[DesignToken]:
        """Generate design tokens based on context."""
        pass

    @abstractmethod
    async def validate(self, tokens: List[DesignToken]) -> List[str]:
        """Validate generated tokens. Returns list of warnings."""
        pass

    def info(self) -> Dict[str, str]:
        """Return plugin info."""
        return {"name": self.name, "description": self.description, "version": self.version}


class ColorPalettePlugin(PluginInterface):
    """Generates color palettes based on mood, industry, or reference."""

    name = "color-palette"
    description = "Generates cohesive color palettes"
    version = "1.0.0"

    # Curated color palettes
    PALETTES = {
        "modern-tech": {
            "primary": "#6366f1",
            "secondary": "#8b5cf6",
            "accent": "#06b6d4",
            "background": "#0f172a",
            "surface": "#1e293b",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "error": "#ef4444",
        },
        "warm-professional": {
            "primary": "#d97706",
            "secondary": "#b45309",
            "accent": "#059669",
            "background": "#fefce8",
            "surface": "#fff7ed",
            "text": "#1c1917",
            "muted": "#78716c",
            "success": "#16a34a",
            "warning": "#ea580c",
            "error": "#dc2626",
        },
        "clean-minimal": {
            "primary": "#18181b",
            "secondary": "#52525b",
            "accent": "#10b981",
            "background": "#ffffff",
            "surface": "#f4f4f5",
            "text": "#09090b",
            "muted": "#a1a1aa",
            "success": "#22c55e",
            "warning": "#eab308",
            "error": "#ef4444",
        },
        "ocean-depth": {
            "primary": "#0284c7",
            "secondary": "#0369a1",
            "accent": "#2dd4bf",
            "background": "#0c4a6e",
            "surface": "#164e63",
            "text": "#ecfeff",
            "muted": "#67e8f9",
            "success": "#34d399",
            "warning": "#fbbf24",
            "error": "#f87171",
        },
        "sunset-warm": {
            "primary": "#e11d48",
            "secondary": "#be123c",
            "accent": "#f97316",
            "background": "#1c1917",
            "surface": "#292524",
            "text": "#fafaf9",
            "muted": "#a8a29e",
            "success": "#4ade80",
            "warning": "#fb923c",
            "error": "#f43f5e",
        },
    }

    async def generate(self, context: Dict[str, Any]) -> List[DesignToken]:
        """Generate color tokens."""
        palette_name = context.get("palette", "modern-tech")
        palette = self.PALETTES.get(palette_name, self.PALETTES["modern-tech"])

        tokens = []
        for color_name, hex_value in palette.items():
            tokens.append(DesignToken(
                name=color_name,
                category="color",
                value=hex_value,
                description=f"{color_name} color for {palette_name} palette",
                css_variable=f"--color-{color_name.replace('_', '-')}",
            ))
        return tokens

    async def validate(self, tokens: List[DesignToken]) -> List[str]:
        """Validate color tokens for accessibility."""
        warnings = []
        # Check contrast ratios would go here
        # Simplified: just check hex format
        for token in tokens:
            if token.category == "color" and not token.value.startswith("#"):
                warnings.append(f"Color {token.name} may not be a valid hex value: {token.value}")
        return warnings


class TypographyPlugin(PluginInterface):
    """Generates typography scales and font pairings."""

    name = "typography"
    description = "Generates typography scales and font pairings"
    version = "1.0.0"

    FONT_PAIRS = {
        "modern-sans": {
            "heading": "Inter, system-ui, sans-serif",
            "body": "Inter, system-ui, sans-serif",
            "mono": "JetBrains Mono, monospace",
        },
        "elegant-serif": {
            "heading": "Playfair Display, Georgia, serif",
            "body": "Source Sans 3, sans-serif",
            "mono": "Fira Code, monospace",
        },
        "geometric-sans": {
            "heading": "Space Grotesk, sans-serif",
            "body": "DM Sans, sans-serif",
            "mono": "Space Mono, monospace",
        },
    }

    TYPE_SCALES = {
        "major-third": [0.75, 0.875, 1, 1.25, 1.563, 1.953, 2.441, 3.052],
        "perfect-fourth": [0.75, 0.875, 1, 1.333, 1.777, 2.369, 3.157, 4.209],
        "golden-ratio": [0.75, 0.875, 1, 1.618, 2.618, 4.236, 6.854, 11.089],
    }

    async def generate(self, context: Dict[str, Any]) -> List[DesignToken]:
        """Generate typography tokens."""
        pair_name = context.get("font_pair", "modern-sans")
        scale_name = context.get("type_scale", "major-third")
        base_size = context.get("base_size", 16)

        fonts = self.FONT_PAIRS.get(pair_name, self.FONT_PAIRS["modern-sans"])
        scales = self.TYPE_SCALES.get(scale_name, self.TYPE_SCALES["major-third"])

        tokens = []

        # Font family tokens
        for font_type, font_stack in fonts.items():
            tokens.append(DesignToken(
                name=f"font-{font_type}",
                category="typography",
                value=font_stack,
                description=f"{font_type} font family",
                css_variable=f"--font-{font_type}",
            ))

        # Font size tokens
        size_names = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl"]
        for i, (name, scale) in enumerate(zip(size_names, scales)):
            size_px = round(base_size * scale, 2)
            tokens.append(DesignToken(
                name=f"text-{name}",
                category="typography",
                value=f"{size_px}px",
                description=f"Font size {name}",
                css_variable=f"--text-{name}",
            ))

        return tokens

    async def validate(self, tokens: List[DesignToken]) -> List[str]:
        """Validate typography tokens."""
        warnings = []
        for token in tokens:
            if token.category == "typography" and "font" in token.name:
                if not any(font in token.value for font in ["sans-serif", "serif", "monospace"]):
                    warnings.append(f"Font {token.name} missing generic fallback: {token.value}")
        return warnings


class LayoutPlugin(PluginInterface):
    """Generates layout tokens (spacing, breakpoints, containers)."""

    name = "layout"
    description = "Generates layout spacing scales and breakpoints"
    version = "1.0.0"

    async def generate(self, context: Dict[str, Any]) -> List[DesignToken]:
        """Generate layout tokens."""
        base_unit = context.get("base_unit", 4)  # px
        tokens = []

        # Spacing scale (0-128)
        spacing_values = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128]
        for val in spacing_values:
            tokens.append(DesignToken(
                name=f"spacing-{val}",
                category="spacing",
                value=f"{val * base_unit}px",
                description=f"Spacing {val}",
                css_variable=f"--spacing-{val}",
            ))

        # Breakpoints
        breakpoints = {
            "sm": "640px",
            "md": "768px",
            "lg": "1024px",
            "xl": "1280px",
            "2xl": "1536px",
        }
        for name, value in breakpoints.items():
            tokens.append(DesignToken(
                name=f"breakpoint-{name}",
                category="breakpoint",
                value=value,
                description=f"Breakpoint {name}",
                css_variable=f"--breakpoint-{name}",
            ))

        # Container widths
        containers = {
            "sm": "640px",
            "md": "768px",
            "lg": "1024px",
            "xl": "1280px",
        }
        for name, value in containers.items():
            tokens.append(DesignToken(
                name=f"container-{name}",
                category="container",
                value=value,
                description=f"Container max width {name}",
                css_variable=f"--container-{name}",
            ))

        # Border radius
        radii = {
            "none": "0px",
            "sm": "2px",
            "default": "4px",
            "md": "6px",
            "lg": "8px",
            "xl": "12px",
            "2xl": "16px",
            "full": "9999px",
        }
        for name, value in radii.items():
            tokens.append(DesignToken(
                name=f"radius-{name}",
                category="border",
                value=value,
                description=f"Border radius {name}",
                css_variable=f"--radius-{name}",
            ))

        return tokens

    async def validate(self, tokens: List[DesignToken]) -> List[str]:
        """Validate layout tokens."""
        return []


class IconGeneratorPlugin(PluginInterface):
    """Suggests icon styles and generates icon specifications."""

    name = "icon-generator"
    description = "Generates icon specifications and style guides"
    version = "1.0.0"

    async def generate(self, context: Dict[str, Any]) -> List[DesignToken]:
        """Generate icon-related tokens."""
        tokens = []

        # Icon sizes
        sizes = {"xs": "12px", "sm": "16px", "md": "20px", "lg": "24px", "xl": "32px", "2xl": "48px"}
        for name, value in sizes.items():
            tokens.append(DesignToken(
                name=f"icon-{name}",
                category="icon",
                value=value,
                description=f"Icon size {name}",
                css_variable=f"--icon-{name}",
            ))

        # Icon styles
        styles = {
            "icon-stroke-width": "2px",
            "icon-linecap": "round",
            "icon-linejoin": "round",
        }
        for name, value in styles.items():
            tokens.append(DesignToken(
                name=name,
                category="icon",
                value=value,
                description=f"Icon style {name}",
                css_variable=f"--{name}",
            ))

        return tokens

    async def validate(self, tokens: List[DesignToken]) -> List[str]:
        """Validate icon tokens."""
        return []


class PluginRegistry:
    """Registry for design plugins."""

    def __init__(self):
        self._plugins: Dict[str, PluginInterface] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        """Register built-in plugins."""
        for plugin_class in [ColorPalettePlugin, TypographyPlugin, LayoutPlugin, IconGeneratorPlugin]:
            plugin = plugin_class()
            self._plugins[plugin.name] = plugin

    def register(self, plugin: PluginInterface):
        """Register a plugin."""
        self._plugins[plugin.name] = plugin
        logger.info(f"Registered design plugin: {plugin.name}")

    def unregister(self, name: str):
        """Unregister a plugin."""
        if name in self._plugins:
            del self._plugins[name]

    def get(self, name: str) -> Optional[PluginInterface]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> List[Dict[str, str]]:
        """List all registered plugins."""
        return [plugin.info() for plugin in self._plugins.values()]

    async def generate_design_system(self, context: Dict[str, Any]) -> DesignSystem:
        """Generate a complete design system using all plugins."""
        all_tokens: List[DesignToken] = []

        for plugin in self._plugins.values():
            try:
                tokens = await plugin.generate(context)
                all_tokens.extend(tokens)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed: {e}")

        return DesignSystem(
            name=context.get("name", "luymas-design-system"),
            tokens=all_tokens,
            metadata={
                "generated_by": "Luymas Designer",
                "plugins_used": list(self._plugins.keys()),
                "context": context,
            },
        )
