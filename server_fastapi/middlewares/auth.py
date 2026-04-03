from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.database import get_db
from utils.auth import decode_token
from models.user import TokenData, UserRole
from bson import ObjectId

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    token_data = decode_token(token)
    if token_data is None:
        print("⚠️ Token decoding failed - Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Verify user exists in database
    try:
        user = await db.users.find_one({"_id": ObjectId(token_data.id)})
        if not user:
            print(f"⚠️ User not found with ID: {token_data.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.get("isActive", True):
            print(f"⚠️ User account deactivated: {user.get('email')}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        print(f"✅ Authenticated user: {user.get('email')} (Role: {token_data.role})")
        return token_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"❌ Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

async def require_admin(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to require admin role
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user
