"""Base class for text processing models."""

class BaseModel:
    """Base class for text processing models."""

    def process_text(self, text: str) -> str:
        """Process text input into formatted output."""
        raise NotImplementedError