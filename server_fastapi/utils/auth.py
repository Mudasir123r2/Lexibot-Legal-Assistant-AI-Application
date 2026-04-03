import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config.settings import settings
from models.user import TokenData


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (supports both passlib and direct bcrypt formats)"""
    try:
        # Direct bcrypt verification
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Fallback: try passlib verification for legacy hashes
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        if not token:
            print("❌ decode_token received empty token")
            return None
            
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("id")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            print(f"❌ decode_token missing required claims. Payload: {payload}")
            return None
        
        return TokenData(id=user_id, role=role)
    except JWTError as e:
        print(f"❌ decode_token JWTError Exception: {str(e)}")
        print(f"   Received token length: {len(token) if token else 0}")
        return None
