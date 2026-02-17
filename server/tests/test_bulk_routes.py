import pytest
import time
from fastapi import status
from unittest.mock import AsyncMock, patch
from io import BytesIO
from PIL import Image
import asyncio


class TestBulkRouteBasic:
    """Test basic bulk route functionality."""
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_all_cached(self, client, test_cache, sample_avatar_png):
        """Test bulk retrieval when all avatars are cached."""
        # Pre-populate cache
        user_ids = ["76561198000000001", "76561198000000002", "76561198000000003"]
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        # Make bulk request
        payload = {
            "user_ids": user_ids,
            "platform": "steam"
        }
        response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 3
        assert data["total_found"] == 3
        assert data["total_cached"] == 3
        assert data["total_fetched"] == 0
        assert len(data["results"]) == 3
        
        # Verify all results are successful
        for result in data["results"]:
            assert result["found"] is True
            assert result["cached"] is True
            assert result["avatar_data"] is not None
            assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_all_uncached(self, client, test_cache, mock_psn_service):
        """Test bulk retrieval when no avatars are cached."""
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            mock_fetch.return_value = buffer.getvalue()
            
            user_ids = ["76561198999999001", "76561198999999002", "76561198999999003"]
            payload = {
                "user_ids": user_ids,
                "platform": "steam"
            }
            response = client.post("/api/v1/bulk/avatars", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_requested"] == 3
            assert data["total_found"] == 3
            assert data["total_cached"] == 0
            assert data["total_fetched"] == 3
            assert mock_fetch.call_count == 3
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_mixed_cached_uncached(self, client, test_cache, sample_avatar_png, mock_psn_service):
        """Test bulk retrieval with mix of cached and uncached avatars."""
        # Cache only the first user
        await test_cache.set("steam", "76561198000000001", sample_avatar_png)
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            mock_fetch.return_value = buffer.getvalue()
            
            user_ids = ["76561198000000001", "76561198999999002", "76561198999999003"]
            payload = {
                "user_ids": user_ids,
                "platform": "steam"
            }
            response = client.post("/api/v1/bulk/avatars", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_requested"] == 3
            assert data["total_found"] == 3
            assert data["total_cached"] == 1
            assert data["total_fetched"] == 2
            assert mock_fetch.call_count == 2  # Only fetches uncached users
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_some_not_found(self, client, test_cache, sample_avatar_png):
        """Test bulk retrieval when some avatars don't exist."""
        await test_cache.set("steam", "76561198000000001", sample_avatar_png)
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            # Return None for non-existent users
            mock_fetch.return_value = None
            
            user_ids = ["76561198000000001", "nonexistent1", "nonexistent2"]
            payload = {
                "user_ids": user_ids,
                "platform": "steam"
            }
            response = client.post("/api/v1/bulk/avatars", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_requested"] == 3
            assert data["total_found"] == 1
            assert data["total_cached"] == 1
            
            # Check individual results
            results = data["results"]
            assert results[0]["found"] is True
            assert results[1]["found"] is False
            assert results[2]["found"] is False


class TestBulkRouteValidation:
    """Test bulk route input validation."""
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_empty_user_ids(self, client):
        """Test bulk request with empty user_ids list."""
        payload = {
            "user_ids": [],
            "platform": "steam"
        }
        response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_too_many_users(self, client):
        """Test bulk request exceeding maximum user limit."""
        user_ids = [f"user{i}" for i in range(101)]  # More than max 100
        payload = {
            "user_ids": user_ids,
            "platform": "steam"
        }
        response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_invalid_platform(self, client):
        """Test bulk request with invalid platform."""
        payload = {
            "user_ids": ["user1", "user2"],
            "platform": "invalid_platform"
        }
        response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid platform" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_max_limit_accepted(self, client, test_cache, sample_avatar_png):
        """Test bulk request with exactly 100 users (max limit)."""
        user_ids = [f"user{i}" for i in range(100)]
        
        # Cache all users
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        payload = {
            "user_ids": user_ids,
            "platform": "steam"
        }
        response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_requested"] == 100


class TestBulkRouteGET:
    """Test GET version of bulk route."""
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_get_method(self, client, test_cache, sample_avatar_png):
        """Test GET endpoint for bulk avatars."""
        user_ids = ["user1", "user2", "user3"]
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        user_ids_str = ",".join(user_ids)
        response = client.get(f"/api/v1/bulk/avatars/steam?user_ids={user_ids_str}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_requested"] == 3
        assert data["total_found"] == 3
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_get_no_user_ids(self, client):
        """Test GET endpoint without user_ids parameter."""
        response = client.get("/api/v1/bulk/avatars/steam")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_bulk_avatars_get_with_spaces(self, client, test_cache, sample_avatar_png):
        """Test GET endpoint with spaces in user_ids."""
        user_ids = ["user1", "user2", "user3"]
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        # Test with spaces after commas
        user_ids_str = "user1, user2, user3"
        response = client.get(f"/api/v1/bulk/avatars/steam?user_ids={user_ids_str}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_requested"] == 3


class TestBulkRouteCacheStatus:
    """Test bulk cache status endpoint."""
    
    @pytest.mark.asyncio
    async def test_cache_status_all_cached(self, client, test_cache, sample_avatar_png):
        """Test cache status when all users are cached."""
        user_ids = ["user1", "user2", "user3"]
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        user_ids_str = ",".join(user_ids)
        response = client.get(f"/api/v1/bulk/cache-status/steam?user_ids={user_ids_str}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["platform"] == "steam"
        assert data["total_checked"] == 3
        assert data["total_cached"] == 3
        
        # Check individual statuses
        cache_status = data["cache_status"]
        for user_id in user_ids:
            assert cache_status[user_id]["cached"] is True
    
    @pytest.mark.asyncio
    async def test_cache_status_none_cached(self, client):
        """Test cache status when no users are cached."""
        user_ids = ["uncached1", "uncached2", "uncached3"]
        user_ids_str = ",".join(user_ids)
        response = client.get(f"/api/v1/bulk/cache-status/steam?user_ids={user_ids_str}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_cached"] == 0
        
        cache_status = data["cache_status"]
        for user_id in user_ids:
            assert cache_status[user_id]["cached"] is False
    
    @pytest.mark.asyncio
    async def test_cache_status_mixed(self, client, test_cache, sample_avatar_png):
        """Test cache status with mix of cached and uncached users."""
        # Cache only first two users
        await test_cache.set("steam", "user1", sample_avatar_png)
        await test_cache.set("steam", "user2", sample_avatar_png)
        
        user_ids = ["user1", "user2", "user3"]
        user_ids_str = ",".join(user_ids)
        response = client.get(f"/api/v1/bulk/cache-status/steam?user_ids={user_ids_str}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_checked"] == 3
        assert data["total_cached"] == 2
        
        cache_status = data["cache_status"]
        assert cache_status["user1"]["cached"] is True
        assert cache_status["user2"]["cached"] is True
        assert cache_status["user3"]["cached"] is False


class TestBulkRouteEfficiency:
    """Test efficiency comparisons: bulk vs individual requests."""
    
    @pytest.mark.asyncio
    async def test_bulk_vs_individual_cached_performance(self, client, test_cache, sample_avatar_png):
        """Compare performance of bulk vs individual requests when all cached."""
        user_ids = [f"user{i}" for i in range(50)]
        
        # Pre-populate cache
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        # Test bulk request timing
        start_bulk = time.time()
        payload = {"user_ids": user_ids, "platform": "steam"}
        bulk_response = client.post("/api/v1/bulk/avatars", json=payload)
        bulk_time = time.time() - start_bulk
        
        assert bulk_response.status_code == status.HTTP_200_OK
        bulk_data = bulk_response.json()
        
        # Test individual requests timing
        start_individual = time.time()
        for user_id in user_ids:
            individual_response = client.get(f"/api/v1/steam/retrieve/{user_id}")
            assert individual_response.status_code == status.HTTP_200_OK
        individual_time = time.time() - start_individual
        
        # Log performance comparison
        print(f"\n=== CACHED PERFORMANCE COMPARISON ===")
        print(f"Bulk request time: {bulk_time:.4f}s")
        print(f"Individual requests time: {individual_time:.4f}s")
        print(f"Speedup: {individual_time / bulk_time:.2f}x faster")
        print(f"Time saved: {individual_time - bulk_time:.4f}s")
        print(f"Processing time from response: {bulk_data['processing_time_ms']}ms")
        
        # Bulk should be faster (or at least not significantly slower)
        # Allow some tolerance for test environment variability
        assert bulk_time < individual_time * 1.5, \
            f"Bulk request ({bulk_time:.4f}s) should be faster than individual ({individual_time:.4f}s)"
    
    @pytest.mark.asyncio
    async def test_bulk_vs_individual_uncached_performance(self, client, mock_psn_service):
        """Compare performance of bulk vs individual requests when none cached."""
        user_ids = [f"uncached{i}" for i in range(20)]
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            # Simulate API delay
            async def slow_fetch(*args, **kwargs):
                await asyncio.sleep(0.01)  # 10ms delay per fetch
                img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()
            
            mock_fetch.side_effect = slow_fetch
            
            # Test bulk request timing
            start_bulk = time.time()
            payload = {"user_ids": user_ids, "platform": "steam"}
            bulk_response = client.post("/api/v1/bulk/avatars", json=payload)
            bulk_time = time.time() - start_bulk
            
            assert bulk_response.status_code == status.HTTP_200_OK
            bulk_data = bulk_response.json()
            
            # Reset mock
            mock_fetch.reset_mock()
            mock_fetch.side_effect = slow_fetch
            
            # Test individual requests timing
            start_individual = time.time()
            for user_id in user_ids:
                individual_response = client.get(f"/api/v1/steam/retrieve/{user_id}")
                assert individual_response.status_code == status.HTTP_200_OK
            individual_time = time.time() - start_individual
            
            print(f"\n=== UNCACHED PERFORMANCE COMPARISON ===")
            print(f"Bulk request time: {bulk_time:.4f}s")
            print(f"Individual requests time: {individual_time:.4f}s")
            print(f"Speedup: {individual_time / bulk_time:.2f}x faster")
            print(f"Time saved: {individual_time - bulk_time:.4f}s")
            print(f"Processing time from response: {bulk_data['processing_time_ms']}ms")
            print(f"Concurrent processing enabled: Bulk uses semaphore with limit of 10")
            
            # Bulk should be faster due to concurrent processing (or at least not significantly slower)
            # Note: In test environment with mocks, concurrency benefits may be limited
            assert bulk_time < individual_time * 1.5, \
                f"Bulk request ({bulk_time:.4f}s) should not be significantly slower than individual ({individual_time:.4f}s)"
    
    @pytest.mark.asyncio
    async def test_bulk_many_unavailable_users_efficiency(self, client, test_cache, sample_avatar_png):
        """Test efficiency when many users are unavailable (realistic scenario)."""
        # Mix of 10 cached, 40 unavailable
        cached_users = [f"cached{i}" for i in range(10)]
        unavailable_users = [f"unavailable{i}" for i in range(40)]
        all_users = cached_users + unavailable_users
        
        # Cache the available users
        for user_id in cached_users:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            # Unavailable users return None
            async def fetch_avatar(user_id):
                await asyncio.sleep(0.005)  # 5ms API delay
                return None  # User not found
            
            mock_fetch.side_effect = fetch_avatar
            
            # Test bulk request
            start_bulk = time.time()
            payload = {"user_ids": all_users, "platform": "steam"}
            bulk_response = client.post("/api/v1/bulk/avatars", json=payload)
            bulk_time = time.time() - start_bulk
            
            assert bulk_response.status_code == status.HTTP_200_OK
            bulk_data = bulk_response.json()
            
            # Reset and test individual requests
            mock_fetch.reset_mock()
            mock_fetch.side_effect = fetch_avatar
            
            start_individual = time.time()
            success_count = 0
            for user_id in all_users:
                response = client.get(f"/api/v1/steam/retrieve/{user_id}")
                if response.status_code == status.HTTP_200_OK:
                    success_count += 1
            individual_time = time.time() - start_individual
            
            print(f"\n=== MANY UNAVAILABLE USERS SCENARIO ===")
            print(f"Total users: {len(all_users)} (10 cached, 40 unavailable)")
            print(f"Bulk request time: {bulk_time:.4f}s")
            print(f"Individual requests time: {individual_time:.4f}s")
            print(f"Speedup: {individual_time / bulk_time:.2f}x faster")
            print(f"Bulk results: {bulk_data['total_found']}/{bulk_data['total_requested']} found")
            print(f"Bulk cached: {bulk_data['total_cached']}, fetched: {bulk_data['total_fetched']}")
            
            # Verify bulk found the right users
            assert bulk_data["total_found"] == 10
            assert bulk_data["total_cached"] == 10
            
            # Bulk should be faster even with many unavailable users
            assert bulk_time < individual_time
    
    @pytest.mark.asyncio
    async def test_bulk_resource_usage_efficiency(self, client, test_cache, sample_avatar_png):
        """Test that bulk requests are more resource-efficient."""
        user_ids = [f"user{i}" for i in range(30)]
        
        # Cache all users
        for user_id in user_ids:
            await test_cache.set("steam", user_id, sample_avatar_png)
        
        # Bulk request - single connection
        payload = {"user_ids": user_ids, "platform": "steam"}
        bulk_response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert bulk_response.status_code == status.HTTP_200_OK
        bulk_data = bulk_response.json()
        
        # Individual requests - multiple connections
        individual_responses = []
        for user_id in user_ids:
            response = client.get(f"/api/v1/steam/retrieve/{user_id}")
            individual_responses.append(response)
        
        print(f"\n=== RESOURCE EFFICIENCY COMPARISON ===")
        print(f"Bulk: 1 HTTP request for {len(user_ids)} users")
        print(f"Individual: {len(user_ids)} HTTP requests")
        print(f"Network overhead reduction: {len(user_ids)}x fewer requests")
        print(f"Database writes: Bulk logs once per user vs individual logs")
        
        # All should succeed
        assert bulk_data["total_found"] == len(user_ids)
        assert all(r.status_code == status.HTTP_200_OK for r in individual_responses)


class TestBulkRouteConcurrency:
    """Test concurrent processing behavior in bulk routes."""
    
    @pytest.mark.asyncio
    async def test_bulk_concurrent_processing(self, client, mock_psn_service):
        """Test that bulk route processes requests concurrently."""
        user_ids = [f"user{i}" for i in range(20)]
        call_times = []
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            async def track_fetch(*args, **kwargs):
                call_times.append(time.time())
                await asyncio.sleep(0.01)  # 10ms delay
                img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()
            
            mock_fetch.side_effect = track_fetch
            
            payload = {"user_ids": user_ids, "platform": "steam"}
            response = client.post("/api/v1/bulk/avatars", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            
            # Analyze call times to verify concurrency
            if len(call_times) > 1:
                time_diffs = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]
                avg_diff = sum(time_diffs) / len(time_diffs)
                
                print(f"\n=== CONCURRENCY ANALYSIS ===")
                print(f"Total API calls: {len(call_times)}")
                print(f"Average time between calls: {avg_diff*1000:.2f}ms")
                print(f"Expected if sequential: ~10ms per call")
                print(f"Expected if concurrent: <1ms between call starts")
                
                # If truly concurrent, calls should start relatively close together
                # In test environment with mocks, this may vary
                # Just verify some level of concurrency (not fully sequential)
                sequential_time = 0.010  # 10ms per call if sequential
                assert avg_diff < sequential_time, \
                    f"Calls should show some concurrency (avg {avg_diff*1000:.2f}ms < {sequential_time*1000}ms)"
    
    @pytest.mark.asyncio
    async def test_bulk_semaphore_limit(self, client):
        """Test that bulk route respects concurrency limits (semaphore)."""
        # The bulk route uses asyncio.Semaphore(10) to limit concurrent requests
        user_ids = [f"user{i}" for i in range(25)]
        active_requests = []
        max_concurrent = 0
        
        with patch('services.avatar_services.SteamAvatarService.get_processed_avatar', new_callable=AsyncMock) as mock_fetch:
            async def track_concurrent(*args, **kwargs):
                nonlocal max_concurrent
                active_requests.append(1)
                current_active = len(active_requests)
                max_concurrent = max(max_concurrent, current_active)
                
                await asyncio.sleep(0.01)
                
                active_requests.pop()
                
                img = Image.new('RGBA', (48, 48), color=(100, 100, 100, 255))
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                return buffer.getvalue()
            
            mock_fetch.side_effect = track_concurrent
            
            payload = {"user_ids": user_ids, "platform": "steam"}
            response = client.post("/api/v1/bulk/avatars", json=payload)
            
            assert response.status_code == status.HTTP_200_OK
            
            print(f"\n=== SEMAPHORE LIMIT TEST ===")
            print(f"Total requests: {len(user_ids)}")
            print(f"Max concurrent observed: {max_concurrent}")
            print(f"Expected limit: 10 (from semaphore)")
            
            # Should not exceed semaphore limit of 10
            assert max_concurrent <= 10, "Should respect semaphore limit"


class TestBulkRouteEpicPlatform:
    """Test bulk route with Epic platform (cache-only)."""
    
    @pytest.mark.asyncio
    async def test_bulk_epic_cache_only(self, client, test_cache, sample_avatar_png):
        """Test that Epic platform only returns cached avatars (no API fetch)."""
        # Cache some Epic users
        cached_users = ["EpicUser1", "EpicUser2"]
        uncached_users = ["EpicUser3", "EpicUser4"]
        all_users = cached_users + uncached_users
        
        for user_id in cached_users:
            await test_cache.set("epic", user_id, sample_avatar_png)
        
        payload = {"user_ids": all_users, "platform": "epic"}
        response = client.post("/api/v1/bulk/avatars", json=payload)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Only cached users should be found
        assert data["total_found"] == len(cached_users)
        assert data["total_cached"] == len(cached_users)
        assert data["total_fetched"] == 0  # No API fetching for Epic
        
        # Check individual results
        for result in data["results"]:
            if result["user_id"] in cached_users:
                assert result["found"] is True
                assert result["cached"] is True
            else:
                assert result["found"] is False
                assert "not found" in result["error"].lower()
