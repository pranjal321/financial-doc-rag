from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import RoleAssign
from app.services.dependencies import get_current_user

router = APIRouter()

VALID_ROLES = ["admin", "analyst", "auditor", "client"]

PERMISSIONS = {
    "admin": ["upload", "edit", "delete", "view", "manage_roles"],
    "analyst": ["upload", "edit", "view"],
    "auditor": ["view", "review"],
    "client": ["view"],
}


@router.post("/create")
def create_role(role: str, user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from {VALID_ROLES}")
    return {"message": f"Role '{role}' is valid and available"}


@router.post("/assign-role")
def assign_role(data: RoleAssign, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    target = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target.role = data.role
    db.commit()
    return {"message": f"Role '{data.role}' assigned to user {data.user_id}"}


@router.get("/users/{user_id}/roles")
def get_user_roles(user_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "role": target.role}


@router.get("/users/{user_id}/permissions")
def get_user_permissions(user_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "role": target.role, "permissions": PERMISSIONS.get(target.role, [])}