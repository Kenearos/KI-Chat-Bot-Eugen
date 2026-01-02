"""
Perplexity API Provider for Eugen Bot
Handles communication with Perplexity Sonar API
"""
import httpx
import json
import time
import logging
from typing import List, Dict, Optional


class PerplexityProvider:
    """Communicates with Perplexity API for AI responses"""

    def __init__(self, api_key, model="sonar-pro", max_tokens=450, temperature=0.7, logger=None):
        """
        Initialize Perplexity API provider

        Args:
            api_key (str): Perplexity API key
            model (str): Model to use (default: sonar-pro)
            max_tokens (int): Maximum tokens in response
            temperature (float): Sampling temperature
            logger: Optional logger instance for error reporting
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = "https://api.perplexity.ai"
        self.logger = logger or logging.getLogger(__name__)

        # Statistics
        self.total_requests = 0
        self.total_tokens = 0
        self.total_errors = 0
        self.last_response_time = 0

    async def get_response(self, messages):
        """
        Send messages to Perplexity API and get response

        Args:
            messages (list): List of message dicts with 'role' and 'content'
                Example: [
                    {"role": "system", "content": "You are..."},
                    {"role": "user", "content": "Hello"}
                ]

        Returns:
            str: AI response content
            None: If error occurred
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )

                self.last_response_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    tokens_used = data.get('usage', {}).get('total_tokens', 0)

                    # Update statistics
                    self.total_requests += 1
                    self.total_tokens += tokens_used

                    return content
                else:
                    self.total_errors += 1
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    self.logger.error(error_msg)
                    return None

        except httpx.TimeoutException:
            self.total_errors += 1
            self.logger.error("API Timeout: Request took too long")
            return None
        except Exception as e:
            self.total_errors += 1
            self.logger.error(f"API Error: {str(e)}")
            return None

    async def validate_api_key(self):
        """
        Validate API key with a simple test request

        Returns:
            bool: True if API key is valid
        """
        test_messages = [
            {"role": "user", "content": "test"}
        ]

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": test_messages,
                        "max_tokens": 10
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                return response.status_code == 200
        except Exception:
            return False

    def get_statistics(self):
        """
        Get API usage statistics

        Returns:
            dict: Statistics including requests, tokens, errors, avg response time
        """
        avg_response_time = self.last_response_time if self.total_requests > 0 else 0
        success_rate = (
            ((self.total_requests - self.total_errors) / self.total_requests * 100)
            if self.total_requests > 0
            else 0
        )

        # Rough cost calculation (example pricing, adjust as needed)
        # Perplexity pricing varies, this is an estimate
        estimated_cost = self.total_tokens * 0.0003 / 1000  # $0.0003 per 1K tokens

        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_errors": self.total_errors,
            "avg_response_time": avg_response_time,
            "success_rate": success_rate,
            "estimated_cost": estimated_cost
        }

    def reset_statistics(self):
        """Reset all statistics counters"""
        self.total_requests = 0
        self.total_tokens = 0
        self.total_errors = 0
        self.last_response_time = 0
