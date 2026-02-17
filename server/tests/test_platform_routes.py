import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from httpx import AsyncClient
import io
from PIL import Image


class TestSteamRoute:
    """Test Steam avatar retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_retrieve_steam_avatar_from_cache(self, client, test_cache, sample_avatar_png):
        """Test retrieving a Steam avatar that's already cached."""
        # Populate cache
        await test_cache.set("steam", "76561198000000001", sample_avatar_png)
        
        # Make request
        response = client.get("/api/v1/steam/retrieve/76561198000000001")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_retrieve_steam_avatar_cache_miss(self, client, test_cache):
        """Test retrieving a Steam avatar that's not cached (should attempt API fetch)."""
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            # Mock API response
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            mock_fetch.return_value = buffer.getvalue()
            
            response = client.get("/api/v1/steam/retrieve/76561198999999999")
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            mock_fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_steam_avatar_not_found(self, client):
        """Test retrieving a Steam avatar that doesn't exist."""
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = None
            
            response = client.get("/api/v1/steam/retrieve/nonexistent")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_retrieve_steam_avatar_with_default(self, client, sample_avatar_png):
        """Test retrieving with default_enabled when user not found."""
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            with patch('services.default_service.default_service.get_default_avatar', new_callable=AsyncMock) as mock_default:
                mock_fetch.return_value = None
                mock_default.return_value = sample_avatar_png
                
                response = client.get("/api/v1/steam/retrieve/nonexistent?default_enabled=true")
                
                assert response.status_code == status.HTTP_200_OK
                assert response.headers["content-type"] == "image/png"
                mock_default.assert_called_once_with("steam")


class TestXboxRoute:
    """Test Xbox avatar retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_retrieve_xbox_avatar_from_cache(self, client, test_cache, sample_avatar_png):
        """Test retrieving an Xbox avatar that's already cached."""
        await test_cache.set("xbox", "TestGamer", sample_avatar_png)
        
        response = client.get("/api/v1/xbox/retrieve/TestGamer")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
    
    @pytest.mark.asyncio
    async def test_retrieve_xbox_avatar_cache_miss(self, client):
        """Test retrieving an Xbox avatar that's not cached."""
        with patch('services.avatar_services.XboxAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            mock_fetch.return_value = buffer.getvalue()
            
            response = client.get("/api/v1/xbox/retrieve/NewGamer")
            
            assert response.status_code == status.HTTP_200_OK
            mock_fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_xbox_avatar_not_found(self, client):
        """Test retrieving an Xbox avatar that doesn't exist."""
        with patch('services.avatar_services.XboxAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = None
            
            response = client.get("/api/v1/xbox/retrieve/nonexistent")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPSNRoute:
    """Test PSN avatar retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_retrieve_psn_avatar_from_cache(self, client, test_cache, sample_avatar_png):
        """Test retrieving a PSN avatar that's already cached."""
        await test_cache.set("psn", "PSNUser123", sample_avatar_png)
        
        response = client.get("/api/v1/psn/retrieve/PSNUser123")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
    
    @pytest.mark.asyncio
    async def test_retrieve_psn_avatar_cache_miss(self, client):
        """Test retrieving a PSN avatar that's not cached."""
        with patch('routes.platforms.get_psn_service') as mock_service:
            mock_psn = AsyncMock()
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            mock_psn.get_processed_avatar.return_value = buffer.getvalue()
            mock_service.return_value = mock_psn
            
            response = client.get("/api/v1/psn/retrieve/NewPSNUser")
            
            assert response.status_code == status.HTTP_200_OK


class TestSwitchRoute:
    """Test Nintendo Switch avatar retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_retrieve_switch_avatar_from_cache(self, client, test_cache, sample_avatar_png):
        """Test retrieving a Switch avatar that's already cached."""
        await test_cache.set("switch", "SwitchUser123", sample_avatar_png)
        
        response = client.get("/api/v1/switch/retrieve/SwitchUser123")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
    
    @pytest.mark.asyncio
    async def test_retrieve_switch_avatar_generation(self, client):
        """Test Switch avatar generation for uncached user."""
        with patch('services.avatar_services.SwitchAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_gen:
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            mock_gen.return_value = buffer.getvalue()
            
            response = client.get("/api/v1/switch/retrieve/NewSwitchUser")
            
            assert response.status_code == status.HTTP_200_OK
            mock_gen.assert_called_once()


class TestCacheHitRates:
    """Test cache hit behavior across platforms."""
    
    @pytest.mark.asyncio
    async def test_cache_hit_reduces_api_calls(self, client, test_cache, sample_avatar_png):
        """Verify that cached avatars don't trigger API calls."""
        await test_cache.set("steam", "76561198000000001", sample_avatar_png)
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            # Make multiple requests
            for _ in range(5):
                response = client.get("/api/v1/steam/retrieve/76561198000000001")
                assert response.status_code == status.HTTP_200_OK
            
            # Should not call API at all since it's cached
            mock_fetch.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_persists_after_fetch(self, client, test_cache):
        """Test that fetched avatars are cached for subsequent requests."""
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            mock_fetch.return_value = buffer.getvalue()
            
            # First request - should call API
            response1 = client.get("/api/v1/steam/retrieve/76561198000000002")
            assert response1.status_code == status.HTTP_200_OK
            assert mock_fetch.call_count == 1
            
            # Second request - should use cache
            response2 = client.get("/api/v1/steam/retrieve/76561198000000002")
            assert response2.status_code == status.HTTP_200_OK
            assert mock_fetch.call_count == 1  # Still only 1 call


class TestErrorHandling:
    """Test error handling in platform routes."""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test handling of API errors - errors are caught and treated as avatar not found."""
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")
            
            response = client.get("/api/v1/steam/retrieve/76561198000000001")
            
            # API errors are caught and return 404 (avatar not found) instead of 500
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_invalid_platform_data(self, client):
        """Test handling of invalid/malformed platform data."""
        # Test with extremely long user ID
        long_id = "a" * 1000
        response = client.get(f"/api/v1/steam/retrieve/{long_id}")
        
        # Should handle gracefully without crashing
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_not_exceeded_normal_use(self, client, test_cache, sample_avatar_png):
        """Test that normal usage doesn't trigger rate limiting."""
        await test_cache.set("steam", "76561198000000001", sample_avatar_png)
        
        # Make several requests under the limit
        for i in range(10):
            response = client.get("/api/v1/steam/retrieve/76561198000000001")
            assert response.status_code == status.HTTP_200_OK
