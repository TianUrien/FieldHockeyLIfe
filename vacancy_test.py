import requests
import json
import uuid

# Use the public endpoint from the frontend .env file
BASE_URL = "https://44807d79-6707-4de4-af2d-bda42117593c.preview.emergentagent.com/api"

def test_vacancy_creation():
    # Generate unique test ID
    test_id = str(uuid.uuid4())[:8]
    
    # 1. Create a test club
    print("\n1. Creating a test club...")
    club_data = {
        "name": f"Test Club {test_id}",
        "email": f"club_{test_id}@test.com",
        "location": "Test City",
        "description": "Test club description",
        "contact_info": "test@club.com",
        "established_year": 2000
    }
    
    club_response = requests.post(f"{BASE_URL}/clubs", json=club_data)
    print(f"Club creation response status: {club_response.status_code}")
    print(f"Club response content: {club_response.text}")
    
    if club_response.status_code != 200:
        print("❌ Club creation failed, cannot proceed with vacancy test")
        return
    
    club = club_response.json()
    club_id = club["id"]
    print(f"✅ Club created with ID: {club_id}")
    
    # 2. Create a vacancy for the club
    print("\n2. Creating a vacancy...")
    vacancy_data = {
        "club_id": club_id,
        "position": "Midfielder",
        "description": "Test vacancy description",
        "requirements": "Test requirements",
        "experience_level": "Intermediate",
        "location": "Test City"
    }
    
    print(f"Sending vacancy data: {json.dumps(vacancy_data, indent=2)}")
    vacancy_response = requests.post(f"{BASE_URL}/vacancies", json=vacancy_data)
    print(f"Vacancy creation response status: {vacancy_response.status_code}")
    print(f"Vacancy response content: {vacancy_response.text}")
    
    if vacancy_response.status_code == 200:
        vacancy = vacancy_response.json()
        print(f"✅ Vacancy created with ID: {vacancy['id']}")
    else:
        print("❌ Vacancy creation failed")

if __name__ == "__main__":
    test_vacancy_creation()