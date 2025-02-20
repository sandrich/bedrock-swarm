"""Factory for creating Bedrock model implementations."""

from typing import Any, Dict, Type

from .base import BedrockModel
from .claude import ClaudeModel
from .titan import TitanModel

# Registry of supported models, their implementations, and configurations
BEDROCK_MODEL_REGISTRY = {
    "us.anthropic.claude-3-5-sonnet": {
        "20241022-v2:0": {
            "class": ClaudeModel,
            "config": {
                "max_tokens": 200000,  # Claude 3 Sonnet context window
                "default_tokens": 4096,
            },
        }
    },
    "amazon.titan-text-express": {
        "v1": {
            "class": TitanModel,
            "config": {
                "max_tokens": 8000,  # Maximum context window
                "default_tokens": 2048,  # Default response length
            },
        }
    },
    "amazon.titan-text-lite": {
        "v1": {
            "class": TitanModel,
            "config": {
                "max_tokens": 4000,
                "default_tokens": 2048,
            },
        }
    },
    "amazon.titan-text-premier": {
        "v1:0": {
            "class": TitanModel,
            "config": {
                "max_tokens": 3072,  # As per validation error encountered
                "default_tokens": 2048,
            },
        }
    },
}


class ModelFactory:
    """Factory for creating Bedrock model implementations."""

    _model_registry = BEDROCK_MODEL_REGISTRY

    @classmethod
    def create_model(cls, model_id: str) -> BedrockModel:
        """Create a model implementation for the given model ID.

        Args:
            model_id: The Bedrock model ID

        Returns:
            An instance of the appropriate model implementation

        Raises:
            ValueError: If the model ID is not supported
        """
        # Find matching model family
        family = next(
            (f for f in cls._model_registry.keys() if model_id.startswith(f)), None
        )

        if not family:
            supported = ", ".join(cls._model_registry.keys())
            raise ValueError(
                f"Unsupported model family. Model ID must start with one of: {supported}"
            )

        # Extract version (everything after the family name and a hyphen)
        version = model_id[len(family) + 1 :]

        # Get model implementation
        family_registry = cls._model_registry[family]
        if version not in family_registry:
            versions = ", ".join(family_registry.keys())
            raise ValueError(
                f"Unsupported version '{version}' for model family '{family}'. "
                f"Supported versions: {versions}"
            )

        # Create model instance with its configuration
        model_info = family_registry[version]
        model = model_info["class"](model_id)
        model.set_config(model_info["config"])
        return model

    @classmethod
    def register_model(
        cls,
        family: str,
        version: str,
        model_class: Type[BedrockModel],
        config: Dict[str, Any],
    ) -> None:
        """Register a new model implementation.

        Args:
            family: Model family (e.g., "us.anthropic.claude-3-5-sonnet")
            version: Model version (e.g., "20241022-v2:0")
            model_class: Model implementation class
            config: Model configuration (max_tokens, default_tokens, etc.)
        """
        if family not in cls._model_registry:
            cls._model_registry[family] = {}
        cls._model_registry[family][version] = {"class": model_class, "config": config}

    @classmethod
    def get_supported_models(cls) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Get all supported models.

        Returns:
            Dictionary of supported model families, versions, and their configurations
        """
        return cls._model_registry.copy()
