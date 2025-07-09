from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
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
from passlib.context import CryptContext
import shutil
import magic
from urllib.parse import quote


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# File upload settings
UPLOAD_DIR = ROOT_DIR / "uploads"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}

# File size limits (in bytes)
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 300 * 1024 * 1024  # 300MB (increased for larger videos)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    # Increase file upload size limit to 300MB
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware to handle large file uploads
from fastapi.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Configure upload size limit
import uvicorn
uvicorn.config.LOGGING_CONFIG["loggers"]["uvicorn.access"]["propagate"] = False

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Custom StaticFiles to handle video content properly
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.requests import Request
import os

class VideoStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
            if path.endswith(('.mp4', '.mov', '.avi')):
                # Set proper headers for video files
                response.headers["Accept-Ranges"] = "bytes"
                response.headers["Cache-Control"] = "no-cache"
            return response
        except Exception:
            return await super().get_response(path, scope)

# Serve uploaded files through the API router with video support
app.mount("/api/uploads", VideoStaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validate_file_type(file_content: bytes, allowed_types: set) -> bool:
    """Validate file type using python-magic"""
    try:
        # Try to determine MIME type using python-magic
        mime = magic.from_buffer(file_content, mime=True)
        return mime in allowed_types
    except:
        # If magic fails, return True to allow upload (basic validation)
        # In production, you might want stricter validation
        return True

def save_uploaded_file(file: UploadFile, directory: str, max_size: int, allowed_types: set) -> str:
    """Save uploaded file and return filename"""
    # Read file content
    file_content = file.file.read()
    file.file.seek(0)  # Reset file pointer
    
    # Validate file size
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB")
    
    # Basic file extension validation (more lenient approach)
    file_extension = Path(file.filename).suffix.lower()
    
    # Check file extension instead of magic for more reliable validation
    if directory == "avatars":
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    elif directory == "documents":
        allowed_extensions = {'.pdf', '.doc', '.docx'}
    elif directory == "photos":
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    elif directory == "videos":
        allowed_extensions = {'.mp4', '.mov', '.avi'}
    else:
        allowed_extensions = set()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}")
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create directory if it doesn't exist
    upload_path = UPLOAD_DIR / directory
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = upload_path / unique_filename
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    return unique_filename


# Define Models
class MediaFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    country: Optional[str] = None
    position: str
    experience_level: str  # "Beginner", "Intermediate", "Advanced", "Professional"
    location: str
    bio: Optional[str] = None
    age: Optional[int] = None
    avatar: Optional[str] = None  # filename
    cv_document: Optional[str] = None  # filename
    photos: List[MediaFile] = []
    videos: List[MediaFile] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PlayerCreate(BaseModel):
    name: str
    email: str
    password: str
    country: Optional[str] = None
    position: str
    experience_level: str
    location: str
    bio: Optional[str] = None
    age: Optional[int] = None

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    position: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None

class PlayerLogin(BaseModel):
    email: str
    password: str

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
    password: str
    location: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    established_year: Optional[int] = None

class ClubLogin(BaseModel):
    email: str
    password: str

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

# Authentication routes
@api_router.post("/players/login", response_model=Player)
async def login_player(credentials: PlayerLogin):
    # Find player by email
    player_data = await db.players.find_one({"email": credentials.email})
    if not player_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, player_data.get("password_hash")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Remove password_hash from response
    player_data.pop("password_hash", None)
    return Player(**player_data)

@api_router.post("/clubs/login", response_model=Club)
async def login_club(credentials: ClubLogin):
    # Find club by email
    club_data = await db.clubs.find_one({"email": credentials.email})
    if not club_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, club_data.get("password_hash")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Remove password_hash from response
    club_data.pop("password_hash", None)
    return Club(**club_data)

# Player routes
@api_router.post("/players", response_model=Player)
async def create_player(player: PlayerCreate):
    # Check if email already exists
    existing_player = await db.players.find_one({"email": player.email})
    if existing_player:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = get_password_hash(player.password)
    
    # Create player data
    player_dict = player.dict()
    player_dict.pop("password")  # Remove plain password
    player_dict["password_hash"] = password_hash
    player_dict["photos"] = []
    player_dict["videos"] = []
    
    player_obj = Player(**{k: v for k, v in player_dict.items() if k != "password_hash"})
    
    # Save to database with password hash
    await db.players.insert_one({**player_obj.dict(), "password_hash": password_hash})
    
    return player_obj

@api_router.get("/players", response_model=List[Player])
async def get_players():
    players = await db.players.find().to_list(1000)
    # Remove password_hash from all players
    for player in players:
        player.pop("password_hash", None)
    return [Player(**player) for player in players]

@api_router.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    player.pop("password_hash", None)
    return Player(**player)

