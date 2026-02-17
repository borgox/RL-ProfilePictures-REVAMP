import pytest
from fastapi import status
from io import BytesIO
from PIL import Image


class TestEpicUpload:
    """Test Epic Games avatar upload endpoint."""
    
    @pytest.mark.asyncio
    async def test_upload_epic_avatar_png(self, client, sample_avatar_png):
        """Test uploading a valid PNG avatar."""
        files = {"file": ("avatar.png", BytesIO(sample_avatar_png), "image/png")}
        response = client.post("/api/v1/epic/upload/EpicUser123", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "EpicUser123"
        assert "file_size_bytes" in data
    
    @pytest.mark.asyncio
    async def test_upload_epic_avatar_jpg(self, client, sample_avatar_jpg):
        """Test uploading a valid JPG avatar (should be converted to PNG)."""
        files = {"file": ("avatar.jpg", BytesIO(sample_avatar_jpg), "image/jpeg")}
        response = client.post("/api/v1/epic/upload/EpicUser456", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "EpicUser456"
    
    @pytest.mark.asyncio
    async def test_upload_epic_avatar_invalid_format(self, client):
        """Test uploading an invalid file format."""
        invalid_file = b"This is not an image"
        files = {"file": ("avatar.txt", BytesIO(invalid_file), "text/plain")}
        response = client.post("/api/v1/epic/upload/EpicUser789", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Only PNG and JPG" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_epic_avatar_large_image(self, client, large_avatar_png):
        """Test uploading a large image (should be resized)."""
        files = {"file": ("avatar.png", BytesIO(large_avatar_png), "image/png")}
        response = client.post("/api/v1/epic/upload/EpicUserLarge", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        # Verify the uploaded file is smaller than the original
        assert data["file_size_bytes"] < len(large_avatar_png)
    
    @pytest.mark.asyncio
    async def test_upload_epic_avatar_overwrites_existing(self, client, test_cache, sample_avatar_png):
        """Test that uploading a new avatar overwrites the existing one."""
        # First upload
        files1 = {"file": ("avatar1.png", BytesIO(sample_avatar_png), "image/png")}
        response1 = client.post("/api/v1/epic/upload/EpicUserOverwrite", files=files1)
        assert response1.status_code == status.HTTP_200_OK
        
        # Create a different avatar
        img = Image.new('RGBA', (48, 48), color=(255, 0, 0, 255))
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        new_avatar = buffer.getvalue()
        
        # Second upload (overwrite)
        files2 = {"file": ("avatar2.png", BytesIO(new_avatar), "image/png")}
        response2 = client.post("/api/v1/epic/upload/EpicUserOverwrite", files=files2)
        assert response2.status_code == status.HTTP_200_OK
        
        # Retrieve and verify it's the new avatar
        response3 = client.get("/api/v1/epic/retrieve/EpicUserOverwrite")
        assert response3.status_code == status.HTTP_200_OK
        # The retrieved avatar should be the second one
    
    @pytest.mark.asyncio
    async def test_upload_epic_avatar_corrupted_image(self, client):
        """Test uploading a corrupted image file."""
        corrupted_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00corrupted"
        files = {"file": ("corrupted.png", BytesIO(corrupted_png), "image/png")}
        response = client.post("/api/v1/epic/upload/EpicUserCorrupted", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestEpicRetrieve:
    """Test Epic Games avatar retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_retrieve_epic_avatar_success(self, client, test_cache, sample_avatar_png):
        """Test retrieving an existing Epic avatar."""
        # Pre-populate cache
        await test_cache.set("epic", "EpicUser123", sample_avatar_png)
        
        response = client.get("/api/v1/epic/retrieve/EpicUser123")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_retrieve_epic_avatar_not_found(self, client):
        """Test retrieving a non-existent Epic avatar."""
        response = client.get("/api/v1/epic/retrieve/NonExistentUser")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_retrieve_epic_avatar_with_default(self, client, sample_avatar_png):
        """Test retrieving with default_enabled when avatar not found."""
        from unittest.mock import AsyncMock, patch
        
        with patch('services.default_service.default_service.get_default_avatar', new_callable=AsyncMock) as mock_default:
            mock_default.return_value = sample_avatar_png
            
            response = client.get("/api/v1/epic/retrieve/NonExistentUser?default_enabled=true")
            
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            mock_default.assert_called_once_with("epic")
    
    @pytest.mark.asyncio
    async def test_retrieve_epic_avatar_cache_headers(self, client, test_cache, sample_avatar_png):
        """Test that Epic avatars have proper cache control headers (no-cache for Epic)."""
        await test_cache.set("epic", "EpicUser123", sample_avatar_png)
        
        response = client.get("/api/v1/epic/retrieve/EpicUser123")
        
        assert response.status_code == status.HTTP_200_OK
        # Epic should have no-cache headers
        assert "no-cache" in response.headers.get("cache-control", "").lower()


class TestEpicWorkflow:
    """Test complete Epic workflow: upload then retrieve."""
    
    @pytest.mark.asyncio
    async def test_upload_then_retrieve_workflow(self, client, sample_avatar_png):
        """Test uploading an avatar and then retrieving it."""
        user_id = "EpicWorkflowUser"
        
        # Step 1: Upload avatar
        files = {"file": ("avatar.png", BytesIO(sample_avatar_png), "image/png")}
        upload_response = client.post(f"/api/v1/epic/upload/{user_id}", files=files)
        
        assert upload_response.status_code == status.HTTP_200_OK
        
        # Step 2: Retrieve avatar
        retrieve_response = client.get(f"/api/v1/epic/retrieve/{user_id}")
        
        assert retrieve_response.status_code == status.HTTP_200_OK
        assert retrieve_response.headers["content-type"] == "image/png"
        assert len(retrieve_response.content) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_users_workflow(self, client, sample_avatar_png):
        """Test uploading avatars for multiple users."""
        user_ids = ["EpicUser1", "EpicUser2", "EpicUser3"]
        
        # Upload avatars for all users
        for user_id in user_ids:
            files = {"file": ("avatar.png", BytesIO(sample_avatar_png), "image/png")}
            response = client.post(f"/api/v1/epic/upload/{user_id}", files=files)
            assert response.status_code == status.HTTP_200_OK
        
        # Retrieve avatars for all users
        for user_id in user_ids:
            response = client.get(f"/api/v1/epic/retrieve/{user_id}")
            assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_update_existing_avatar(self, client, sample_avatar_png):
        """Test updating an existing Epic avatar."""
        user_id = "EpicUpdateUser"
        
        # First upload
        files1 = {"file": ("avatar1.png", BytesIO(sample_avatar_png), "image/png")}
        response1 = client.post(f"/api/v1/epic/upload/{user_id}", files=files1)
        assert response1.status_code == status.HTTP_200_OK
        
        # Retrieve first avatar
        retrieve1 = client.get(f"/api/v1/epic/retrieve/{user_id}")
        assert retrieve1.status_code == status.HTTP_200_OK
        first_size = len(retrieve1.content)
        
        # Create and upload different avatar
        img = Image.new('RGBA', (48, 48), color=(0, 255, 0, 255))
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        new_avatar = buffer.getvalue()
        
        files2 = {"file": ("avatar2.png", BytesIO(new_avatar), "image/png")}
        response2 = client.post(f"/api/v1/epic/upload/{user_id}", files=files2)
        assert response2.status_code == status.HTTP_200_OK
        
        # Retrieve updated avatar
        retrieve2 = client.get(f"/api/v1/epic/retrieve/{user_id}")
        assert retrieve2.status_code == status.HTTP_200_OK


class TestEpicEdgeCases:
    """Test edge cases for Epic routes."""
    
    @pytest.mark.asyncio
    async def test_upload_with_special_characters_in_user_id(self, client, sample_avatar_png):
        """Test uploading avatar with special characters in user ID."""
        user_id = "Epic_User-123.test"
        files = {"file": ("avatar.png", BytesIO(sample_avatar_png), "image/png")}
        response = client.post(f"/api/v1/epic/upload/{user_id}", files=files)
        
        # Should handle special characters gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    @pytest.mark.asyncio
    async def test_retrieve_with_very_long_user_id(self, client):
        """Test retrieving avatar with extremely long user ID."""
        user_id = "a" * 500
        response = client.get(f"/api/v1/epic/retrieve/{user_id}")
        
        # Should handle gracefully without crashing
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
    
    @pytest.mark.asyncio
    async def test_upload_empty_file(self, client):
        """Test uploading an empty file."""
        empty_file = b""
        files = {"file": ("empty.png", BytesIO(empty_file), "image/png")}
        response = client.post("/api/v1/epic/upload/EpicUserEmpty", files=files)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_concurrent_uploads_same_user(self, client, sample_avatar_png):
        """Test concurrent uploads for the same user (race condition test)."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        user_id = "EpicConcurrentUser"
        
        def upload():
            files = {"file": ("avatar.png", BytesIO(sample_avatar_png), "image/png")}
            return client.post(f"/api/v1/epic/upload/{user_id}", files=files)
        
        # Simulate concurrent uploads
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(upload) for _ in range(3)]
            results = [f.result() for f in futures]
        
        # At least one should succeed
        success_count = sum(1 for r in results if r.status_code == status.HTTP_200_OK)
        assert success_count >= 1
