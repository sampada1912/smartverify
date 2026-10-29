from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.services.auth_service import get_current_user, require_role
import subprocess
import sys
import os

router = APIRouter(prefix="/demo", tags=["Demo Management"])


@router.post("/reset-seed")
def reset_demo_database(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Resets the prototype database and reseeds all 8 demonstration scenarios and sample PDFs."""
    from seed_demo_data import seed_database
    try:
        seed_database()
        return {"status": "SUCCESS", "message": "Demo database successfully reset and reseeded with 8 test cases."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo data: {str(e)}")
