"""
Gemini Client Configuration

This module provides a centralized Gemini client configuration
using the latest Google GenAI SDK.
"""

import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini client with API key from environment
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1beta"}
)

def generate_text(prompt: str, model: str = "gemini-2.0-flash") -> str:
    """
    Generate text using Gemini model
    
    Args:
        prompt: The input prompt for generation
        model: Model to use (default: gemini-2.0-flash)
    
    Returns:
        Generated text or error message
    """
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating text: {str(e)}"

def get_client():
    """
    Get the configured Gemini client instance
    
    Returns:
        Configured genai.Client instance
    """
    return client
