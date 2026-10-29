from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, Token, UserResponse, UserCreate
from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_role
)
from app.services.audit_service import record_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Standard authentication endpoint verifying credentials against securely hashed database records.
    Supports either registered email address or username.
    """
    identifier = request.username.strip()
    user = db.query(User).filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

    if not user or not verify_password(request.password, user.hashed_password):
        # Audit failed login attempt (Do NOT log password!)
        record_audit_event(
            db=db,
            actor_id=identifier[:50],
            actor_role="ANONYMOUS",
            action="USER_LOGIN_FAILED",
            entity_type="USER_SESSION",
            entity_id=identifier[:50],
            details=f"Failed login attempt for identifier '{identifier}' (invalid credentials)"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        record_audit_event(
            db=db,
            actor_id=user.username,
            actor_role=user.role.value,
            action="USER_LOGIN_REJECTED",
            entity_type="USER_SESSION",
            entity_id=user.username,
            details=f"Login rejected: Account for user '{user.username}' is disabled"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    token = create_access_token({
        "sub": user.username,
        "role": user.role.value,
        "institution_id": user.institution_id
    })

    # Audit successful login
    record_audit_event(
        db=db,
        actor_id=user.username,
        actor_role=user.role.value,
        action="USER_LOGIN_SUCCESS",
        entity_type="USER_SESSION",
        entity_id=user.username,
        details=f"User '{user.username}' ({user.role.value}) authenticated successfully"
    )

    return Token(
        access_token=token,
        role=user.role,
        username=user.username,
        institution_id=user.institution_id,
        full_name=user.full_name
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Terminates the authenticated session and records a formal audit log event.
    """
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="USER_LOGOUT",
        entity_type="USER_SESSION",
        entity_id=current_user.username,
        details=f"User '{current_user.username}' logged out"
    )
    return {"status": "SUCCESS", "message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns verified profile of currently authenticated user derived from valid JWT bearer token.
    """
    return current_user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_account(
    req: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Administrative endpoint for provisioning accounts.
    Strictly restricted to ADMIN role. Non-admin users cannot provision accounts.
    """
    existing_username = db.query(User).filter(User.username == req.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = db.query(User).filter(User.email == req.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=req.username.strip(),
        email=req.email.strip().lower(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip(),
        role=req.role,
        institution_id=req.institution_id.strip() if req.institution_id else None,
        is_active=True
    )
    db.add(new_user)
    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="USER_ACCOUNT_CREATED",
        entity_type="USER",
        entity_id=new_user.username,
        details=f"Admin '{current_user.username}' provisioned user '{new_user.username}' with role '{new_user.role.value}'"
    )

    db.refresh(new_user)
    return new_user
