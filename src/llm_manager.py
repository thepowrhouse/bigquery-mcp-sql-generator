#!/usr/bin/env python3
"""
LLM Manager that provides a unified interface for different LLM providers
Supports both Google Gemini and OpenAI models
"""

import os
import asyncio
from typing import Optional, Dict, Any

# Try to import configuration
try:
    from src.config import LLM_PROVIDER, GOOGLE_API_KEY, OPENAI_API_KEY, OPENAI_MODEL
except ImportError:
    # Fallback configuration if config is not available
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')

# Try to import Google GenAI
GOOGLE_GENAI_AVAILABLE = False
configure = None
GenerativeModel = None

try:
    from google.generativeai.client import configure
    from google.generativeai.generative_models import GenerativeModel
    GOOGLE_GENAI_AVAILABLE = True
    print("Google Generative AI is available")
except ImportError:
    print("Google Generative AI not available")

# Try to import OpenAI
OPENAI_AVAILABLE = False
AsyncOpenAI = None

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
    print("OpenAI is available")
except ImportError:
    print("OpenAI not available")

class LLMManager:
    """Manages different LLM providers with a unified interface"""
    
    def __init__(self):
        self.provider = LLM_PROVIDER.lower()
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate that the required API keys are available for the selected provider"""
        if self.provider == 'gemini':
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is required for Gemini provider")
            if not GOOGLE_GENAI_AVAILABLE:
                raise ValueError("Google Generative AI library is not available")
        elif self.provider == 'openai':
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            if not OPENAI_AVAILABLE:
                raise ValueError("OpenAI library is not available")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate a response using the configured LLM provider
        
        Args:
            prompt (str): The prompt to send to the LLM
            model (str, optional): Specific model to use (overrides default)
            
        Returns:
            str: The generated response text
        """
        if self.provider == 'gemini':
            return await self._generate_gemini_response(prompt, model)
        elif self.provider == 'openai':
            return await self._generate_openai_response(prompt, model)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def _generate_gemini_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate a response using Google Gemini
        
        Args:
            prompt (str): The prompt to send to Gemini
            model (str, optional): Specific model to use
            
        Returns:
            str: The generated response text
        """
        if not GOOGLE_GENAI_AVAILABLE or configure is None or GenerativeModel is None:
            raise ValueError("Google Generative AI is not available")
        
        # Configure Google GenAI
        configure(api_key=GOOGLE_API_KEY)
        
        # Use specified model or default
        model_name = model or 'gemini-2.5-flash'
        
        # Create the model
        gemini_model = GenerativeModel(model_name)
        
        # Generate the response
        response = await gemini_model.generate_content_async(prompt)
        return response.text
    
    async def _generate_openai_response(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate a response using OpenAI
        
        Args:
            prompt (str): The prompt to send to OpenAI
            model (str, optional): Specific model to use
            
        Returns:
            str: The generated response text
        """
        if not OPENAI_AVAILABLE or AsyncOpenAI is None:
            raise ValueError("OpenAI library is not available")
        
        # Create OpenAI client
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Use specified model or default
        model_name = model or OPENAI_MODEL
        
        # Generate the response
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        return response.choices[0].message.content

# Create a global instance
llm_manager = LLMManager()

# Convenience function for easy access
async def generate_llm_response(prompt: str, model: Optional[str] = None) -> str:
    """
    Generate an LLM response using the configured provider
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str, optional): Specific model to use
        
    Returns:
        str: The generated response text
    """
    return await llm_manager.generate_response(prompt, model)