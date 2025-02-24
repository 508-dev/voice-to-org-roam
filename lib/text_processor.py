#!/usr/bin/env python3
"""Text processor for converting raw input into well-formatted org-mode content."""

import logging
import asyncio
from datetime import datetime
from typing import Optional, TypeVar, Type, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from models.base_model import BaseModel
from models.openai_model import OpenAIModel
from models.local_model import LocalModel
from models.model_factory import create_model, ModelType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Custom exception for text processing errors."""
    pass

@dataclass
class ProcessingConfig:
    """Configuration for text processing."""
    model_type: ModelType = ModelType.GPT35
    model_params: Dict[str, Any] = field(default_factory=dict)
    enable_linking: bool = True
    extract_tags: bool = True
    default_tags: list[str] = field(default_factory=list)

@dataclass
class ProcessedText:
    """Container for processed text and metadata."""
    content: str
    title: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

class TextProcessor:
    """Processes raw text input into formatted org-mode content."""

    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Initialize the text processor with configuration.

        Args:
            config: Optional ProcessingConfig object
        """
        self.config = config or ProcessingConfig()
        try:
            self.model = create_model(
                self.config.model_type,
                **self.config.model_params
            )
            logger.info(f"Initialized TextProcessor with {self.config.model_type}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise ProcessingError(f"Model initialization failed: {str(e)}")

    async def process_meeting_notes(self, raw_text: str) -> ProcessedText:
        """Process raw meeting notes into structured org-mode format.

        Args:
            raw_text: The raw text input from voice transcription

        Returns:
            ProcessedText object containing formatted content and metadata
        """
        try:
            # Format the system prompt for meeting notes
            system_prompt = """
            Convert the following meeting notes into org-mode format.
            Include:
            - Appropriate headers and structure
            - Timestamps for key points
            - Any action items or TODOs
            - Proper org syntax
            - Extract any proper nouns as [[id:placeholder][Name]] links
            - Identify and tag key topics
            """

            formatted_text = await self.model.process_text(raw_text, system_prompt)

            # Add timestamp header
            timestamp = self.format_timestamp()
            content = f"* Meeting Notes {timestamp}\n{formatted_text}"

            # Extract tags including default ones
            tags = self._extract_tags(formatted_text)
            tags.extend(["meeting"] + self.config.default_tags)

            return ProcessedText(
                content=content,
                tags=list(set(tags)),  # Deduplicate tags
                properties={
                    "CATEGORY": "meetings",
                    "CREATED": timestamp
                }
            )

        except Exception as e:
            error_msg = f"Error processing meeting notes: {str(e)}"
            logger.error(error_msg)
            return ProcessedText(
                content=raw_text,
                tags=["meeting", "error"],
                error=error_msg
            )

    async def process_general_notes(self, raw_text: str, context: Optional[str] = None) -> ProcessedText:
        """Process general notes into org-mode format with optional context.

        Args:
            raw_text: The raw text input from voice transcription
            context: Optional context about the note (type, related topics, etc.)

        Returns:
            ProcessedText object containing formatted content and metadata
        """
        try:
            # Format system prompt for general notes
            system_prompt = """
            Convert the following notes into org-mode format.
            - Use appropriate headers and structure
            - Identify and format any links to other notes
            - Extract key concepts and create org-roam style links
            - Maintain any existing org-roam links
            """

            if context:
                system_prompt += f"\nContext: {context}"

            formatted_text = await self.model.process_text(raw_text, system_prompt)

            # Extract potential title from first line
            first_line = formatted_text.split('\n')[0]
            title = first_line.lstrip('*# ').strip()

            return ProcessedText(
                content=formatted_text,
                title=title,
                tags=self._extract_tags(formatted_text)
            )

        except Exception as e:
            logger.error(f"Error processing general notes: {str(e)}")
            raise

    def _extract_tags(self, text: str) -> list[str]:
        """Extract org-mode tags from text content.

        Args:
            text: The formatted org-mode text

        Returns:
            List of extracted tags
        """
        tags = []
        for line in text.split('\n'):
            if line.startswith(':FILETAGS:'):
                tags.extend(tag.strip() for tag in line.split(':')[2:-1])
        return tags

    @staticmethod
    def format_timestamp(dt: Optional[datetime] = None) -> str:
        """Format a datetime into org-mode timestamp.

        Args:
            dt: Optional datetime object, uses current time if None

        Returns:
            Formatted org-mode timestamp string
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("<%Y-%m-%d %a %H:%M>")

