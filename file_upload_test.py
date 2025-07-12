import requests
import unittest
import uuid
import os
import time
from datetime import datetime

# Use the public endpoint from the frontend .env file
BASE_URL = "https://44807d79-6707-4de4-af2d-bda42117593c.preview.emergentagent.com/api"

class FileUploadTest:
    def __init__(self):
        # Generate unique identifiers for test data to avoid conflicts
        self.test_id = str(uuid.uuid4())[:8]
        self.player_email = f"player_{self.test_id}@test.com"
        self.password = "TestPassword123!"
        
        # Store created resources for cleanup and further tests
        self.player_id = None
        self.photo_id = None
        self.video_id = None
        
        # Test file paths
        self.test_avatar_path = "/app/tests/test_avatar.jpg"
        self.test_cv_path = "/app/tests/test_cv.pdf"
        self.test_photo_path = "/app/tests/test_photo.jpg"
        self.test_video_path = "/app/tests/test_video.mp4"
        
        # Create test files if they don't exist
        self.create_test_files()
    
    def create_test_files(self):
        """Create test files for upload testing"""
        os.makedirs("/app/tests", exist_ok=True)
        
        # Create a simple test image file (JPEG format)
        if not os.path.exists(self.test_avatar_path):
            with open(self.test_avatar_path, "wb") as f:
                # Minimal valid JPEG file
                f.write(bytes.fromhex('FFD8FFE000104A46494600010101004800480000FFDB004300FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC0000B08000100010101011100FFC4001500010100000000000000000000000000000007FFC4001400010000000000000000000000000000000AFFD9'))
        
        # Create a simple test PDF file
        if not os.path.exists(self.test_cv_path):
            with open(self.test_cv_path, "wb") as f:
                # Minimal valid PDF file
                f.write(b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%EOF\n")
        
        # Create a simple test photo file (JPEG format)
        if not os.path.exists(self.test_photo_path):
            with open(self.test_photo_path, "wb") as f:
                # Minimal valid JPEG file
                f.write(bytes.fromhex('FFD8FFE000104A46494600010101004800480000FFDB004300FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC0000B08000100010101011100FFC4001500010100000000000000000000000000000007FFC4001400010000000000000000000000000000000AFFD9'))
        
        # Create a simple test video file (MP4 format)
        if not os.path.exists(self.test_video_path):
            with open(self.test_video_path, "wb") as f:
                # Minimal MP4 file header (not a valid playable video, but should pass MIME type check)
                f.write(bytes.fromhex('00000018667479706D703432000000006D7034316D70343269736F6D00000000'))
                f.write(b'\x00' * 100)  # Padding
    
    def run_tests(self):
        print("\n===== Starting File Upload Tests =====")
        
        # Test player registration
        print("\n🔍 Testing player registration...")
        player_data = {
            "name": f"Test Player {self.test_id}",
            "email": self.player_email,
            "password": self.password,
            "position": "Forward",
            "experience_level": "Intermediate",
            "location": "Test City",
            "bio": "Test player bio",
            "age": 25
        }
        
        response = requests.post(f"{BASE_URL}/players", json=player_data)
        if response.status_code == 200:
            player = response.json()
            self.player_id = player["id"]
            print(f"✅ Player registration test passed. Player ID: {self.player_id}")
        else:
            print(f"❌ Player registration test failed: {response.status_code} - {response.text}")
            return False
        
        # Test avatar upload
        print("\n🔍 Testing avatar upload...")
        with open(self.test_avatar_path, 'rb') as avatar_file:
            files = {'file': ('test_avatar.jpg', avatar_file, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/players/{self.player_id}/avatar", files=files)
            
            if response.status_code == 200:
                avatar_data = response.json()
                if 'filename' in avatar_data:
                    print(f"✅ Avatar upload test passed. Filename: {avatar_data['filename']}")
                    
                    # Test avatar access
                    avatar_url = f"{BASE_URL}/uploads/avatars/{avatar_data['filename']}"
                    avatar_response = requests.get(avatar_url)
                    if avatar_response.status_code == 200:
                        print(f"✅ Avatar access test passed. URL: {avatar_url}")
                    else:
                        print(f"❌ Avatar access test failed: {avatar_response.status_code}")
                        return False
                else:
                    print("❌ Avatar upload test failed: No filename in response")
                    return False
            else:
                print(f"❌ Avatar upload test failed: {response.status_code} - {response.text}")
                return False
        
        # Test CV upload
        print("\n🔍 Testing CV upload...")
        with open(self.test_cv_path, 'rb') as cv_file:
            files = {'file': ('test_cv.pdf', cv_file, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/players/{self.player_id}/cv", files=files)
            
            if response.status_code == 200:
                cv_data = response.json()
                if 'filename' in cv_data:
                    print(f"✅ CV upload test passed. Filename: {cv_data['filename']}")
                    
                    # Test CV access
                    cv_url = f"{BASE_URL}/uploads/documents/{cv_data['filename']}"
                    cv_response = requests.get(cv_url)
                    if cv_response.status_code == 200:
                        print(f"✅ CV access test passed. URL: {cv_url}")
                    else:
                        print(f"❌ CV access test failed: {cv_response.status_code}")
                        return False
                else:
                    print("❌ CV upload test failed: No filename in response")
                    return False
            else:
                print(f"❌ CV upload test failed: {response.status_code} - {response.text}")
                return False
        
        # Test photo upload
        print("\n🔍 Testing photo upload...")
        with open(self.test_photo_path, 'rb') as photo_file:
            files = {'file': ('test_photo.jpg', photo_file, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/players/{self.player_id}/photos", files=files)
            
            if response.status_code == 200:
                photo_data = response.json()
                if 'filename' in photo_data:
                    print(f"✅ Photo upload test passed. Filename: {photo_data['filename']}")
                    
                    # Test photo access
                    photo_url = f"{BASE_URL}/uploads/photos/{photo_data['filename']}"
                    photo_response = requests.get(photo_url)
                    if photo_response.status_code == 200:
                        print(f"✅ Photo access test passed. URL: {photo_url}")
                    else:
                        print(f"❌ Photo access test failed: {photo_response.status_code}")
                        return False
                    
                    # Get updated player to get the photo ID
                    player_response = requests.get(f"{BASE_URL}/players/{self.player_id}")
                    if player_response.status_code == 200:
                        player_data = player_response.json()
                        if player_data['photos'] and len(player_data['photos']) > 0:
                            self.photo_id = player_data['photos'][0]['id']
                            print(f"✅ Photo ID retrieved: {self.photo_id}")
                        else:
                            print("❌ Photo not found in player data")
                            return False
                    else:
                        print(f"❌ Failed to get player data: {player_response.status_code}")
                        return False
                else:
                    print("❌ Photo upload test failed: No filename in response")
                    return False
            else:
                print(f"❌ Photo upload test failed: {response.status_code} - {response.text}")
                return False
        
        # Test video upload
        print("\n🔍 Testing video upload...")
        with open(self.test_video_path, 'rb') as video_file:
            files = {'file': ('test_video.mp4', video_file, 'video/mp4')}
            response = requests.post(f"{BASE_URL}/players/{self.player_id}/videos", files=files)
            
            if response.status_code == 200:
                video_data = response.json()
                if 'filename' in video_data:
                    print(f"✅ Video upload test passed. Filename: {video_data['filename']}")
                    
                    # Test video access
                    video_url = f"{BASE_URL}/uploads/videos/{video_data['filename']}"
                    video_response = requests.get(video_url)
                    if video_response.status_code == 200:
                        print(f"✅ Video access test passed. URL: {video_url}")
                    else:
                        print(f"❌ Video access test failed: {video_response.status_code}")
                        return False
                    
                    # Get updated player to get the video ID
                    player_response = requests.get(f"{BASE_URL}/players/{self.player_id}")
                    if player_response.status_code == 200:
                        player_data = player_response.json()
                        if player_data['videos'] and len(player_data['videos']) > 0:
                            self.video_id = player_data['videos'][0]['id']
                            print(f"✅ Video ID retrieved: {self.video_id}")
                        else:
                            print("❌ Video not found in player data")
                            return False
                    else:
                        print(f"❌ Failed to get player data: {player_response.status_code}")
                        return False
                else:
                    print("❌ Video upload test failed: No filename in response")
                    return False
            else:
                print(f"❌ Video upload test failed: {response.status_code} - {response.text}")
                return False
        
        # Test photo deletion
        if self.photo_id:
            print("\n🔍 Testing photo deletion...")
            response = requests.delete(f"{BASE_URL}/players/{self.player_id}/photos/{self.photo_id}")
            if response.status_code == 200:
                print("✅ Photo deletion test passed")
            else:
                print(f"❌ Photo deletion test failed: {response.status_code} - {response.text}")
                return False
        
        # Test video deletion
        if self.video_id:
            print("\n🔍 Testing video deletion...")
            response = requests.delete(f"{BASE_URL}/players/{self.player_id}/videos/{self.video_id}")
            if response.status_code == 200:
                print("✅ Video deletion test passed")
            else:
                print(f"❌ Video deletion test failed: {response.status_code} - {response.text}")
                return False
        
        print("\n🎉 All file upload tests completed successfully!")
        return True

if __name__ == "__main__":
    test = FileUploadTest()
    test.run_tests()