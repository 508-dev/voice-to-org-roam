"""Factory for creating text processing models."""

from typing import Optional
from .base_model import BaseModel
from .openai_model import OpenAIModel
from .local_model import LocalModel
from .types import ModelType

def create_model(model_type: ModelType, api_key: Optional[str] = None) -> BaseModel:
    """Create a model instance of the specified type."""
    if model_type in (ModelType.GPT35, ModelType.GPT4):
        if not api_key:
            raise ValueError("API key required for OpenAI models")
        return OpenAIModel(api_key, model_type)
    elif model_type == ModelType.LOCAL:
        return LocalModel()
    else:
        raise ValueError(f"Unknown model type: {model_type}")