from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user():
    return models.User(
        id=1,
        username="manager",
        role=models.RoleEnum.manager
    )