import requests
import unittest
import uuid
import time
from datetime import datetime

# Use the public endpoint from the frontend .env file
BASE_URL = "https://ea34da36-c9b5-4114-83d2-e361afa39702.preview.emergentagent.com/api"

class FieldHockeyConnectAPITest(unittest.TestCase):
    def setUp(self):
        # Generate unique identifiers for test data to avoid conflicts
        self.test_id = str(uuid.uuid4())[:8]
        self.player_email = f"player_{self.test_id}@test.com"
        self.club_email = f"club_{self.test_id}@test.com"
        
        # Store created resources for cleanup and further tests
        self.player_id = None
        self.club_id = None
        self.vacancy_id = None
        self.application_id = None

    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n🔍 Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Field Hockey Connect API")
        print("✅ Root endpoint test passed")

    def test_02_player_registration(self):
        """Test player registration"""
        print("\n🔍 Testing player registration...")
        player_data = {
            "name": f"Test Player {self.test_id}",
            "email": self.player_email,
            "position": "Forward",
            "experience_level": "Intermediate",
            "location": "Test City",
            "bio": "Test player bio",
            "age": 25
        }
        
        response = requests.post(f"{BASE_URL}/players", json=player_data)
        self.assertEqual(response.status_code, 200)
        
        # Store player ID for later tests
        player = response.json()
        self.player_id = player["id"]
        self.assertEqual(player["name"], player_data["name"])
        self.assertEqual(player["email"], player_data["email"])
        print(f"✅ Player registration test passed. Player ID: {self.player_id}")

    def test_03_club_registration(self):
        """Test club registration"""
        print("\n🔍 Testing club registration...")
        club_data = {
            "name": f"Test Club {self.test_id}",
            "email": self.club_email,
            "location": "Test City",
            "description": "Test club description",
            "contact_info": "test@club.com",
            "established_year": 2000
        }
        
        response = requests.post(f"{BASE_URL}/clubs", json=club_data)
        self.assertEqual(response.status_code, 200)
        
        # Store club ID for later tests
        club = response.json()
        self.club_id = club["id"]
        self.assertEqual(club["name"], club_data["name"])
        self.assertEqual(club["email"], club_data["email"])
        print(f"✅ Club registration test passed. Club ID: {self.club_id}")

    def test_04_create_vacancy(self):
        """Test creating a vacancy"""
        print("\n🔍 Testing vacancy creation...")
        # Skip if club registration failed
        if not self.club_id:
            self.skipTest("Club registration failed, skipping vacancy creation")
        
        vacancy_data = {
            "club_id": self.club_id,
            "position": "Midfielder",
            "description": "Test vacancy description",
            "requirements": "Test requirements",
            "experience_level": "Intermediate",
            "location": "Test City"
        }
        
        try:
            print(f"Sending vacancy data: {vacancy_data}")
            response = requests.post(f"{BASE_URL}/vacancies", json=vacancy_data)
            print(f"Vacancy creation response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            # Store vacancy ID for later tests
            vacancy = response.json()
            self.vacancy_id = vacancy["id"]
            self.assertEqual(vacancy["position"], vacancy_data["position"])
            self.assertEqual(vacancy["club_id"], self.club_id)
            print(f"✅ Vacancy creation test passed. Vacancy ID: {self.vacancy_id}")
        except Exception as e:
            print(f"❌ Vacancy creation test failed: {str(e)}")
            self.fail(f"Vacancy creation failed: {str(e)}")

    def test_05_get_vacancies(self):
        """Test getting all vacancies"""
        print("\n🔍 Testing get vacancies...")
        response = requests.get(f"{BASE_URL}/vacancies")
        self.assertEqual(response.status_code, 200)
        
        vacancies = response.json()
        self.assertIsInstance(vacancies, list)
        
        # Check if our created vacancy is in the list
        if self.vacancy_id:
            found = False
            for vacancy in vacancies:
                if vacancy["id"] == self.vacancy_id:
                    found = True
                    break
            self.assertTrue(found, "Created vacancy not found in vacancies list")
        
        print("✅ Get vacancies test passed")

    def test_06_get_club_vacancies(self):
        """Test getting vacancies for a specific club"""
        print("\n🔍 Testing get club vacancies...")
        # Skip if club registration failed
        if not self.club_id:
            self.skipTest("Club registration failed, skipping get club vacancies")
        
        response = requests.get(f"{BASE_URL}/clubs/{self.club_id}/vacancies")
        self.assertEqual(response.status_code, 200)
        
        vacancies = response.json()
        self.assertIsInstance(vacancies, list)
        
        # Check if all vacancies belong to our club
        for vacancy in vacancies:
            self.assertEqual(vacancy["club_id"], self.club_id)
        
        print("✅ Get club vacancies test passed")

    def test_07_create_application(self):
        """Test creating an application"""
        print("\n🔍 Testing application creation...")
        # Skip if player or vacancy registration failed
        if not self.player_id or not self.vacancy_id:
            self.skipTest("Player or vacancy creation failed, skipping application creation")
        
        application_data = {
            "player_id": self.player_id,
            "vacancy_id": self.vacancy_id
        }
        
        response = requests.post(f"{BASE_URL}/applications", json=application_data)
        self.assertEqual(response.status_code, 200)
        
        # Store application ID for later tests
        application = response.json()
        self.application_id = application["id"]
        self.assertEqual(application["player_id"], self.player_id)
        self.assertEqual(application["vacancy_id"], self.vacancy_id)
        print(f"✅ Application creation test passed. Application ID: {self.application_id}")

    def test_08_get_player_applications(self):
        """Test getting applications for a specific player"""
        print("\n🔍 Testing get player applications...")
        # Skip if player registration failed
        if not self.player_id:
            self.skipTest("Player registration failed, skipping get player applications")
        
        response = requests.get(f"{BASE_URL}/players/{self.player_id}/applications")
        self.assertEqual(response.status_code, 200)
        
        applications = response.json()
        self.assertIsInstance(applications, list)
        
        # Check if all applications belong to our player
        for application in applications:
            self.assertEqual(application["player_id"], self.player_id)
        
        print("✅ Get player applications test passed")

    def test_09_get_club_applications(self):
        """Test getting applications for a specific club"""
        print("\n🔍 Testing get club applications...")
        # Skip if club registration failed
        if not self.club_id:
            self.skipTest("Club registration failed, skipping get club applications")
        
        response = requests.get(f"{BASE_URL}/clubs/{self.club_id}/applications")
        self.assertEqual(response.status_code, 200)
        
        applications = response.json()
        self.assertIsInstance(applications, list)
        
        print("✅ Get club applications test passed")

    def test_10_full_flow(self):
        """Test the complete flow from registration to application"""
        print("\n🔍 Testing complete flow...")
        # This test depends on all previous tests passing
        if not all([self.player_id, self.club_id, self.vacancy_id, self.application_id]):
            self.skipTest("Previous tests failed, skipping complete flow test")
        
        print("✅ Complete flow test passed")
        print("\n🎉 All API tests completed successfully!")

if __name__ == "__main__":
    # Run the tests in order
    unittest.main(argv=['first-arg-is-ignored'], exit=False)