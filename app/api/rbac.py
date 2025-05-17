from fastapi import Depends, HTTPException, status
from app.api.deps import get_current_user

def require_role(required_role: str):
    def role_checker(current_user = Depends(get_current_user)):
        if getattr(current_user, 'role', None) != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You need '{required_role}' role to access this resource."
            )
        return current_user
    return role_checker
