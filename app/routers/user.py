from typing import Dict, Union

from fastapi import APIRouter, HTTPException

user_router = APIRouter()


@user_router.get("/users/")
def user_home():
    return {"message": "Hello User"}