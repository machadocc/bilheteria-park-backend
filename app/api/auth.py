from fastapi import APIRouter, HTTPException
from ..auth import authenticate_admin, create_access_token
from ..schemas import AuthLogin, TokenOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
def login(login_data: AuthLogin):
    if not authenticate_admin(login_data.username, login_data.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = create_access_token({"sub": login_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
