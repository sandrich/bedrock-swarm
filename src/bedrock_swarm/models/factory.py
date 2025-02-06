"""Factory for creating Bedrock model implementations."""

from typing import Dict, Type

from .base import BedrockModel
from .claude import Claude35Model


class ModelFactory:
    """Factory for creating Bedrock model implementations.

    This class handles the creation of appropriate model implementations
    based on the model ID. It maintains a registry of supported models
    and their implementations.
    """

    # Registry of supported models and their implementations
    _model_registry: Dict[str, Dict[str, Type[BedrockModel]]] = {
        "us.anthropic.claude-3-5-sonnet": {
            "20241022-v2:0": Claude35Model,
        }
    }

    @classmethod
    def create_model(cls, model_id: str) -> BedrockModel:
        """Create a model implementation for the given model ID.

        Args:
            model_id: The Bedrock model ID

        Returns:
            An instance of the appropriate model implementation

        Raises:
            InvalidModelError: If the model ID is not supported
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

        # Create and return model instance
        return family_registry[version]()

    @classmethod
    def register_model(
        cls, family: str, version: str, model_class: Type[BedrockModel]
    ) -> None:
        """Register a new model implementation.

        Args:
            family: Model family (e.g., "us.anthropic.claude-3-5-sonnet")
            version: Model version (e.g., "20241022-v2:0")
            model_class: Model implementation class
        """
        if family not in cls._model_registry:
            cls._model_registry[family] = {}
        cls._model_registry[family][version] = model_class

    @classmethod
    def get_supported_models(cls) -> Dict[str, Dict[str, Type[BedrockModel]]]:
        """Get all supported models.

        Returns:
            Dictionary of supported model families and their versions
        """
        return cls._model_registry.copy()
