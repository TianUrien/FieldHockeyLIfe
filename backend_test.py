import requests
import unittest
import uuid
import time
import os
import json
from datetime import datetime, timedelta

# Use the public endpoint from the frontend .env file
BASE_URL = "https://bdd291c1-244a-4f95-a238-200c9e7be078.preview.emergentagent.com/api"

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
            "title": "Midfielder Position",
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
        
        # Test enhanced club features
        print("\n===== Testing Enhanced Club Features =====")
        cls.test_enhanced_club_features()
    
    @classmethod
    def test_enhanced_club_features(cls):
        """Test the enhanced club features"""
        
        # Test Application model with optional fields
        print("\n🔍 Testing Application model with optional fields...")
        # Create a new application with optional fields
        application_data = {
            "player_id": cls.player_id,
            "vacancy_id": cls.vacancy_id,
            "cover_letter": "I am very interested in this position and believe my skills would be a great fit."
        }
        
        response = requests.post(f"{BASE_URL}/applications", json=application_data)
        if response.status_code == 400:
            print("✅ Application with same player and vacancy rejected (already applied)")
        elif response.status_code == 200:
            application = response.json()
            # Check that optional fields are present in the response
            if "player_position" in application and "player_location" in application and "player_experience" in application and "vacancy_title" in application:
                print("✅ Application model with optional fields test passed")
            else:
                print("❌ Application model with optional fields test failed: Optional fields not present in response")
                return
        else:
            print(f"❌ Application model with optional fields test failed: {response.status_code} - {response.text}")
            return
            
        # Test updating club profile with enhanced fields
        print("\n🔍 Testing updating club profile with enhanced fields...")
        update_data = {
            "achievements": "3x National Champions, 2x European Cup Finalists",
            "club_story": "Founded in 2010, our club has grown from a small local team to one of the premier hockey clubs in the country.",
            "facilities": "2 artificial turf pitches, modern gym, video analysis room, physiotherapy suite",
            "social_media": {
                "instagram": "testhockeyclub",
                "facebook": "TestHockeyClub",
                "twitter": "TestHockeyClub"
            },
            "website": "https://testhockeyclub.com",
            "phone": "+44 123 456 7890",
            "club_type": "Professional"
        }
        
        response = requests.put(f"{BASE_URL}/clubs/{cls.club_id}", json=update_data)
        if response.status_code == 200:
            club = response.json()
            if (club["achievements"] == update_data["achievements"] and 
                club["club_story"] == update_data["club_story"] and
                club["facilities"] == update_data["facilities"] and
                club["website"] == update_data["website"] and
                club["phone"] == update_data["phone"] and
                club["club_type"] == update_data["club_type"]):
                print("✅ Club profile update with enhanced fields test passed")
            else:
                print("❌ Club profile update with enhanced fields test failed: Profile not updated correctly")
                return
        else:
            print(f"❌ Club profile update with enhanced fields test failed: {response.status_code} - {response.text}")
            return
        
        # Test club logo upload
        print("\n🔍 Testing club logo upload...")
        # Create a simple test image if it doesn't exist
        if not os.path.exists("/app/tests/test_logo.jpg"):
            os.makedirs("/app/tests", exist_ok=True)
            with open("/app/tests/test_logo.jpg", "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"" * 100)  # Simple PNG header
                
        with open("/app/tests/test_logo.jpg", 'rb') as logo_file:
            files = {'file': ('test_logo.jpg', logo_file, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/clubs/{cls.club_id}/logo", files=files)
            
            if response.status_code == 200:
                logo_data = response.json()
                if 'filename' in logo_data:
                    print(f"✅ Club logo upload test passed. Filename: {logo_data['filename']}")
                    
                    # Test logo access
                    logo_url = f"{BASE_URL}/uploads/logos/{logo_data['filename']}"
                    logo_response = requests.get(logo_url)
                    if logo_response.status_code == 200:
                        print(f"✅ Club logo access test passed. URL: {logo_url}")
                    else:
                        print(f"❌ Club logo access test failed: {logo_response.status_code}")
                        return
                else:
                    print("❌ Club logo upload test failed: No filename in response")
                    return
            else:
                print(f"❌ Club logo upload test failed: {response.status_code} - {response.text}")
                return
        
        # Test club gallery image upload
        print("\n🔍 Testing club gallery image upload...")
        # Create a simple test image if it doesn't exist
        if not os.path.exists("/app/tests/test_gallery.jpg"):
            os.makedirs("/app/tests", exist_ok=True)
            with open("/app/tests/test_gallery.jpg", "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"" * 100)  # Simple PNG header
                
        with open("/app/tests/test_gallery.jpg", 'rb') as gallery_file:
            files = {'file': ('test_gallery.jpg', gallery_file, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/clubs/{cls.club_id}/gallery", files=files)
            
            if response.status_code == 200:
                gallery_data = response.json()
                if 'filename' in gallery_data:
                    print(f"✅ Club gallery image upload test passed. Filename: {gallery_data['filename']}")
                    
                    # Test gallery image access
                    gallery_url = f"{BASE_URL}/uploads/club_gallery/{gallery_data['filename']}"
                    gallery_response = requests.get(gallery_url)
                    if gallery_response.status_code == 200:
                        print(f"✅ Club gallery image access test passed. URL: {gallery_url}")
                    else:
                        print(f"❌ Club gallery image access test failed: {gallery_response.status_code}")
                        return
                        
                    # Get updated club to get the gallery image ID
                    club_response = requests.get(f"{BASE_URL}/clubs/{cls.club_id}")
                    if club_response.status_code == 200:
                        club_data = club_response.json()
                        if club_data['gallery_images'] and len(club_data['gallery_images']) > 0:
                            gallery_id = club_data['gallery_images'][0]['id']
                            print(f"✅ Gallery image ID retrieved: {gallery_id}")
                            
                            # Test gallery image deletion
                            print("\n🔍 Testing gallery image deletion...")
                            delete_response = requests.delete(f"{BASE_URL}/clubs/{cls.club_id}/gallery/{gallery_id}")
                            if delete_response.status_code == 200:
                                print("✅ Gallery image deletion test passed")
                            else:
                                print(f"❌ Gallery image deletion test failed: {delete_response.status_code} - {delete_response.text}")
                                return
                        else:
                            print("❌ Gallery image not found in club data")
                            return
                    else:
                        print(f"❌ Failed to get club data: {club_response.status_code}")
                        return
                else:
                    print("❌ Club gallery image upload test failed: No filename in response")
                    return
            else:
                print(f"❌ Club gallery image upload test failed: {response.status_code} - {response.text}")
                return
                
        # Test file type validation
        print("\n🔍 Testing file type validation...")
        # Create a simple text file
        test_invalid_file = "/app/tests/test_invalid.txt"
        with open(test_invalid_file, "w") as f:
            f.write("This is not an image file")
                
        with open(test_invalid_file, 'rb') as invalid_file:
            files = {'file': ('test_invalid.txt', invalid_file, 'text/plain')}
            response = requests.post(f"{BASE_URL}/clubs/{cls.club_id}/gallery", files=files)
            
            if response.status_code == 400:
                print("✅ File type validation test passed - rejected invalid file type")
            else:
                print(f"❌ File type validation test failed: {response.status_code} - {response.text}")
                return
        
        # Test creating a vacancy with enhanced fields
        print("\n🔍 Testing creating a vacancy with enhanced fields...")
        vacancy_data = {
            "club_id": cls.club_id,
            "position": "Forward",
            "title": "Senior Forward Position",
            "description": "We're looking for an experienced forward to join our coaching team.",
            "requirements": "Minimum 5 years playing experience at national level",
            "experience_level": "Professional",
            "location": "London, UK",
            "salary_range": "£30,000-£40,000",
            "contract_type": "Full-time",
            "start_date": "2025-03-01",
            "application_deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "benefits": ["Visa sponsorship", "Accommodation", "Health insurance"],
            "status": "active",
            "priority": "high"
        }
        
        response = requests.post(f"{BASE_URL}/vacancies", json=vacancy_data)
        if response.status_code == 200:
            vacancy = response.json()
            enhanced_vacancy_id = vacancy["id"]
            if (vacancy["title"] == vacancy_data["title"] and 
                vacancy["salary_range"] == vacancy_data["salary_range"] and
                vacancy["contract_type"] == vacancy_data["contract_type"] and
                vacancy["priority"] == vacancy_data["priority"]):
                print(f"✅ Vacancy creation with enhanced fields test passed. Vacancy ID: {enhanced_vacancy_id}")
            else:
                print("❌ Vacancy creation with enhanced fields test failed: Vacancy not created correctly")
                return
        else:
            print(f"❌ Vacancy creation with enhanced fields test failed: {response.status_code} - {response.text}")
            return
        
        # Test club analytics
        print("\n🔍 Testing club analytics...")
        response = requests.get(f"{BASE_URL}/clubs/{cls.club_id}/analytics")
        if response.status_code == 200:
            analytics = response.json()
            if all(key in analytics for key in ["total_vacancies", "active_vacancies", "total_applications", "pending_applications", "total_views"]):
                print(f"✅ Club analytics test passed. Analytics: {json.dumps(analytics, indent=2)}")
            else:
                print("❌ Club analytics test failed: Missing expected analytics fields")
                return
        else:
            print(f"❌ Club analytics test failed: {response.status_code} - {response.text}")
            return
        
        print("\n🎉 All enhanced club features tests completed successfully!")
    
    def test_dummy(self):
        """Dummy test to satisfy unittest runner"""
        pass

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)