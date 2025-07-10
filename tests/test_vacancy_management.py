import requests
import unittest
import uuid
from datetime import datetime, timedelta

# Use the public endpoint from the frontend .env file
BASE_URL = "https://bdd291c1-244a-4f95-a238-200c9e7be078.preview.emergentagent.com/api"

class VacancyManagementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate unique identifiers for test data
        cls.test_id = str(uuid.uuid4())[:8]
        cls.club_email = f"club_{cls.test_id}@test.com"
        cls.password = "TestPassword123!"
        
        # Register a test club
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
            cls.club = response.json()
            cls.club_id = cls.club["id"]
            print(f"✅ Test club created with ID: {cls.club_id}")
        else:
            print(f"❌ Failed to create test club: {response.status_code} - {response.text}")
            raise Exception("Test setup failed")
        
        # Create test vacancies
        cls.vacancies = []
        for i in range(3):
            vacancy_data = {
                "club_id": cls.club_id,
                "position": ["Forward", "Midfielder", "Defender"][i],
                "title": f"Test Vacancy {i+1}",
                "description": f"Test vacancy description {i+1}",
                "requirements": f"Test requirements {i+1}",
                "experience_level": ["Beginner", "Intermediate", "Advanced"][i],
                "location": "Test City",
                "status": "active"
            }
            
            response = requests.post(f"{BASE_URL}/vacancies", json=vacancy_data)
            if response.status_code == 200:
                vacancy = response.json()
                cls.vacancies.append(vacancy)
                print(f"✅ Test vacancy {i+1} created with ID: {vacancy['id']}")
            else:
                print(f"❌ Failed to create test vacancy {i+1}: {response.status_code} - {response.text}")
                raise Exception("Test setup failed")
    
    def test_01_edit_vacancy(self):
        """Test editing a vacancy"""
        print("\n🔍 Testing vacancy editing...")
        
        # Get the first vacancy
        vacancy = self.vacancies[0]
        
        # Update data
        update_data = {
            "title": f"Updated Vacancy {self.test_id}",
            "description": "Updated description",
            "requirements": "Updated requirements",
            "experience_level": "Professional",
            "location": "Updated City",
            "status": "paused"
        }
        
        response = requests.put(f"{BASE_URL}/vacancies/{vacancy['id']}", json=update_data)
        
        self.assertEqual(response.status_code, 200, f"Failed to update vacancy: {response.text}")
        
        updated_vacancy = response.json()
        
        # Verify the updates
        self.assertEqual(updated_vacancy["title"], update_data["title"])
        self.assertEqual(updated_vacancy["description"], update_data["description"])
        self.assertEqual(updated_vacancy["requirements"], update_data["requirements"])
        self.assertEqual(updated_vacancy["experience_level"], update_data["experience_level"])
        self.assertEqual(updated_vacancy["location"], update_data["location"])
        self.assertEqual(updated_vacancy["status"], update_data["status"])
        
        print("✅ Vacancy editing test passed")
    
    def test_02_change_vacancy_status(self):
        """Test changing vacancy status"""
        print("\n🔍 Testing vacancy status changes...")
        
        # Get the second vacancy
        vacancy = self.vacancies[1]
        
        # Test all status options
        statuses = ["active", "paused", "draft", "closed"]
        
        for status in statuses:
            update_data = {"status": status}
            
            response = requests.put(f"{BASE_URL}/vacancies/{vacancy['id']}", json=update_data)
            
            self.assertEqual(response.status_code, 200, f"Failed to update vacancy status to {status}: {response.text}")
            
            updated_vacancy = response.json()
            self.assertEqual(updated_vacancy["status"], status, f"Status not updated to {status}")
            
            print(f"✅ Successfully changed vacancy status to {status}")
        
        print("✅ Vacancy status change test passed")
    
    def test_03_delete_vacancy(self):
        """Test deleting a vacancy"""
        print("\n🔍 Testing vacancy deletion...")
        
        # Get the third vacancy
        vacancy = self.vacancies[2]
        
        response = requests.delete(f"{BASE_URL}/vacancies/{vacancy['id']}")
        
        self.assertEqual(response.status_code, 200, f"Failed to delete vacancy: {response.text}")
        
        # Verify the vacancy is deleted
        response = requests.get(f"{BASE_URL}/vacancies/{vacancy['id']}")
        self.assertEqual(response.status_code, 404, "Vacancy still exists after deletion")
        
        print("✅ Vacancy deletion test passed")
    
    def test_04_club_vacancies_endpoint(self):
        """Test the club vacancies endpoint"""
        print("\n🔍 Testing club vacancies endpoint...")
        
        response = requests.get(f"{BASE_URL}/clubs/{self.club_id}/vacancies")
        
        self.assertEqual(response.status_code, 200, f"Failed to get club vacancies: {response.text}")
        
        vacancies = response.json()
        self.assertIsInstance(vacancies, list, "Response is not a list")
        
        # We should have at least 2 vacancies (one was deleted)
        self.assertGreaterEqual(len(vacancies), 2, "Expected at least 2 vacancies")
        
        print(f"✅ Club vacancies endpoint test passed - found {len(vacancies)} vacancies")
    
    def test_05_create_vacancy_with_all_fields(self):
        """Test creating a vacancy with all available fields"""
        print("\n🔍 Testing creating a vacancy with all fields...")
        
        vacancy_data = {
            "club_id": self.club_id,
            "position": "Goalkeeper",
            "title": f"Complete Vacancy {self.test_id}",
            "description": "Detailed description of the position",
            "requirements": "Specific requirements for the position",
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
        
        self.assertEqual(response.status_code, 200, f"Failed to create vacancy: {response.text}")
        
        vacancy = response.json()
        
        # Verify all fields
        self.assertEqual(vacancy["title"], vacancy_data["title"])
        self.assertEqual(vacancy["position"], vacancy_data["position"])
        self.assertEqual(vacancy["description"], vacancy_data["description"])
        self.assertEqual(vacancy["requirements"], vacancy_data["requirements"])
        self.assertEqual(vacancy["experience_level"], vacancy_data["experience_level"])
        self.assertEqual(vacancy["location"], vacancy_data["location"])
        self.assertEqual(vacancy["salary_range"], vacancy_data["salary_range"])
        self.assertEqual(vacancy["contract_type"], vacancy_data["contract_type"])
        self.assertEqual(vacancy["start_date"], vacancy_data["start_date"])
        self.assertEqual(vacancy["status"], vacancy_data["status"])
        self.assertEqual(vacancy["priority"], vacancy_data["priority"])
        self.assertEqual(vacancy["benefits"], vacancy_data["benefits"])
        
        print("✅ Creating vacancy with all fields test passed")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)