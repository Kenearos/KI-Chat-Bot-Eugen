"""
Tests for PerplexityProvider AI API class
"""
import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from ai_provider import PerplexityProvider


class TestPerplexityProvider:
    """Test PerplexityProvider functionality"""

    def test_init_sets_attributes(self):
        """Test that initialization sets all attributes correctly"""
        provider = PerplexityProvider(
            api_key="test-key",
            model="sonar-pro",
            max_tokens=450,
            temperature=0.7
        )

        assert provider.api_key == "test-key"
        assert provider.model == "sonar-pro"
        assert provider.max_tokens == 450
        assert provider.temperature == 0.7
        assert provider.base_url == "https://api.perplexity.ai"

    def test_init_default_values(self):
        """Test default parameter values"""
        provider = PerplexityProvider(api_key="test-key")

        assert provider.model == "sonar-pro"
        assert provider.max_tokens == 450
        assert provider.temperature == 0.7

    def test_init_statistics_start_at_zero(self):
        """Test that statistics counters start at zero"""
        provider = PerplexityProvider(api_key="test-key")

        assert provider.total_requests == 0
        assert provider.total_tokens == 0
        assert provider.total_errors == 0
        assert provider.last_response_time == 0

    @pytest.mark.asyncio
    async def test_get_response_success(self, sample_messages, mock_perplexity_response):
        """Test successful API response"""
        provider = PerplexityProvider(api_key="test-key")

        # Mock the HTTP client
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_perplexity_response

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # Call the method
            result = await provider.get_response(sample_messages)

            # Verify result
            assert result == "This is a test response from the AI."
            assert provider.total_requests == 1
            assert provider.total_tokens == 70  # From mock response
            assert provider.total_errors == 0

    @pytest.mark.asyncio
    async def test_get_response_constructs_correct_payload(self, sample_messages):
        """Test that request payload is constructed correctly"""
        provider = PerplexityProvider(
            api_key="test-key",
            model="sonar-pro",
            max_tokens=450,
            temperature=0.7
        )

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"total_tokens": 10}
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await provider.get_response(sample_messages)

            # Verify the call was made with correct parameters
            call_args = mock_post.call_args
            assert call_args[1]["json"]["model"] == "sonar-pro"
            assert call_args[1]["json"]["messages"] == sample_messages
            assert call_args[1]["json"]["max_tokens"] == 450
            assert call_args[1]["json"]["temperature"] == 0.7

    @pytest.mark.asyncio
    async def test_get_response_includes_auth_header(self, sample_messages):
        """Test that Authorization header is included"""
        provider = PerplexityProvider(api_key="test-secret-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"total_tokens": 10}
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await provider.get_response(sample_messages)

            call_args = mock_post.call_args
            headers = call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer test-secret-key"
            assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_response_handles_401_error(self, sample_messages):
        """Test handling of 401 Unauthorized error"""
        provider = PerplexityProvider(api_key="invalid-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.get_response(sample_messages)

            assert result is None
            assert provider.total_errors == 1
            assert provider.total_requests == 0  # Failed requests don't count

    @pytest.mark.asyncio
    async def test_get_response_handles_500_error(self, sample_messages):
        """Test handling of 500 server error"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.get_response(sample_messages)

            assert result is None
            assert provider.total_errors == 1

    @pytest.mark.asyncio
    async def test_get_response_handles_timeout(self, sample_messages):
        """Test handling of request timeout"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.get_response(sample_messages)

            assert result is None
            assert provider.total_errors == 1

    @pytest.mark.asyncio
    async def test_get_response_handles_network_error(self, sample_messages):
        """Test handling of network errors"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(side_effect=httpx.NetworkError("Network error"))
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.get_response(sample_messages)

            assert result is None
            assert provider.total_errors == 1

    @pytest.mark.asyncio
    async def test_get_response_tracks_response_time(self, sample_messages, mock_perplexity_response):
        """Test that response time is tracked"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_perplexity_response

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await provider.get_response(sample_messages)

            assert provider.last_response_time > 0

    @pytest.mark.asyncio
    async def test_validate_api_key_success(self):
        """Test successful API key validation"""
        provider = PerplexityProvider(api_key="valid-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.validate_api_key()

            assert result is True

    @pytest.mark.asyncio
    async def test_validate_api_key_failure(self):
        """Test failed API key validation"""
        provider = PerplexityProvider(api_key="invalid-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 401

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.validate_api_key()

            assert result is False

    @pytest.mark.asyncio
    async def test_validate_api_key_handles_exception(self):
        """Test API key validation handles exceptions"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(side_effect=Exception("Network error"))
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.validate_api_key()

            assert result is False

    @pytest.mark.asyncio
    async def test_validate_api_key_uses_minimal_request(self):
        """Test that validation uses minimal tokens"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await provider.validate_api_key()

            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert payload["max_tokens"] == 10  # Minimal tokens
            assert payload["messages"][0]["content"] == "test"

    def test_get_statistics_initial_state(self):
        """Test statistics in initial state"""
        provider = PerplexityProvider(api_key="test-key")

        stats = provider.get_statistics()

        assert stats["total_requests"] == 0
        assert stats["total_tokens"] == 0
        assert stats["total_errors"] == 0
        assert stats["avg_response_time"] == 0
        assert stats["success_rate"] == 0
        assert stats["estimated_cost"] == 0

    @pytest.mark.asyncio
    async def test_get_statistics_after_requests(self, sample_messages, mock_perplexity_response):
        """Test statistics after successful requests"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_perplexity_response

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            # Make 2 successful requests
            await provider.get_response(sample_messages)
            await provider.get_response(sample_messages)

            stats = provider.get_statistics()

            assert stats["total_requests"] == 2
            assert stats["total_tokens"] == 140  # 70 * 2
            assert stats["total_errors"] == 0
            assert stats["success_rate"] == 100
            assert stats["estimated_cost"] > 0

    @pytest.mark.asyncio
    async def test_get_statistics_with_errors(self, sample_messages):
        """Test statistics calculation with errors"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            # First request succeeds
            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"total_tokens": 50}
            }

            # Second request fails
            mock_response_fail = Mock()
            mock_response_fail.status_code = 500
            mock_response_fail.text = "Error"

            mock_post = AsyncMock(side_effect=[mock_response_success, mock_response_fail])
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await provider.get_response(sample_messages)
            await provider.get_response(sample_messages)

            stats = provider.get_statistics()

            assert stats["total_requests"] == 1
            assert stats["total_errors"] == 1
            assert stats["success_rate"] == 0  # 0 out of 1 completed request succeeded

    def test_reset_statistics(self):
        """Test resetting statistics"""
        provider = PerplexityProvider(api_key="test-key")

        # Manually set some statistics
        provider.total_requests = 10
        provider.total_tokens = 500
        provider.total_errors = 2
        provider.last_response_time = 1.5

        provider.reset_statistics()

        assert provider.total_requests == 0
        assert provider.total_tokens == 0
        assert provider.total_errors == 0
        assert provider.last_response_time == 0

    @pytest.mark.asyncio
    async def test_get_response_missing_usage_data(self, sample_messages):
        """Test handling response without usage data"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}]
                # No usage field
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            result = await provider.get_response(sample_messages)

            assert result == "test response"
            assert provider.total_tokens == 0  # Should default to 0

    @pytest.mark.asyncio
    async def test_get_response_uses_correct_endpoint(self, sample_messages):
        """Test that correct API endpoint is used"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"total_tokens": 10}
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            await provider.get_response(sample_messages)

            call_args = mock_post.call_args
            # First positional argument should be the URL
            assert call_args[0][0] == "https://api.perplexity.ai/chat/completions"

    @pytest.mark.asyncio
    async def test_get_response_timeout_configuration(self, sample_messages):
        """Test that timeout is configured correctly"""
        provider = PerplexityProvider(api_key="test-key")

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test"}}],
                "usage": {"total_tokens": 10}
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value.post = mock_post

            await provider.get_response(sample_messages)

            # Check that AsyncClient was instantiated with timeout
            call_args = mock_client_class.call_args
            assert call_args[1]["timeout"] == 30.0
