"""Type definitions for models."""

from enum import Enum

class ModelType(Enum):
    """Available model types."""
    GPT35 = "gpt-3.5-turbo"
    GPT4 = "gpt-4"
    LOCAL = "local"