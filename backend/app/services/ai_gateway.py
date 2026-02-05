"""
AI Gateway Service

Multi-provider AI gateway with automatic failover.
Supports: Mistral AI (France), Scaleway (France), Ollama (local).

All providers are EU-based or local to ensure GDPR compliance.
"""

import logging
import os
import httpx
from typing import List, Optional, Dict, Any, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

# Providers
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from app.core.config import settings

logger = logging.getLogger(__name__)

class AIGateway:
    """
    Gateway to manage multiple AI providers with failover support.
    
    Priority is defined in settings.AI_PROVIDER_PRIORITY.
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseChatModel] = {}
        self._initialize_providers()
        
    def _initialize_providers(self):
        """Initialize all configured providers."""

        # Initialize Langfuse Callback if configured
        callbacks = []
        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            try:
                # Conditional import - only load if configured
                from langfuse.langchain import CallbackHandler
                
                # Pass config directly to handler, do not mutate os.environ
                langfuse_handler = CallbackHandler(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,  # None means disabled, self-hosted URL required
                )
                callbacks.append(langfuse_handler)
                logger.info("✅ Langfuse observability initialized")
            except ImportError:
                logger.warning("⚠️ Langfuse package not installed, skipping observability")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Langfuse: {e}")
        
        # 1. Mistral AI (Official API)
        if settings.MISTRAL_API_KEY:
            try:
                self.providers["mistral"] = ChatMistralAI(
                    mistral_api_key=settings.MISTRAL_API_KEY,
                    model=settings.MISTRAL_MODEL,
                    endpoint=settings.MISTRAL_API_BASE,
                    temperature=0.2,
                    timeout=settings.AI_TIMEOUT,
                    callbacks=callbacks,
                )
                logger.info("✅ Mistral AI provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Mistral AI: {e}")

        # 2. Scaleway (via OpenAI compatible API)
        if settings.SCALEWAY_API_KEY:
            try:
                self.providers["scaleway"] = ChatOpenAI(
                    api_key=settings.SCALEWAY_API_KEY,
                    base_url=settings.SCALEWAY_API_BASE,
                    model=settings.SCALEWAY_MODEL,
                    temperature=0.2,
                    timeout=settings.AI_TIMEOUT,
                    callbacks=callbacks,
                )
                logger.info("✅ Scaleway provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Scaleway: {e}")

        # 3. Local Ollama (Fallback)
        # Always initialize Ollama as fallback
        try:
            self.providers["ollama"] = ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.2,
                timeout=settings.AI_TIMEOUT, # Note: ChatOllama uses request_timeout in older versions, timeout in newer
                callbacks=callbacks,
            )
            logger.info("✅ Local Ollama provider initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama: {e}")
            
    def get_llm(self, preferred_provider: Optional[str] = None) -> BaseChatModel:
        """
        Get the best available LLM based on priority and availability.
        """
        priority_list = settings.AI_PROVIDER_PRIORITY.split(",")
        
        # If specific provider requested, try that first
        if preferred_provider:
             priority_list.insert(0, preferred_provider)
             
        for provider_name in priority_list:
            provider_name = provider_name.strip().lower()
            if provider_name in self.providers:
                return self.providers[provider_name]
                
        # If no priority providers found, return first available
        if self.providers:
            return list(self.providers.values())[0]
            
        raise Exception("No AI providers available. Check your configuration.")

    def get_runnable(self, tools: List[BaseTool] = None):
        """
        Get a runnable chain with the best available LLM.
        Directly binds tools if provided.
        """
        llm = self.get_llm()
        
        if tools:
            # Check if LLM supports tool binding
            if hasattr(llm, "bind_tools"):
                 return llm.bind_tools(tools)
            else:
                logger.warning(f"LLM {llm} does not support bind_tools")
                return llm
        
        return llm

# Global instance
ai_gateway = AIGateway()
