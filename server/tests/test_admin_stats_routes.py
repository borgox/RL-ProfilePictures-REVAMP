import pytest
from fastapi import status


class TestAdminAuthentication:
    """Test admin authentication and authorization."""
    
    @pytest.mark.asyncio
    async def test_admin_stats_without_auth(self, client):
        """Test accessing admin stats without authentication."""
        response = client.get("/api/v1/admin/stats")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_admin_stats_with_invalid_auth(self, client):
        """Test accessing admin stats with invalid authentication."""
        headers = {"Authorization": "Bearer wrong_secret"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_admin_stats_with_valid_auth(self, client):
        """Test accessing admin stats with valid authentication."""
        headers = {"Authorization": f"Bearer {client.app.state.limiter}"}
        # Use the admin_secret from settings
        from config import settings
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "cache" in data
        assert "database" in data
        assert "system" in data
    
    @pytest.mark.asyncio
    async def test_admin_delete_without_auth(self, client):
        """Test deleting avatar without authentication."""
        response = client.delete("/api/v1/epic/delete/TestUser")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_admin_auth_no_bearer_prefix(self, client):
        """Test authentication without Bearer prefix."""
        from config import settings
        headers = {"Authorization": settings.admin_secret}
        
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK


class TestAdminDelete:
    """Test admin delete functionality."""
    
    @pytest.mark.asyncio
    async def test_delete_epic_avatar_success(self, client, test_cache, sample_avatar_png):
        """Test successful deletion of Epic avatar."""
        from config import settings
        
        # Pre-populate cache
        await test_cache.set("epic", "TestUser", sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.delete("/api/v1/epic/delete/TestUser", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()
        
        # Verify avatar is actually deleted from cache
        cached_data = await test_cache.get("epic", "TestUser")
        assert cached_data is None
    
    @pytest.mark.asyncio
    async def test_delete_epic_avatar_not_found(self, client):
        """Test deleting non-existent Epic avatar - cache.delete() always returns True."""
        from config import settings
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.delete("/api/v1/epic/delete/NonExistentUser", headers=headers)
        
        # Cache delete returns True even if file doesn't exist, so we get 200
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_delete_steam_avatar_success(self, client, test_cache, sample_avatar_png):
        """Test successful deletion of Steam avatar."""
        from config import settings
        
        await test_cache.set("steam", "76561198000000001", sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.delete("/api/v1/steam/delete/76561198000000001", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_delete_xbox_avatar_success(self, client, test_cache, sample_avatar_png):
        """Test successful deletion of Xbox avatar."""
        from config import settings
        
        await test_cache.set("xbox", "TestGamer", sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.delete("/api/v1/xbox/delete/TestGamer", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_delete_psn_avatar_success(self, client, test_cache, sample_avatar_png):
        """Test successful deletion of PSN avatar."""
        from config import settings
        
        await test_cache.set("psn", "PSNUser123", sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.delete("/api/v1/psn/delete/PSNUser123", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_delete_multiple_avatars(self, client, test_cache, sample_avatar_png):
        """Test deleting multiple avatars sequentially."""
        from config import settings
        
        # Create multiple avatars
        users = ["User1", "User2", "User3"]
        for user in users:
            await test_cache.set("epic", user, sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        
        # Delete all
        for user in users:
            response = client.delete(f"/api/v1/epic/delete/{user}", headers=headers)
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all deleted
        for user in users:
            cached_data = await test_cache.get("epic", user)
            assert cached_data is None


class TestAdminStats:
    """Test admin statistics endpoint."""
    
    @pytest.mark.asyncio
    async def test_admin_stats_structure(self, client):
        """Test that admin stats return proper structure."""
        from config import settings
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check top-level structure
        assert "cache" in data
        assert "database" in data
        assert "system" in data
        
        # Check system info
        system = data["system"]
        assert "rate_limit_requests" in system
        assert "rate_limit_window" in system
        assert "target_image_size" in system
        assert "cache_directory" in system
    
    @pytest.mark.asyncio
    async def test_admin_stats_cache_info(self, client, test_cache, sample_avatar_png):
        """Test that admin stats include cache information."""
        from config import settings
        
        # Populate some cache data
        await test_cache.set("steam", "user1", sample_avatar_png)
        await test_cache.set("epic", "user2", sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        cache_stats = data["cache"]
        assert "memory_cache" in cache_stats or "filesystem_cache" in cache_stats
    
    @pytest.mark.asyncio
    async def test_admin_stats_database_info(self, client):
        """Test that admin stats include database information."""
        from config import settings
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        db_stats = data["database"]
        # Database stats should contain some metrics
        assert isinstance(db_stats, dict)


class TestAdminCleanup:
    """Test admin cleanup endpoint."""
    
    @pytest.mark.asyncio
    async def test_admin_cleanup_success(self, client):
        """Test successful cleanup operation."""
        from config import settings
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.post("/api/v1/admin/cleanup?hours=24", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "cleaned" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_admin_cleanup_custom_hours(self, client):
        """Test cleanup with custom hours parameter."""
        from config import settings
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.post("/api/v1/admin/cleanup?hours=48", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "48 hours" in data["message"]
    
    @pytest.mark.asyncio
    async def test_admin_cleanup_without_auth(self, client):
        """Test cleanup without authentication."""
        response = client.post("/api/v1/admin/cleanup?hours=24")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStatsRoute:
    """Test public stats dashboard route."""
    
    @pytest.mark.asyncio
    async def test_stats_dashboard_without_secret(self, client):
        """Test accessing stats dashboard without secret."""
        response = client.get("/api/v1/stats")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_stats_dashboard_with_invalid_secret(self, client):
        """Test accessing stats dashboard with invalid secret."""
        response = client.get("/api/v1/stats?secret=wrong_secret")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_stats_dashboard_with_valid_secret(self, client, test_db):
        """Test accessing stats dashboard with valid secret."""
        from config import settings
        from unittest.mock import patch, AsyncMock
        
        # Mock the database stats method to return simple stats (SQLite doesn't support PostgreSQL syntax)
        mock_stats = {
            "total_requests": 100,
            "successful_requests": 95,
            "cache_hits": 80,
            "cache_hit_rate": 80.0,
            "cached_files": 50,
            "cache_size_mb": 10.5,
            "user_analytics": {},
            "recent_activity": {},
            "platform_popularity": {},
            "daily_trends": [],
            "hourly_trends": [],
            "top_users": [],
            "recent_errors": []
        }
        
        with patch.object(test_db, 'get_comprehensive_stats', new_callable=AsyncMock, return_value=mock_stats):
            response = client.get(f"/api/v1/stats?secret={settings.admin_secret}")
            
            assert response.status_code == status.HTTP_200_OK
            # Should return HTML content
            assert "text/html" in response.headers.get("content-type", "")
            assert b"Analytics" in response.content or b"Dashboard" in response.content
    
    @pytest.mark.asyncio
    async def test_stats_dashboard_html_structure(self, client, test_db):
        """Test that stats dashboard returns valid HTML."""
        from config import settings
        from unittest.mock import patch, AsyncMock
        
        # Mock stats to avoid SQLite syntax issues
        mock_stats = {
            "total_requests": 100,
            "successful_requests": 95,
            "cache_hits": 80,
            "cache_hit_rate": 80.0,
            "cached_files": 50,
            "cache_size_mb": 10.5,
            "user_analytics": {},
            "recent_activity": {},
            "platform_popularity": {},
            "daily_trends": [],
            "hourly_trends": [],
            "top_users": [],
            "recent_errors": []
        }
        
        with patch.object(test_db, 'get_comprehensive_stats', new_callable=AsyncMock, return_value=mock_stats):
            response = client.get(f"/api/v1/stats?secret={settings.admin_secret}")
            
            assert response.status_code == status.HTTP_200_OK
            html_content = response.content.decode('utf-8')
            
            # Check for essential HTML elements
            assert "<!DOCTYPE html>" in html_content
            assert "<html" in html_content
            assert "</html>" in html_content
            assert "chart" in html_content.lower() or "stats" in html_content.lower()


class TestAdminEdgeCases:
    """Test edge cases for admin routes."""
    
    @pytest.mark.asyncio
    async def test_delete_with_special_characters(self, client, test_cache, sample_avatar_png):
        """Test deleting user with special characters in ID."""
        from config import settings
        
        user_id = "User_Test-123"
        await test_cache.set("epic", user_id, sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.delete(f"/api/v1/epic/delete/{user_id}", headers=headers)
        
        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    @pytest.mark.asyncio
    async def test_admin_stats_during_high_load(self, client, test_cache, sample_avatar_png):
        """Test admin stats work correctly during high load."""
        from config import settings
        
        # Simulate high load by creating many cache entries
        for i in range(100):
            await test_cache.set("steam", f"user{i}", sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.get("/api/v1/admin/stats", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        # Should complete without timeout
    
    @pytest.mark.asyncio
    async def test_concurrent_deletes_same_avatar(self, client, test_cache, sample_avatar_png):
        """Test concurrent delete requests for the same avatar."""
        from config import settings
        from concurrent.futures import ThreadPoolExecutor
        
        user_id = "ConcurrentDeleteUser"
        await test_cache.set("epic", user_id, sample_avatar_png)
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        
        def delete_avatar():
            return client.delete(f"/api/v1/epic/delete/{user_id}", headers=headers)
        
        # Simulate concurrent deletes
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(delete_avatar) for _ in range(3)]
            results = [f.result() for f in futures]
        
        # First should succeed, others should fail or also succeed (idempotent)
        success_count = sum(1 for r in results if r.status_code == status.HTTP_200_OK)
        not_found_count = sum(1 for r in results if r.status_code == status.HTTP_404_NOT_FOUND)
        
        # At least one should succeed
        assert success_count >= 1
        # Rest should either succeed (idempotent) or return not found
        assert success_count + not_found_count == 3
    
    @pytest.mark.asyncio
    async def test_admin_cleanup_with_zero_hours(self, client):
        """Test cleanup with zero hours (edge case)."""
        from config import settings
        
        headers = {"Authorization": f"Bearer {settings.admin_secret}"}
        response = client.post("/api/v1/admin/cleanup?hours=0", headers=headers)
        
        # Should handle gracefully (might clean all or reject)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
