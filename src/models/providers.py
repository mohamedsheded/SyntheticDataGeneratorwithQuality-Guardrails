"""LLM provider abstractions"""

import os
import time
from abc import ABC, abstractmethod
from typing import Optional
import openai
import groq
from pathlib import Path

# Try to import langsmith for tracing
try:
    from langsmith import traceable
except ImportError:
    # If langsmith is not available, create a no-op decorator
    def traceable(func=None, **kwargs):
        if func is None:
            return lambda f: f
        return func

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Also try loading from current directory
        load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

from ..config.schema import ModelConfig


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_id = f"{config.provider}:{config.model}"
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> tuple[str, float]:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Tuple of (generated_text, generation_time_seconds)
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, config: ModelConfig, api_key: Optional[str] = None):
        super().__init__(config)
        # Get API key from parameter, environment variable, or raise error
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            # Provide helpful error message
            env_var_set = "OPENAI_API_KEY" in os.environ
            error_msg = (
                "OpenAI API key not found.\n"
                "Please set the OPENAI_API_KEY environment variable in one of these ways:\n"
                "  1. Export in your shell: export OPENAI_API_KEY=your_key_here\n"
                "  2. Create a .env file in the project root with: OPENAI_API_KEY=your_key_here\n"
                "  3. Pass it as a parameter to create_provider()\n"
            )
            if env_var_set:
                error_msg += f"\nNote: OPENAI_API_KEY is in os.environ but is empty or None."
            raise ValueError(error_msg)
        
        self.client = openai.OpenAI(api_key=api_key)
    
    @traceable(name=f"openai_generate", run_type="llm")
    def generate(self, prompt: str, **kwargs) -> tuple[str, float]:
        """Generate using OpenAI API"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )
            
            generation_time = time.time() - start_time
            text = response.choices[0].message.content.strip()
            
            return text, generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            raise RuntimeError(f"OpenAI generation failed: {e}") from e


class GroqProvider(LLMProvider):
    """Groq API provider"""
    
    def __init__(self, config: ModelConfig, api_key: Optional[str] = None):
        super().__init__(config)
        # Get API key from parameter, environment variable, or raise error
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            # Provide helpful error message
            env_var_set = "GROQ_API_KEY" in os.environ
            error_msg = (
                "Groq API key not found.\n"
                "Please set the GROQ_API_KEY environment variable in one of these ways:\n"
                "  1. Export in your shell: export GROQ_API_KEY=your_key_here\n"
                "  2. Create a .env file in the project root with: GROQ_API_KEY=your_key_here\n"
                "  3. Pass it as a parameter to create_provider()\n"
            )
            if env_var_set:
                error_msg += f"\nNote: GROQ_API_KEY is in os.environ but is empty or None."
            raise ValueError(error_msg)
        
        self.client = groq.Groq(api_key=api_key)
    
    @traceable(name=f"groq_generate", run_type="llm")
    def generate(self, prompt: str, **kwargs) -> tuple[str, float]:
        """Generate using Groq API"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )
            
            generation_time = time.time() - start_time
            
            # Check if response has choices
            if not response.choices or len(response.choices) == 0:
                raise RuntimeError("Groq API returned no choices in response")
            
            choice = response.choices[0]
            
            # Check finish_reason - might indicate why content is missing
            finish_reason = getattr(choice, 'finish_reason', None)
            if finish_reason and finish_reason not in ('stop', 'length'):
                # Log warning but don't fail - some finish reasons are acceptable
                import sys
                print(f"Warning: Groq API finished with reason: {finish_reason}", file=sys.stderr)
            
            # Check if message content exists
            message_content = choice.message.content
            if message_content is None:
                error_msg = f"Groq API returned None for message content"
                if finish_reason:
                    error_msg += f" (finish_reason: {finish_reason})"
                # Debug: Log full response structure if DEBUG_GROQ is set
                if os.getenv("DEBUG_GROQ"):
                    import sys
                    print(f"DEBUG: Full response structure: {response}", file=sys.stderr)
                    print(f"DEBUG: Choice object: {choice}", file=sys.stderr)
                    print(f"DEBUG: Message object: {choice.message}", file=sys.stderr)
                raise RuntimeError(error_msg)
            
            text = message_content.strip()
            
            # Validate we got actual content
            if not text:
                error_msg = "Groq API returned empty content after stripping"
                if finish_reason:
                    error_msg += f" (finish_reason: {finish_reason})"
                if os.getenv("DEBUG_GROQ"):
                    import sys
                    print(f"DEBUG: Original message_content: {repr(message_content)}", file=sys.stderr)
                raise RuntimeError(error_msg)
            
            return text, generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            raise RuntimeError(f"Groq generation failed: {e}") from e


def create_provider(config: ModelConfig, api_key: Optional[str] = None) -> LLMProvider:
    """
    Factory function to create appropriate provider.
    
    Args:
        config: Model configuration
        api_key: Optional API key (if not provided, uses provider-specific env var)
                 For OpenAI: OPENAI_API_KEY
                 For Groq: GROQ_API_KEY
        
    Returns:
        LLMProvider instance
    """
    if config.provider == "openai":
        return OpenAIProvider(config, api_key=api_key)
    elif config.provider == "groq":
        return GroqProvider(config, api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}. Supported providers: 'openai', 'groq'.")

