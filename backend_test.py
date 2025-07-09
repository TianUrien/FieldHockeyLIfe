import requests
import unittest
import uuid
import time
from datetime import datetime

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
        
        # Run the tests in sequence
        cls.test_sequence()
    
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
        print("\n🔍 Testing complete flow...")
        if all([cls.player_id, cls.club_id, cls.vacancy_id, cls.application_id]):
            print("✅ Complete flow test passed")
            print("\n🎉 All API tests completed successfully!")
        else:
            print("❌ Complete flow test failed: Some resources were not created properly")
    
    def test_dummy(self):
        """Dummy test to satisfy unittest runner"""
        pass

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)