"""Local text processing model."""

from .base_model import BaseModel

class LocalModel(BaseModel):
    """Simple local text processing model."""

    def process_text(self, text: str) -> str:
        """Process text locally with simple formatting."""
        lines = text.split('. ')
        formatted = []

        for line in lines:
            if line:
                formatted.append(f"* {line.strip()}")

        return '\n'.join(formatted)

