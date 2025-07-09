import requests
import unittest
import uuid
import time
import os
import json
from datetime import datetime, timedelta

# Use the public endpoint from the frontend .env file
BASE_URL = "https://ea34da36-c9b5-4114-83d2-e361afa39702.preview.emergentagent.com/api"

class FieldHockeyConnectAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate unique identifiers for test data to avoid conflicts
        cls.test_id = str(uuid.uuid4())[:8]
        cls.player_email = f"player_{cls.test_id}@test.com"
        cls.club_email = f"club_{cls.test_id}@test.com"
        cls.password = "TestPassword123!"
        
        # Store created resources for cleanup and further tests
        cls.player_id = None
        cls.club_id = None
        cls.vacancy_id = None
        cls.application_id = None
        cls.photo_id = None
        cls.video_id = None
        
        # Test file paths
        cls.test_avatar_path = "/app/tests/test_avatar.jpg"
        cls.test_cv_path = "/app/tests/test_cv.pdf"
        cls.test_photo_path = "/app/tests/test_photo.jpg"
        cls.test_video_path = "/app/tests/test_video.mp4"
        cls.test_logo_path = "/app/tests/test_logo.jpg"
        cls.test_gallery_path = "/app/tests/test_gallery.jpg"
        
        # Create test files if they don't exist
        cls.create_test_files()
        
        # Run the tests in sequence
        cls.test_sequence()
    
    @classmethod
    def create_test_files(cls):
        """Create test files for upload testing"""
        os.makedirs("/app/tests", exist_ok=True)
        
        # Create a simple test image file
        if not os.path.exists(cls.test_avatar_path):
            with open(cls.test_avatar_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)  # Simple PNG header
        
        # Create a simple test PDF file
        if not os.path.exists(cls.test_cv_path):
            with open(cls.test_cv_path, "wb") as f:
                f.write(b"%PDF-1.4\n" + b"\x00" * 100)  # Simple PDF header
        
        # Create a simple test photo file
        if not os.path.exists(cls.test_photo_path):
            with open(cls.test_photo_path, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)  # Simple PNG header
        
        # Create a simple test video file
        if not os.path.exists(cls.test_video_path):
            with open(cls.test_video_path, "wb") as f:
                f.write(b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 100)  # Simple MP4 header
    
    @classmethod
    def test_sequence(cls):
        print("\n===== Starting API Tests =====")
        
        # Test root endpoint
        print("\n🔍 Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200 and response.json()["message"] == "Field Hockey Connect API":
            print("✅ Root endpoint test passed")
        else:
            print(f"❌ Root endpoint test failed: {response.status_code} - {response.text}")
            return
        
        # Test player registration with password
        print("\n🔍 Testing player registration with password...")
        player_data = {
            "name": f"Test Player {cls.test_id}",
            "email": cls.player_email,
            "password": cls.password,
            "position": "Forward",
            "experience_level": "Intermediate",
            "location": "Test City",
            "bio": "Test player bio",
            "age": 25
        }
        
        response = requests.post(f"{BASE_URL}/players", json=player_data)
        if response.status_code == 200:
            player = response.json()
            cls.player_id = player["id"]
            # Check that password is not in the response
            if "password" not in player and "password_hash" not in player:
                print(f"✅ Player registration test passed. Player ID: {cls.player_id}")
                print("✅ Password security check passed - password not visible in response")
            else:
                print("❌ Password security check failed - password visible in response")
                return
        else:
            print(f"❌ Player registration test failed: {response.status_code} - {response.text}")
            return
        
        # Test player login with correct credentials
        print("\n🔍 Testing player login with correct credentials...")
        login_data = {
            "email": cls.player_email,
            "password": cls.password
        }
        
        response = requests.post(f"{BASE_URL}/players/login", json=login_data)
        if response.status_code == 200:
            player = response.json()
            if player["id"] == cls.player_id:
                print("✅ Player login test passed")
                # Check that password is not in the response
                if "password" not in player and "password_hash" not in player:
                    print("✅ Password security check passed - password not visible in response")
                else:
                    print("❌ Password security check failed - password visible in response")
                    return
            else:
                print("❌ Player login test failed: Incorrect player data returned")
                return
        else:
            print(f"❌ Player login test failed: {response.status_code} - {response.text}")
            return
        
        # Test player login with incorrect credentials
        print("\n🔍 Testing player login with incorrect credentials...")
        login_data = {
            "email": cls.player_email,
            "password": "WrongPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/players/login", json=login_data)
        if response.status_code == 401:
            print("✅ Player login with incorrect credentials test passed")
        else:
            print(f"❌ Player login with incorrect credentials test failed: {response.status_code} - {response.text}")
            return
        
        # Test club registration with password
        print("\n🔍 Testing club registration with password...")
        club_data = {
            "name": f"Test Club {cls.test_id}",
            "email": cls.club_email,
            "password": cls.password,
            "location": "Test City",
            "description": "Test club description",
            "contact_info": "test@club.com",
            "established_year": 2000
        }
        
        response = requests.post(f"{BASE_URL}/clubs", json=club_data)
        if response.status_code == 200:
            club = response.json()
            cls.club_id = club["id"]
            # Check that password is not in the response
            if "password" not in club and "password_hash" not in club:
                print(f"✅ Club registration test passed. Club ID: {cls.club_id}")
                print("✅ Password security check passed - password not visible in response")
            else:
                print("❌ Password security check failed - password visible in response")
                return
        else:
            print(f"❌ Club registration test failed: {response.status_code} - {response.text}")
            return
        
        # Test club login with correct credentials
        print("\n🔍 Testing club login with correct credentials...")
        login_data = {
            "email": cls.club_email,
            "password": cls.password
        }
        
        response = requests.post(f"{BASE_URL}/clubs/login", json=login_data)
        if response.status_code == 200:
            club = response.json()
            if club["id"] == cls.club_id:
                print("✅ Club login test passed")
                # Check that password is not in the response
                if "password" not in club and "password_hash" not in club:
                    print("✅ Password security check passed - password not visible in response")
                else:
                    print("❌ Password security check failed - password visible in response")
                    return
            else:
                print("❌ Club login test failed: Incorrect club data returned")
                return
        else:
            print(f"❌ Club login test failed: {response.status_code} - {response.text}")
            return
        
        # Test club login with incorrect credentials
        print("\n🔍 Testing club login with incorrect credentials...")
        login_data = {
            "email": cls.club_email,
            "password": "WrongPassword123!"
        }
        
        response = requests.post(f"{BASE_URL}/clubs/login", json=login_data)
        if response.status_code == 401:
            print("✅ Club login with incorrect credentials test passed")
        else:
            print(f"❌ Club login with incorrect credentials test failed: {response.status_code} - {response.text}")
            return
        
        # Test duplicate email registration for player
        print("\n🔍 Testing duplicate email registration for player...")
        player_data = {
            "name": f"Duplicate Player {cls.test_id}",
            "email": cls.player_email,  # Using the same email
            "password": cls.password,
            "position": "Defender",
            "experience_level": "Advanced",
            "location": "Another City",
            "bio": "Duplicate player bio",
            "age": 30
        }
        
        response = requests.post(f"{BASE_URL}/players", json=player_data)
        if response.status_code == 400:
            print("✅ Duplicate email registration test for player passed")
        else:
            print(f"❌ Duplicate email registration test for player failed: {response.status_code} - {response.text}")
            return
        
        # Test duplicate email registration for club
        print("\n🔍 Testing duplicate email registration for club...")
        club_data = {
            "name": f"Duplicate Club {cls.test_id}",
            "email": cls.club_email,  # Using the same email
            "password": cls.password,
            "location": "Another City",
            "description": "Duplicate club description",
            "contact_info": "duplicate@club.com",
            "established_year": 2010
        }
        
        response = requests.post(f"{BASE_URL}/clubs", json=club_data)
        if response.status_code == 400:
            print("✅ Duplicate email registration test for club passed")
        else:
            print(f"❌ Duplicate email registration test for club failed: {response.status_code} - {response.text}")
            return
        
        # Test creating a vacancy
        print("\n🔍 Testing vacancy creation...")
        vacancy_data = {
            "club_id": cls.club_id,
            "position": "Midfielder",
            "description": "Test vacancy description",
            "requirements": "Test requirements",
            "experience_level": "Intermediate",
            "location": "Test City"
        }
        
        response = requests.post(f"{BASE_URL}/vacancies", json=vacancy_data)
        if response.status_code == 200:
            vacancy = response.json()
            cls.vacancy_id = vacancy["id"]
            print(f"✅ Vacancy creation test passed. Vacancy ID: {cls.vacancy_id}")
        else:
            print(f"❌ Vacancy creation test failed: {response.status_code} - {response.text}")
            return
        
        # Test getting vacancies
        print("\n🔍 Testing get vacancies...")
        response = requests.get(f"{BASE_URL}/vacancies")
        if response.status_code == 200:
            vacancies = response.json()
            if isinstance(vacancies, list):
                print("✅ Get vacancies test passed")
            else:
                print("❌ Get vacancies test failed: Response is not a list")
                return
        else:
            print(f"❌ Get vacancies test failed: {response.status_code} - {response.text}")
            return
        
        # Test getting club vacancies
        print("\n🔍 Testing get club vacancies...")
        response = requests.get(f"{BASE_URL}/clubs/{cls.club_id}/vacancies")
        if response.status_code == 200:
            vacancies = response.json()
            if isinstance(vacancies, list):
                print("✅ Get club vacancies test passed")
            else:
                print("❌ Get club vacancies test failed: Response is not a list")
                return
        else:
            print(f"❌ Get club vacancies test failed: {response.status_code} - {response.text}")
            return
        
        # Test creating an application
        print("\n🔍 Testing application creation...")
        application_data = {
            "player_id": cls.player_id,
            "vacancy_id": cls.vacancy_id
        }
        
        response = requests.post(f"{BASE_URL}/applications", json=application_data)
        if response.status_code == 200:
            application = response.json()
            cls.application_id = application["id"]
            print(f"✅ Application creation test passed. Application ID: {cls.application_id}")
        else:
            print(f"❌ Application creation test failed: {response.status_code} - {response.text}")
            return
        
        # Test getting player applications
        print("\n🔍 Testing get player applications...")
        response = requests.get(f"{BASE_URL}/players/{cls.player_id}/applications")
        if response.status_code == 200:
            applications = response.json()
            if isinstance(applications, list):
                print("✅ Get player applications test passed")
            else:
                print("❌ Get player applications test failed: Response is not a list")
                return
        else:
            print(f"❌ Get player applications test failed: {response.status_code} - {response.text}")
            return
        
        # Test getting club applications
        print("\n🔍 Testing get club applications...")
        response = requests.get(f"{BASE_URL}/clubs/{cls.club_id}/applications")
        if response.status_code == 200:
            applications = response.json()
            if isinstance(applications, list):
                print("✅ Get club applications test passed")
            else:
                print("❌ Get club applications test failed: Response is not a list")
                return
        else:
            print(f"❌ Get club applications test failed: {response.status_code} - {response.text}")
            return
        
        # Test complete flow
        print("\n🔍 Testing complete authentication and application flow...")
        if all([cls.player_id, cls.club_id, cls.vacancy_id, cls.application_id]):
            print("✅ Complete flow test passed")
        else:
            print("❌ Complete flow test failed: Some resources were not created properly")
            return
        
        # Test player profile update
        print("\n🔍 Testing player profile update...")
        update_data = {
            "name": f"Updated Player {cls.test_id}",
            "country": "Test Country",
            "position": "Defender",
            "experience_level": "Advanced",
            "location": "Updated City",
            "bio": "Updated player bio",
            "age": 28
        }
        
        response = requests.put(f"{BASE_URL}/players/{cls.player_id}", json=update_data)
        if response.status_code == 200:
            updated_player = response.json()
            if (updated_player["name"] == update_data["name"] and 
                updated_player["country"] == update_data["country"] and
                updated_player["position"] == update_data["position"]):
                print("✅ Player profile update test passed")
            else:
                print("❌ Player profile update test failed: Profile not updated correctly")
                return
        else:
            print(f"❌ Player profile update test failed: {response.status_code} - {response.text}")
            return
        
        # Test file upload functionality
        print("\n🔍 Testing file upload functionality...")

        # Test avatar upload
        print("\n🔍 Testing avatar upload...")
        with open(cls.test_avatar_path, 'rb') as avatar_file:
            files = {'file': ('test_avatar.jpg', avatar_file, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/players/{cls.player_id}/avatar", files=files)
            
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
                        return
                else:
                    print("❌ Avatar upload test failed: No filename in response")
                    return
            else:
                print(f"❌ Avatar upload test failed: {response.status_code} - {response.text}")
                return

        # Test CV upload
        print("\n🔍 Testing CV upload...")
        with open(cls.test_cv_path, 'rb') as cv_file:
            files = {'file': ('test_cv.pdf', cv_file, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/players/{cls.player_id}/cv", files=files)
            
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
                        return
                else:
                    print("❌ CV upload test failed: No filename in response")
                    return
            else:
                print(f"❌ CV upload test failed: {response.status_code} - {response.text}")
                return

        # Test photo upload
        print("\n🔍 Testing photo upload...")
        with open(cls.test_photo_path, 'rb') as photo_file:
            files = {'file': ('test_photo.jpg', photo_file, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/players/{cls.player_id}/photos", files=files)
            
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
                        return
                        
                    # Get updated player to get the photo ID
                    player_response = requests.get(f"{BASE_URL}/players/{cls.player_id}")
                    if player_response.status_code == 200:
                        player_data = player_response.json()
                        if player_data['photos'] and len(player_data['photos']) > 0:
                            cls.photo_id = player_data['photos'][0]['id']
                            print(f"✅ Photo ID retrieved: {cls.photo_id}")
                        else:
                            print("❌ Photo not found in player data")
                            return
                    else:
                        print(f"❌ Failed to get player data: {player_response.status_code}")
                        return
                else:
                    print("❌ Photo upload test failed: No filename in response")
                    return
            else:
                print(f"❌ Photo upload test failed: {response.status_code} - {response.text}")
                return

        # Test video upload
        print("\n🔍 Testing video upload...")
        with open(cls.test_video_path, 'rb') as video_file:
            files = {'file': ('test_video.mp4', video_file, 'video/mp4')}
            response = requests.post(f"{BASE_URL}/players/{cls.player_id}/videos", files=files)
            
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
                        return
                        
                    # Get updated player to get the video ID
                    player_response = requests.get(f"{BASE_URL}/players/{cls.player_id}")
                    if player_response.status_code == 200:
                        player_data = player_response.json()
                        if player_data['videos'] and len(player_data['videos']) > 0:
                            cls.video_id = player_data['videos'][0]['id']
                            print(f"✅ Video ID retrieved: {cls.video_id}")
                        else:
                            print("❌ Video not found in player data")
                            return
                    else:
                        print(f"❌ Failed to get player data: {player_response.status_code}")
                        return
                else:
                    print("❌ Video upload test failed: No filename in response")
                    return
            else:
                print(f"❌ Video upload test failed: {response.status_code} - {response.text}")
                return

        # Test photo deletion
        if cls.photo_id:
            print("\n🔍 Testing photo deletion...")
            response = requests.delete(f"{BASE_URL}/players/{cls.player_id}/photos/{cls.photo_id}")
            if response.status_code == 200:
                print("✅ Photo deletion test passed")
            else:
                print(f"❌ Photo deletion test failed: {response.status_code} - {response.text}")
                return

        # Test video deletion
        if cls.video_id:
            print("\n🔍 Testing video deletion...")
            response = requests.delete(f"{BASE_URL}/players/{cls.player_id}/videos/{cls.video_id}")
            if response.status_code == 200:
                print("✅ Video deletion test passed")
            else:
                print(f"❌ Video deletion test failed: {response.status_code} - {response.text}")
                return
        
        print("\n🎉 All API tests completed successfully!")
    
    def test_dummy(self):
        """Dummy test to satisfy unittest runner"""
        pass

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)