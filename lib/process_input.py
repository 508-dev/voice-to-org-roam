#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from typing import Optional, Tuple
from text_processor import TextProcessor
from models.types import ModelType
from models.model_factory import create_model
import re

def get_api_key() -> Optional[str]:
    """Get OpenAI API key from environment or config file."""
    # First try environment variable
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        return api_key

    # Then try config file in home directory
    config_path = Path.home() / '.config' / 'voice-to-org' / 'openai.key'
    if config_path.exists():
        return config_path.read_text().strip()

    return None

def process_text(text: str, note_type: str = 'general') -> str:
    """Process raw text input into formatted org-mode content."""
    # Try to use OpenAI if API key is available, otherwise fall back to local
    api_key = get_api_key()
    model_type = ModelType.GPT35 if api_key else ModelType.LOCAL

    try:
        model = create_model(model_type, api_key)
        processor = TextProcessor(model)

        if note_type == 'meeting':
            return processor.format_meeting_notes(text)
        return processor.format_general_notes(text)
    except Exception as e:
        print(f"Error in text processing: {e}", file=sys.stderr)
        # Fall back to simple formatting
        return f"* {text}"

def extract_links(text: str) -> Tuple[str, list]:
    """
    Extract potential org-roam links from text and format them.
    Returns the processed text and a list of link candidates.
    """
    # Look for potential entity names that should be links
    # This is a basic implementation - you might want to use NLP for better detection
    words = text.split()
    link_candidates = []

    # Convert appropriate words/phrases to org-roam links
    processed_words = []
    i = 0
    while i < len(words):
        # Check for multi-word proper nouns
        current_phrase = words[i]
        if current_phrase[0].isupper():
            j = i + 1
            while j < len(words) and words[j][0].isupper():
                current_phrase += " " + words[j]
                j += 1

            if j > i + 1:  # Multi-word proper noun found
                link_candidates.append(current_phrase)
                processed_words.append(f"[[{current_phrase}]]")
                i = j
                continue

        # Single proper nouns and known entities
        if words[i][0].isupper():
            link_candidates.append(words[i])
            processed_words.append(f"[[{words[i]}]]")
        else:
            processed_words.append(words[i])
        i += 1

    return " ".join(processed_words), link_candidates

def format_for_daily(text: str) -> str:
    """Format text for a daily note entry."""
    processed_text, _ = extract_links(text)
    # Add a timestamp and heading
    timestamp = "** %<%Y-%m-%d %H:%M>"
    return f"{timestamp}\n{processed_text}"

def format_for_note(text: str) -> str:
    """Format text for a regular note entry."""
    processed_text, _ = extract_links(text)
    return processed_text

def main():
    if len(sys.argv) != 3:
        print("Usage: process_input.py <note_type> <content>", file=sys.stderr)
        sys.exit(1)

    note_type = sys.argv[1]
    content = sys.argv[2]

    if note_type == "daily":
        print(format_for_daily(content))
    else:
        print(format_for_note(content))

if __name__ == "__main__":
    main()

