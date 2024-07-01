from fastapi import APIRouter, HTTPException, Depends, status
from app.database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.cruds.grammar import create_grammar,list_all_grammars,get_grammar_by_level
from app.database.schemas.grammar import CreateGrammarDto
from app.database.schemas import payload
from datetime import date
grammar_router = APIRouter()

@grammar_router.post("/grammars/")
async def add_new_grammar(grammar:CreateGrammarDto, db:AsyncSession=Depends(get_db)):
    return await create_grammar(grammar, db)
@grammar_router.get("/grammars/")
async def get_all_grammars(db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload = await list_all_grammars(db),
        message="List all grammars 😎"
    )

@grammar_router.get("/grammars/{level}")
async def find_grammar_by_level(level:str, db:AsyncSession=Depends(get_db)):
    return payload.BaseResponse(
        date=date.today(),
        status=status.HTTP_200_OK,
        payload = await get_grammar_by_level(level, db),
        message="Grammar found 😎"
    )