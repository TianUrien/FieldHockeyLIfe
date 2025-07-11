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
from datetime import datetime, timedelta
from passlib.context import CryptContext
import shutil
import magic
from urllib.parse import quote
from backend.email_service import send_verification_email, send_welcome_email, send_password_reset_email


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
    if directory == "avatars" or directory == "logos":
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    elif directory == "documents":
        allowed_extensions = {'.pdf', '.doc', '.docx'}
    elif directory == "photos" or directory == "club_gallery":
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    elif directory == "videos" or directory == "club_videos":
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

class PlayerProfile(BaseModel):
    """Player profile model without sensitive information"""
    id: str
    name: str
    email: str
    country: Optional[str] = None
    position: str
    experience_level: str
    location: str
    bio: Optional[str] = None
    age: Optional[int] = None
    avatar: Optional[str] = None
    cv_document: Optional[str] = None
    photos: List[MediaFile] = []
    videos: List[MediaFile] = []
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

class ClubProfile(BaseModel):
    """Club profile model without sensitive information"""
    id: str
    name: str
    email: str
    location: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    established_year: Optional[int] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    club_type: Optional[str] = None
    league: Optional[str] = None
    achievements: Optional[str] = None
    club_story: Optional[str] = None
    facilities: Optional[str] = None
    social_media: Optional[dict] = None
    gallery_images: List[MediaFile] = []
    videos: List[MediaFile] = []
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

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
    # Email verification fields
    is_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
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
    # Enhanced club profile fields
    logo: Optional[str] = None  # logo filename
    website: Optional[str] = None
    phone: Optional[str] = None
    club_type: Optional[str] = None  # "Professional", "Amateur", "Youth", "University"
    league: Optional[str] = None
    achievements: Optional[str] = None
    club_story: Optional[str] = None
    facilities: Optional[str] = None
    social_media: Optional[dict] = None  # {"instagram": "", "facebook": "", "twitter": ""}
    gallery_images: List[MediaFile] = []
    videos: List[MediaFile] = []
    # Email verification fields
    is_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ClubCreate(BaseModel):
    name: str
    email: str
    password: str
    location: str
    description: Optional[str] = None
    contact_info: Optional[str] = None
    established_year: Optional[int] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    club_type: Optional[str] = None
    league: Optional[str] = None

class ClubUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    contact_info: Optional[str] = None
    established_year: Optional[int] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    club_type: Optional[str] = None
    league: Optional[str] = None
    achievements: Optional[str] = None
    club_story: Optional[str] = None
    facilities: Optional[str] = None
    social_media: Optional[dict] = None

class ClubLogin(BaseModel):
    email: str
    password: str

# Email verification models
class EmailVerificationRequest(BaseModel):
    token: str
    user_type: str  # "player" or "club"

class ResendVerificationRequest(BaseModel):
    email: str
    user_type: str  # "player" or "club"

class PasswordResetRequest(BaseModel):
    email: str
    user_type: str  # "player" or "club"

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    user_type: str  # "player" or "club"

class Vacancy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    club_id: str
    club_name: str
    # Basic info
    position: str
    title: str  # Job title (can be different from position)
    description: str
    requirements: Optional[str] = None
    experience_level: str  # "Beginner", "Intermediate", "Advanced", "Professional"
    location: str
    # Enhanced fields
    salary_range: Optional[str] = None  # "25000-35000", "Negotiable", etc.
    contract_type: Optional[str] = None  # "Full-time", "Part-time", "Seasonal", "Contract"
    start_date: Optional[str] = None
    application_deadline: Optional[datetime] = None
    benefits: List[str] = []  # ["Visa", "Accommodation", "Transport", "Insurance", etc.]
    status: str = "active"  # "draft", "active", "paused", "closed"
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    # Analytics
    views_count: int = 0
    applications_count: int = 0
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