@api_router.put("/players/{player_id}", response_model=Player)
async def update_player(player_id: str, player_update: PlayerUpdate):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in player_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.players.update_one({"id": player_id}, {"$set": update_data})
    
    # Return updated player
    updated_player = await db.players.find_one({"id": player_id})
    updated_player.pop("password_hash", None)
    return Player(**updated_player)

# File upload routes
@api_router.post("/players/{player_id}/avatar")
async def upload_avatar(player_id: str, file: UploadFile = File(...)):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Save file
    filename = save_uploaded_file(file, "avatars", MAX_AVATAR_SIZE, ALLOWED_IMAGE_TYPES)
    
    # Update player with new avatar
    await db.players.update_one(
        {"id": player_id}, 
        {"$set": {"avatar": filename, "updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "Avatar uploaded successfully"}

@api_router.post("/players/{player_id}/cv")
async def upload_cv(player_id: str, file: UploadFile = File(...)):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Save file
    filename = save_uploaded_file(file, "documents", MAX_DOCUMENT_SIZE, ALLOWED_DOCUMENT_TYPES)
    
    # Update player with new CV
    await db.players.update_one(
        {"id": player_id}, 
        {"$set": {"cv_document": filename, "updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "CV uploaded successfully"}

@api_router.post("/players/{player_id}/photos")
async def upload_photo(player_id: str, file: UploadFile = File(...)):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Save file
    filename = save_uploaded_file(file, "photos", MAX_PHOTO_SIZE, ALLOWED_IMAGE_TYPES)
    
    # Get file size
    file.file.seek(0)
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Create media file object
    media_file = MediaFile(
        filename=filename,
        original_name=file.filename,
        file_type=file.content_type or "image/jpeg",
        file_size=file_size
    )
    
    # Add to player's photos
    await db.players.update_one(
        {"id": player_id}, 
        {"$push": {"photos": media_file.dict()}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "Photo uploaded successfully"}

@api_router.post("/players/{player_id}/videos")
async def upload_video(player_id: str, file: UploadFile = File(...)):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Save file
    filename = save_uploaded_file(file, "videos", MAX_VIDEO_SIZE, ALLOWED_VIDEO_TYPES)
    
    # Determine file type based on extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension == '.mp4':
        file_type = 'video/mp4'
    elif file_extension == '.mov':
        file_type = 'video/quicktime'
    elif file_extension == '.avi':
        file_type = 'video/x-msvideo'
    else:
        file_type = file.content_type or "video/mp4"
    
    # Get file size
    file.file.seek(0)
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Create media file object
    media_file = MediaFile(
        filename=filename,
        original_name=file.filename,
        file_type=file_type,
        file_size=file_size
    )
    
    # Add to player's videos
    await db.players.update_one(
        {"id": player_id}, 
        {"$push": {"videos": media_file.dict()}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "Video uploaded successfully"}

@api_router.delete("/players/{player_id}/photos/{photo_id}")
async def delete_photo(player_id: str, photo_id: str):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Find and remove photo
    photo_to_remove = None
    for photo in player.get("photos", []):
        if photo["id"] == photo_id:
            photo_to_remove = photo
            break
    
    if not photo_to_remove:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Remove file from filesystem
    file_path = UPLOAD_DIR / "photos" / photo_to_remove["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    await db.players.update_one(
        {"id": player_id}, 
        {"$pull": {"photos": {"id": photo_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Photo deleted successfully"}

@api_router.delete("/players/{player_id}/videos/{video_id}")
async def delete_video(player_id: str, video_id: str):
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Find and remove video
    video_to_remove = None
    for video in player.get("videos", []):
        if video["id"] == video_id:
            video_to_remove = video
            break
    
    if not video_to_remove:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Remove file from filesystem
    file_path = UPLOAD_DIR / "videos" / video_to_remove["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    await db.players.update_one(
        {"id": player_id}, 
        {"$pull": {"videos": {"id": video_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Video deleted successfully"}

# Club routes
@api_router.post("/clubs", response_model=Club)
async def create_club(club: ClubCreate):
    # Check if email already exists
    existing_club = await db.clubs.find_one({"email": club.email})
    if existing_club:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = get_password_hash(club.password)
    
    # Create club data
    club_dict = club.dict()
    club_dict.pop("password")  # Remove plain password
    club_dict["password_hash"] = password_hash
    
    club_obj = Club(**{k: v for k, v in club_dict.items() if k != "password_hash"})
    
    # Save to database with password hash
    await db.clubs.insert_one({**club_obj.dict(), "password_hash": password_hash})
    
    return club_obj

@api_router.get("/clubs", response_model=List[Club])
async def get_clubs():
    clubs = await db.clubs.find().to_list(1000)
    # Remove password_hash from all clubs
    for club in clubs:
        club.pop("password_hash", None)
    return [Club(**club) for club in clubs]

@api_router.get("/clubs/{club_id}", response_model=Club)
async def get_club(club_id: str):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    club.pop("password_hash", None)
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