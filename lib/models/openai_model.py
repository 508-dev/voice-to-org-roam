"""OpenAI-based text processing model."""

from typing import Optional
import openai
from .base_model import BaseModel
from .types import ModelType

class OpenAIModel(BaseModel):
    """OpenAI-based text processing model."""

    def __init__(self, api_key: str, model_type: ModelType = ModelType.GPT35):
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_type.value

    def process_text(self, text: str) -> str:
        """Process text using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats text into org-mode notes."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content