class VacancyCreate(BaseModel):
    club_id: str
    position: str
    title: str
    description: str
    requirements: Optional[str] = None
    experience_level: str
    location: str
    salary_range: Optional[str] = None
    contract_type: Optional[str] = None
    start_date: Optional[str] = None
    application_deadline: Optional[datetime] = None
    benefits: List[str] = []
    status: str = "active"
    priority: str = "normal"

class VacancyUpdate(BaseModel):
    position: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    contract_type: Optional[str] = None
    start_date: Optional[str] = None
    application_deadline: Optional[datetime] = None
    benefits: Optional[List[str]] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str
    player_name: str
    player_position: Optional[str] = None  # Made optional for backward compatibility
    player_location: Optional[str] = None  # Made optional for backward compatibility
    player_experience: Optional[str] = None  # Made optional for backward compatibility
    vacancy_id: str
    vacancy_title: Optional[str] = None  # Made optional for backward compatibility
    vacancy_position: str
    club_name: str
    # Enhanced application fields
    status: str = "pending"  # "pending", "reviewed", "shortlisted", "accepted", "rejected"
    priority: str = "normal"  # "low", "normal", "high"
    rating: Optional[int] = None  # 1-5 star rating from club
    notes: Optional[str] = None  # Club notes about the application
    cover_letter: Optional[str] = None  # Player's cover letter
    reviewed_by: Optional[str] = None  # Club member who reviewed
    reviewed_at: Optional[datetime] = None
    # Metadata
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationCreate(BaseModel):
    player_id: str
    vacancy_id: str
    cover_letter: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    reviewed_by: Optional[str] = None

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
    
    # Check if email is verified
    if not player_data.get("is_verified", False):
        raise HTTPException(status_code=403, detail="Please verify your email address before logging in")
    
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
    
    # Check if email is verified
    if not club_data.get("is_verified", False):
        raise HTTPException(status_code=403, detail="Please verify your email address before logging in")
    
    # Remove password_hash from response
    club_data.pop("password_hash", None)
    return Club(**club_data)

# Player routes
@api_router.post("/players")
async def create_player(player: PlayerCreate):
    # Check if email already exists
    existing_player = await db.players.find_one({"email": player.email})
    if existing_player:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = get_password_hash(player.password)
    
    # Generate verification token
    verification_token = str(uuid.uuid4())
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Create player data
    player_dict = player.dict()
    player_dict.pop("password")  # Remove plain password
    player_dict["password_hash"] = password_hash
    player_dict["photos"] = []
    player_dict["videos"] = []
    player_dict["is_verified"] = False
    player_dict["verification_token"] = verification_token
    player_dict["verification_token_expires"] = verification_expires
    
    player_obj = Player(**{k: v for k, v in player_dict.items() if k != "password_hash"})
    
    # Save to database with password hash
    await db.players.insert_one({**player_obj.dict(), "password_hash": password_hash})
    
    # Send verification email
    email_sent = send_verification_email(player.email, verification_token, "player", player.name)
    
    if not email_sent:
        # If email sending fails, still allow registration but warn user
        logging.warning(f"Failed to send verification email to {player.email}")
        return {"message": "Account created successfully, but verification email could not be sent. Please contact support."}
    
    return {"message": "Account created successfully! Please check your email to verify your account."}

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

@api_router.post("/clubs")
async def create_club(club: ClubCreate):
    # Check if email already exists
    existing_club = await db.clubs.find_one({"email": club.email})
    if existing_club:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = get_password_hash(club.password)
    
    # Generate verification token
    verification_token = str(uuid.uuid4())
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Create club data
    club_dict = club.dict()
    club_dict.pop("password")  # Remove plain password
    club_dict["password_hash"] = password_hash
    club_dict["gallery_images"] = []
    club_dict["videos"] = []
    club_dict["social_media"] = {}
    club_dict["is_verified"] = False
    club_dict["verification_token"] = verification_token
    club_dict["verification_token_expires"] = verification_expires
    
    club_obj = Club(**{k: v for k, v in club_dict.items() if k != "password_hash"})
    
    # Save to database with password hash
    await db.clubs.insert_one({**club_obj.dict(), "password_hash": password_hash})
    
    # Send verification email
    email_sent = send_verification_email(club.email, verification_token, "club", club.name)
    
    if not email_sent:
        # If email sending fails, still allow registration but warn user
        logging.warning(f"Failed to send verification email to {club.email}")
        return {"message": "Account created successfully, but verification email could not be sent. Please contact support."}
    
    return {"message": "Account created successfully! Please check your email to verify your account."}

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

