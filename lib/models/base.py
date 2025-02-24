from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ModelConfig:
    """Configuration parameters for AI models.

    Attributes:
        max_tokens: Maximum tokens to generate in response
        temperature: Controls randomness in generation (0.0-1.0)
        model_path: Optional path for local models
        api_key: Optional API key for cloud models
        extra_params: Additional model-specific parameters
    """
    max_tokens: int = 1000
    temperature: float = 0.7
    model_path: Optional[str] = None
    api_key: Optional[str] = None
    extra_params: Dict[str, Any] = None

class BaseModel(ABC):
    """Abstract base class defining the interface for AI text processing models.

    This class establishes the contract that all model implementations must follow.
    Subclasses should implement the core text processing functionality while
    inheriting common configuration and validation logic.
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize the model with optional configuration.

        Args:
            config: Model configuration parameters. If None, uses defaults.
        """
        self.config = config or ModelConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the model configuration.

        Raises:
            ValueError: If configuration parameters are invalid.
        """
        if self.config.temperature < 0.0 or self.config.temperature > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        if self.config.max_tokens < 1:
            raise ValueError("max_tokens must be positive")

    @abstractmethod
    async def process_text(
        self,
        raw_text: str,
        system_prompt: str
    ) -> str:
        """Process raw text input using the AI model.

        This method should be implemented by concrete model classes to perform
        the actual text processing using their specific AI backend.

        Args:
            raw_text: The input text to process
            system_prompt: Instructions for how to process the text

        Returns:
            The processed text output

        Raises:
            Exception: If text processing fails
        """
        pass
