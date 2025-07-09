from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    position: str
    experience_level: str  # "Beginner", "Intermediate", "Advanced", "Professional"
    location: str
    bio: Optional[str] = None
    age: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PlayerCreate(BaseModel):
    name: str
    email: str
    position: str
    experience_level: str
    location: str
    bio: Optional[str] = None
    age: Optional[int] = None

class Club(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    location: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    established_year: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClubCreate(BaseModel):
    name: str
    email: str
    location: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    established_year: Optional[int] = None

class Vacancy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    club_name: str
    position: str
    description: str
    requirements: Optional[str] = None
    experience_level: str  # "Beginner", "Intermediate", "Advanced", "Professional"
    location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VacancyCreate(BaseModel):
    club_id: str
    position: str
    description: str
    requirements: Optional[str] = None
    experience_level: str
    location: str

class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    player_name: str
    vacancy_id: str
    vacancy_position: str
    club_name: str
    status: str = "pending"  # "pending", "accepted", "rejected"
    applied_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationCreate(BaseModel):
    player_id: str
    vacancy_id: str

# Basic routes
@api_router.get("/")
async def root():
    return {"message": "Field Hockey Connect API"}

# Player routes
@api_router.post("/players", response_model=Player)
async def create_player(player: PlayerCreate):
    # Check if email already exists
    existing_player = await db.players.find_one({"email": player.email})
    if existing_player:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    player_dict = player.dict()
    player_obj = Player(**player_dict)
    await db.players.insert_one(player_obj.dict())
    return player_obj

@api_router.get("/players", response_model=List[Player])
async def get_players():
    players = await db.players.find().to_list(1000)
    return [Player(**player) for player in players]

@api_router.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return Player(**player)

# Club routes
@api_router.post("/clubs", response_model=Club)
async def create_club(club: ClubCreate):
    # Check if email already exists
    existing_club = await db.clubs.find_one({"email": club.email})
    if existing_club:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    club_dict = club.dict()
    club_obj = Club(**club_dict)
    await db.clubs.insert_one(club_obj.dict())
    return club_obj

@api_router.get("/clubs", response_model=List[Club])
async def get_clubs():
    clubs = await db.clubs.find().to_list(1000)
    return [Club(**club) for club in clubs]

@api_router.get("/clubs/{club_id}", response_model=Club)
async def get_club(club_id: str):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return Club(**club)

# Vacancy routes
@api_router.post("/vacancies", response_model=Vacancy)
async def create_vacancy(vacancy: VacancyCreate):
    # Get club information
    club = await db.clubs.find_one({"id": vacancy.club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    vacancy_dict = vacancy.dict()
    vacancy_dict["club_name"] = club["name"]
    vacancy_obj = Vacancy(**vacancy_dict)
    await db.vacancies.insert_one(vacancy_obj.dict())
    return vacancy_obj

@api_router.get("/vacancies", response_model=List[Vacancy])
async def get_vacancies():
    vacancies = await db.vacancies.find().sort("created_at", -1).to_list(1000)
    return [Vacancy(**vacancy) for vacancy in vacancies]

@api_router.get("/vacancies/{vacancy_id}", response_model=Vacancy)
async def get_vacancy(vacancy_id: str):
    vacancy = await db.vacancies.find_one({"id": vacancy_id})
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return Vacancy(**vacancy)

@api_router.get("/clubs/{club_id}/vacancies", response_model=List[Vacancy])
async def get_club_vacancies(club_id: str):
    vacancies = await db.vacancies.find({"club_id": club_id}).sort("created_at", -1).to_list(1000)
    return [Vacancy(**vacancy) for vacancy in vacancies]

# Application routes
@api_router.post("/applications", response_model=Application)
async def create_application(application: ApplicationCreate):
    # Check if player exists
    player = await db.players.find_one({"id": application.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Check if vacancy exists
    vacancy = await db.vacancies.find_one({"id": application.vacancy_id})
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Check if application already exists
    existing_app = await db.applications.find_one({
        "player_id": application.player_id,
        "vacancy_id": application.vacancy_id
    })
    if existing_app:
        raise HTTPException(status_code=400, detail="Already applied to this vacancy")
    
    application_dict = application.dict()
    application_dict["player_name"] = player["name"]
    application_dict["vacancy_position"] = vacancy["position"]
    application_dict["club_name"] = vacancy["club_name"]
    
    application_obj = Application(**application_dict)
    await db.applications.insert_one(application_obj.dict())
    return application_obj

@api_router.get("/applications", response_model=List[Application])
async def get_applications():
    applications = await db.applications.find().sort("applied_at", -1).to_list(1000)
    return [Application(**application) for application in applications]

@api_router.get("/players/{player_id}/applications", response_model=List[Application])
async def get_player_applications(player_id: str):
    applications = await db.applications.find({"player_id": player_id}).sort("applied_at", -1).to_list(1000)
    return [Application(**application) for application in applications]

@api_router.get("/clubs/{club_id}/applications", response_model=List[Application])
async def get_club_applications(club_id: str):
    # Get all vacancies for this club
    vacancies = await db.vacancies.find({"club_id": club_id}).to_list(1000)
    vacancy_ids = [vacancy["id"] for vacancy in vacancies]
    
    # Get all applications for these vacancies
    applications = await db.applications.find({"vacancy_id": {"$in": vacancy_ids}}).sort("applied_at", -1).to_list(1000)
    return [Application(**application) for application in applications]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()