@api_router.put("/clubs/{club_id}", response_model=Club)
async def update_club(club_id: str, club_update: ClubUpdate):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in club_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.clubs.update_one({"id": club_id}, {"$set": update_data})
    
    # Return updated club
    updated_club = await db.clubs.find_one({"id": club_id})
    updated_club.pop("password_hash", None)
    return Club(**updated_club)

# Club file upload routes
@api_router.post("/clubs/{club_id}/logo")
async def upload_club_logo(club_id: str, file: UploadFile = File(...)):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Save file
    filename = save_uploaded_file(file, "logos", MAX_AVATAR_SIZE, ALLOWED_IMAGE_TYPES)
    
    # Update club with new logo
    await db.clubs.update_one(
        {"id": club_id}, 
        {"$set": {"logo": filename, "updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "Logo uploaded successfully"}

@api_router.post("/clubs/{club_id}/gallery")
async def upload_club_gallery_image(club_id: str, file: UploadFile = File(...)):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Save file
    filename = save_uploaded_file(file, "club_gallery", MAX_PHOTO_SIZE, ALLOWED_IMAGE_TYPES)
    
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
    
    # Add to club's gallery
    await db.clubs.update_one(
        {"id": club_id}, 
        {"$push": {"gallery_images": media_file.dict()}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "Gallery image uploaded successfully"}

@api_router.post("/clubs/{club_id}/videos")
async def upload_club_video(club_id: str, file: UploadFile = File(...)):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Save file
    filename = save_uploaded_file(file, "club_videos", MAX_VIDEO_SIZE, ALLOWED_VIDEO_TYPES)
    
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
    
    # Add to club's videos
    await db.clubs.update_one(
        {"id": club_id}, 
        {"$push": {"videos": media_file.dict()}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"filename": filename, "message": "Video uploaded successfully"}

@api_router.delete("/clubs/{club_id}/gallery/{image_id}")
async def delete_club_gallery_image(club_id: str, image_id: str):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Find and remove image
    image_to_remove = None
    for image in club.get("gallery_images", []):
        if image["id"] == image_id:
            image_to_remove = image
            break
    
    if not image_to_remove:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Remove file from filesystem
    file_path = UPLOAD_DIR / "club_gallery" / image_to_remove["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    await db.clubs.update_one(
        {"id": club_id}, 
        {"$pull": {"gallery_images": {"id": image_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Gallery image deleted successfully"}

@api_router.delete("/clubs/{club_id}/videos/{video_id}")
async def delete_club_video(club_id: str, video_id: str):
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Find and remove video
    video_to_remove = None
    for video in club.get("videos", []):
        if video["id"] == video_id:
            video_to_remove = video
            break
    
    if not video_to_remove:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Remove file from filesystem
    file_path = UPLOAD_DIR / "club_videos" / video_to_remove["filename"]
    if file_path.exists():
        file_path.unlink()
    
    # Remove from database
    await db.clubs.update_one(
        {"id": club_id}, 
        {"$pull": {"videos": {"id": video_id}}, "$set": {"updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Club video deleted successfully"}

# Vacancy routes
@api_router.post("/vacancies", response_model=Vacancy)
async def create_vacancy(vacancy: VacancyCreate):
    # Get club information
    club = await db.clubs.find_one({"id": vacancy.club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    vacancy_dict = vacancy.dict()
    vacancy_dict["club_name"] = club["name"]
    
    # Set published_at if status is active
    if vacancy_dict.get("status") == "active":
        vacancy_dict["published_at"] = datetime.utcnow()
    
    vacancy_obj = Vacancy(**vacancy_dict)
    await db.vacancies.insert_one(vacancy_obj.dict())
    return vacancy_obj

@api_router.get("/vacancies", response_model=List[Vacancy])
async def get_vacancies(
    status: Optional[str] = None,
    position: Optional[str] = None,
    experience_level: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100
):
    # Build filter query
    filter_query = {}
    if status:
        filter_query["status"] = status
    if position:
        filter_query["position"] = position
    if experience_level:
        filter_query["experience_level"] = experience_level
    if location:
        filter_query["location"] = {"$regex": location, "$options": "i"}
    
    # Only show active vacancies for public listing (unless status is specifically requested)
    if not status:
        filter_query["status"] = "active"
    
    vacancies = await db.vacancies.find(filter_query).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Increment view count for active vacancies
    for vacancy in vacancies:
        if vacancy.get("status") == "active":
            await db.vacancies.update_one(
                {"id": vacancy["id"]}, 
                {"$inc": {"views_count": 1}}
            )
    
    return [Vacancy(**vacancy) for vacancy in vacancies]

@api_router.get("/vacancies/{vacancy_id}", response_model=Vacancy)
async def get_vacancy(vacancy_id: str):
    vacancy = await db.vacancies.find_one({"id": vacancy_id})
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Increment view count
    await db.vacancies.update_one(
        {"id": vacancy_id}, 
        {"$inc": {"views_count": 1}}
    )
    
    return Vacancy(**vacancy)

@api_router.put("/vacancies/{vacancy_id}", response_model=Vacancy)
async def update_vacancy(vacancy_id: str, vacancy_update: VacancyUpdate):
    vacancy = await db.vacancies.find_one({"id": vacancy_id})
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in vacancy_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Set published_at if status changes to active
    if update_data.get("status") == "active" and vacancy.get("status") != "active":
        update_data["published_at"] = datetime.utcnow()
    
    await db.vacancies.update_one({"id": vacancy_id}, {"$set": update_data})
    
    # Return updated vacancy
    updated_vacancy = await db.vacancies.find_one({"id": vacancy_id})
    return Vacancy(**updated_vacancy)

@api_router.delete("/vacancies/{vacancy_id}")
async def delete_vacancy(vacancy_id: str):
    vacancy = await db.vacancies.find_one({"id": vacancy_id})
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Delete all applications for this vacancy
    await db.applications.delete_many({"vacancy_id": vacancy_id})
    
    # Delete the vacancy
    await db.vacancies.delete_one({"id": vacancy_id})
    
    return {"message": "Vacancy deleted successfully"}

@api_router.get("/clubs/{club_id}/vacancies", response_model=List[Vacancy])
async def get_club_vacancies(
    club_id: str,
    status: Optional[str] = None,
    limit: int = 100
):
    filter_query = {"club_id": club_id}
    if status:
        filter_query["status"] = status
    
    vacancies = await db.vacancies.find(filter_query).sort("created_at", -1).limit(limit).to_list(limit)
    return [Vacancy(**vacancy) for vacancy in vacancies]

@api_router.get("/clubs/{club_id}/analytics")
async def get_club_analytics(club_id: str):
    # Get club vacancies stats
    total_vacancies = await db.vacancies.count_documents({"club_id": club_id})
    active_vacancies = await db.vacancies.count_documents({"club_id": club_id, "status": "active"})
    
    # Get application stats
    club_vacancies = await db.vacancies.find({"club_id": club_id}).to_list(1000)
    vacancy_ids = [v["id"] for v in club_vacancies]
    
    total_applications = await db.applications.count_documents({"vacancy_id": {"$in": vacancy_ids}})
    pending_applications = await db.applications.count_documents({
        "vacancy_id": {"$in": vacancy_ids},
        "status": "pending"
    })
    
    # Calculate total views
    total_views = sum(vacancy.get("views_count", 0) for vacancy in club_vacancies)
    
    return {
        "total_vacancies": total_vacancies,
        "active_vacancies": active_vacancies,
        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "total_views": total_views,
        "avg_applications_per_vacancy": round(total_applications / max(total_vacancies, 1), 2)
    }

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
    application_dict["player_position"] = player["position"]
    application_dict["player_location"] = player["location"]
    application_dict["player_experience"] = player["experience_level"]
    application_dict["vacancy_title"] = vacancy.get("title", vacancy["position"])
    application_dict["vacancy_position"] = vacancy["position"]
    application_dict["club_name"] = vacancy["club_name"]
    
    application_obj = Application(**application_dict)
    await db.applications.insert_one(application_obj.dict())
    
    # Increment application count for vacancy
    await db.vacancies.update_one(
        {"id": application.vacancy_id},
        {"$inc": {"applications_count": 1}}
    )
    
    return application_obj

@api_router.get("/applications", response_model=List[Application])
async def get_applications(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    player_id: Optional[str] = None,
    vacancy_id: Optional[str] = None,
    limit: int = 100
):
    filter_query = {}
    if status:
        filter_query["status"] = status
    if priority:
        filter_query["priority"] = priority
    if player_id:
        filter_query["player_id"] = player_id
    if vacancy_id:
        filter_query["vacancy_id"] = vacancy_id
    
    applications = await db.applications.find(filter_query).sort("applied_at", -1).limit(limit).to_list(limit)
    return [Application(**application) for application in applications]

@api_router.get("/applications/{application_id}", response_model=Application)
async def get_application(application_id: str):
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return Application(**application)

@api_router.put("/applications/{application_id}", response_model=Application)
async def update_application(application_id: str, application_update: ApplicationUpdate):
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in application_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Set reviewed_at if status changes from pending
    if update_data.get("status") and application.get("status") == "pending":
        update_data["reviewed_at"] = datetime.utcnow()
    
    await db.applications.update_one({"id": application_id}, {"$set": update_data})
    
    # Return updated application
    updated_application = await db.applications.find_one({"id": application_id})
    return Application(**updated_application)

@api_router.get("/players/{player_id}/applications", response_model=List[Application])
async def get_player_applications(player_id: str, status: Optional[str] = None):
    filter_query = {"player_id": player_id}
    if status:
        filter_query["status"] = status
    
    applications = await db.applications.find(filter_query).sort("applied_at", -1).to_list(1000)
    return [Application(**application) for application in applications]

@api_router.get("/clubs/{club_id}/applications", response_model=List[Application])
async def get_club_applications(
    club_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    vacancy_id: Optional[str] = None,
    limit: int = 100
):
    # Get all vacancies for this club
    filter_query = {"club_id": club_id}
    if vacancy_id:
        filter_query["id"] = vacancy_id
    
    vacancies = await db.vacancies.find(filter_query).to_list(1000)
    vacancy_ids = [vacancy["id"] for vacancy in vacancies]
    
    # Get all applications for these vacancies
    app_filter = {"vacancy_id": {"$in": vacancy_ids}}
    if status:
        app_filter["status"] = status
    if priority:
        app_filter["priority"] = priority
    
    applications = await db.applications.find(app_filter).sort("applied_at", -1).limit(limit).to_list(limit)
    return [Application(**application) for application in applications]

@api_router.post("/applications/{application_id}/shortlist")
async def shortlist_application(application_id: str):
    """Shortlist an application"""
    application = await db.applications.find_one({"id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    await db.applications.update_one(
        {"id": application_id},
        {"$set": {
            "status": "shortlisted",
            "priority": "high",
            "updated_at": datetime.utcnow(),
            "reviewed_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Application shortlisted successfully"}

@api_router.post("/applications/bulk-update")
async def bulk_update_applications(
    application_ids: List[str],
    update_data: ApplicationUpdate
):
    """Bulk update multiple applications"""
    if not application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.applications.update_many(
        {"id": {"$in": application_ids}},
        {"$set": update_dict}
    )
    
    return {"message": f"Updated {result.modified_count} applications successfully"}

# Public Profile endpoints
@api_router.get("/public/players/{player_id}", response_model=PlayerProfile)
async def get_public_player_profile(player_id: str):
    """Get public player profile - accessible to everyone"""
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Check if player profile is verified (only show verified public profiles)
    if not player.get("is_verified", False):
        raise HTTPException(status_code=404, detail="Player profile not available")
    
    # Remove MongoDB _id field and sensitive information completely
    player.pop("_id", None)
    sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
    for field in sensitive_fields:
        player.pop(field, None)
    
    return PlayerProfile(**player)

@api_router.get("/public/clubs/{club_id}", response_model=ClubProfile)
async def get_public_club_profile(club_id: str):
    """Get public club profile - accessible to everyone"""
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Check if club profile is verified (only show verified public profiles)
    if not club.get("is_verified", False):
        raise HTTPException(status_code=404, detail="Club profile not available")
    
    # Remove MongoDB _id field and sensitive information completely
    club.pop("_id", None)
    sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
    for field in sensitive_fields:
        club.pop(field, None)
    
    return ClubProfile(**club)

@api_router.get("/public/clubs/{club_id}/vacancies")
async def get_public_club_vacancies(club_id: str):
    """Get public vacancies for a club - accessible to everyone"""
    # Verify club exists and is verified
    club = await db.clubs.find_one({"id": club_id})
    if not club or not club.get("is_verified", False):
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Get active vacancies for this club
    vacancies = await db.vacancies.find({
        "club_id": club_id,
        "status": "active"
    }).sort("created_at", -1).to_list(100)
    
    # Remove MongoDB _id field from each vacancy
    for vacancy in vacancies:
        vacancy.pop("_id", None)
    
    return vacancies

@api_router.get("/public/players/browse")
async def browse_public_players(
    position: Optional[str] = None,
    experience_level: Optional[str] = None,
    location: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Browse public player profiles with filters"""
    filter_query = {"is_verified": True}
    
    if position:
        filter_query["position"] = position
    if experience_level:
        filter_query["experience_level"] = experience_level
    if location:
        filter_query["location"] = {"$regex": location, "$options": "i"}
    if country:
        filter_query["country"] = {"$regex": country, "$options": "i"}
    
    players = await db.players.find(filter_query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    # Remove sensitive information from each player
    public_players = []
    for player in players:
        player.pop("_id", None)
        sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
        for field in sensitive_fields:
            player.pop(field, None)
        public_players.append(PlayerProfile(**player))
    
    return public_players

@api_router.get("/public/clubs/browse")
async def browse_public_clubs(
    location: Optional[str] = None,
    club_type: Optional[str] = None,
    league: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Browse public club profiles with filters"""
    filter_query = {"is_verified": True}
    
    if location:
        filter_query["location"] = {"$regex": location, "$options": "i"}
    if club_type:
        filter_query["club_type"] = club_type
    if league:
        filter_query["league"] = {"$regex": league, "$options": "i"}
    
    clubs = await db.clubs.find(filter_query).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    # Remove sensitive information from each club
    public_clubs = []
    for club in clubs:
        club.pop("_id", None)
        sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
        for field in sensitive_fields:
            club.pop(field, None)
        public_clubs.append(ClubProfile(**club))
    
    return public_clubs

@api_router.get("/public/stats")
async def get_public_stats():
    """Get public platform statistics"""
    try:
        total_players = await db.players.count_documents({"is_verified": True})
        total_clubs = await db.clubs.count_documents({"is_verified": True})
        total_vacancies = await db.vacancies.count_documents({"status": "active"})
        total_applications = await db.applications.count_documents({})
        
        return {
            "total_players": total_players,
            "total_clubs": total_clubs,
            "active_vacancies": total_vacancies,
            "total_applications": total_applications
        }
    except Exception as e:
        return {
            "total_players": 0,
            "total_clubs": 0,
            "active_vacancies": 0,
            "total_applications": 0
        }

# Profile viewing endpoints
@api_router.get("/players/{player_id}/profile", response_model=PlayerProfile)
async def get_player_profile(player_id: str):
    """Get detailed player profile - accessible by clubs for reviewing applications"""
    player = await db.players.find_one({"id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Remove MongoDB _id field and sensitive information completely
    player.pop("_id", None)
    sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
    for field in sensitive_fields:
        player.pop(field, None)
    
    return PlayerProfile(**player)

@api_router.get("/clubs/{club_id}/profile", response_model=ClubProfile)
async def get_club_profile(club_id: str):
    """Get detailed club profile - accessible by players for viewing club information"""
    club = await db.clubs.find_one({"id": club_id})
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    
    # Remove MongoDB _id field and sensitive information completely
    club.pop("_id", None)
    sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
    for field in sensitive_fields:
        club.pop(field, None)
    
    return ClubProfile(**club)
    
    return Club(**club)

@api_router.get("/clubs/{club_id}/applications-with-profiles")
async def get_club_applications_with_profiles(
    club_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    vacancy_id: Optional[str] = None,
    limit: int = 100
):
    """Get applications for a club with detailed player profile information"""
    # Get all vacancies for this club
    filter_query = {"club_id": club_id}
    if vacancy_id:
        filter_query["id"] = vacancy_id
    
    vacancies = await db.vacancies.find(filter_query).to_list(1000)
    vacancy_ids = [vacancy["id"] for vacancy in vacancies]
    
    if not vacancy_ids:
        return []
    
    # Get all applications for these vacancies
    app_filter = {"vacancy_id": {"$in": vacancy_ids}}
    if status:
        app_filter["status"] = status
    if priority:
        app_filter["priority"] = priority
    
    applications = await db.applications.find(app_filter).sort("applied_at", -1).limit(limit).to_list(limit)
    
    # Enrich applications with player profile data
    enriched_applications = []
    for app in applications:
        # Remove MongoDB _id field from application
        app.pop("_id", None)
        
        # Get player profile
        player = await db.players.find_one({"id": app["player_id"]})
        if player:
            # Remove MongoDB _id field and sensitive data completely
            player.pop("_id", None)
            sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
            for field in sensitive_fields:
                player.pop(field, None)
            
            # Add player profile to application
            app["player_profile"] = player
        
        # Get vacancy details
        vacancy = await db.vacancies.find_one({"id": app["vacancy_id"]})
        if vacancy:
            vacancy.pop("_id", None)
            app["vacancy_details"] = vacancy
            
        enriched_applications.append(app)
    
    return enriched_applications

@api_router.get("/players/{player_id}/applications-with-clubs")
async def get_player_applications_with_clubs(
    player_id: str,
    status: Optional[str] = None
):
    """Get applications for a player with detailed club profile information"""
    filter_query = {"player_id": player_id}
    if status:
        filter_query["status"] = status
    
    applications = await db.applications.find(filter_query).sort("applied_at", -1).to_list(1000)
    
    # Enrich applications with club profile data
    enriched_applications = []
    for app in applications:
        # Remove MongoDB _id field from application
        app.pop("_id", None)
        
        # Get vacancy details
        vacancy = await db.vacancies.find_one({"id": app["vacancy_id"]})
        if vacancy:
            vacancy.pop("_id", None)
            app["vacancy_details"] = vacancy
            
            # Get club profile
            club = await db.clubs.find_one({"id": vacancy["club_id"]})
            if club:
                # Remove MongoDB _id field and sensitive data completely
                club.pop("_id", None)
                sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
                for field in sensitive_fields:
                    club.pop(field, None)
                
                # Add club profile to application
                app["club_profile"] = club
            
        enriched_applications.append(app)
    
    return enriched_applications

@api_router.get("/vacancies/{vacancy_id}/with-club-profile")
async def get_vacancy_with_club_profile(vacancy_id: str):
    """Get vacancy details with full club profile information"""
    vacancy = await db.vacancies.find_one({"id": vacancy_id})
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Remove MongoDB _id field
    vacancy.pop("_id", None)
    
    # Get club profile
    club = await db.clubs.find_one({"id": vacancy["club_id"]})
    if club:
        # Remove MongoDB _id field and sensitive data completely
        club.pop("_id", None)
        sensitive_fields = ["password_hash", "verification_token", "verification_token_expires", "password_reset_token", "password_reset_expires"]
        for field in sensitive_fields:
            club.pop(field, None)
        
        vacancy["club_profile"] = club
    
    # Increment view count
    await db.vacancies.update_one(
        {"id": vacancy_id}, 
        {"$inc": {"views_count": 1}}
    )
    
    return vacancy

# Email verification endpoints
@api_router.post("/verify-email")
async def verify_email(verification: EmailVerificationRequest):
    """Verify email address using token"""
    user_type = verification.user_type.lower()
    
    if user_type not in ["player", "club"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    # Determine collection
    collection = db.players if user_type == "player" else db.clubs
    
    # Find user by verification token
    user = await collection.find_one({
        "verification_token": verification.token,
        "verification_token_expires": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    # Update user as verified and remove token
    await collection.update_one(
        {"id": user["id"]},
        {
            "$set": {"is_verified": True, "updated_at": datetime.utcnow()},
            "$unset": {"verification_token": "", "verification_token_expires": ""}
        }
    )
    
    # Send welcome email
    send_welcome_email(user["email"], user_type, user["name"])
    
    return {"message": "Email verified successfully! Welcome to Field Hockey Connect."}

@api_router.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest):
    """Resend verification email"""
    user_type = request.user_type.lower()
    
    if user_type not in ["player", "club"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    # Determine collection
    collection = db.players if user_type == "player" else db.clubs
    
    # Find user by email
    user = await collection.find_one({"email": request.email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("is_verified", False):
        raise HTTPException(status_code=400, detail="Email is already verified")
    
    # Generate new verification token
    verification_token = str(uuid.uuid4())
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user with new token
    await collection.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "verification_token": verification_token,
                "verification_token_expires": verification_expires,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send verification email
    email_sent = send_verification_email(request.email, verification_token, user_type, user["name"])
    
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send verification email")
    
    return {"message": "Verification email sent successfully"}

@api_router.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset email"""
    user_type = request.user_type.lower()
    
    if user_type not in ["player", "club"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    # Determine collection
    collection = db.players if user_type == "player" else db.clubs
    
    # Find user by email
    user = await collection.find_one({"email": request.email})
    
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If an account with this email exists, a password reset email has been sent"}
    
    # Generate password reset token
    reset_token = str(uuid.uuid4())
    reset_expires = datetime.utcnow() + timedelta(hours=2)  # 2 hour expiry
    
    # Update user with reset token
    await collection.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires": reset_expires,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Send password reset email
    send_password_reset_email(request.email, reset_token, user_type, user["name"])
    
    return {"message": "If an account with this email exists, a password reset email has been sent"}

@api_router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password using token"""
    user_type = request.user_type.lower()
    
    if user_type not in ["player", "club"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    # Determine collection
    collection = db.players if user_type == "player" else db.clubs
    
    # Find user by reset token
    user = await collection.find_one({
        "password_reset_token": request.token,
        "password_reset_expires": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Hash new password
    new_password_hash = get_password_hash(request.new_password)
    
    # Update user with new password and remove reset token
    await collection.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow()
            },
            "$unset": {
                "password_reset_token": "",
                "password_reset_expires": ""
            }
        }
    )
    
    return {"message": "Password reset successfully"}

@api_router.get("/check-verification-status")
async def check_verification_status(email: str, user_type: str):
    """Check if user email is verified"""
    user_type = user_type.lower()
    
    if user_type not in ["player", "club"]:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    # Determine collection
    collection = db.players if user_type == "player" else db.clubs
    
    # Find user by email
    user = await collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "is_verified": user.get("is_verified", False),
        "email": user["email"],
        "name": user["name"]
    }

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