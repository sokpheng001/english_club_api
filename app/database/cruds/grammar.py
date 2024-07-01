
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.database.schemas.grammar import CreateGrammarDto, ResponseGrammarDto
from app.database.schemas.lesson import ResponseLessonDto
from app.database.cruds.lesson import get_lesson_by_uuid, get_lesson_by_grammar_id

from datetime import date
from app.models.grammar import Grammar
from app.models.lesson import Lesson
from app.database.schemas.english_level import MyLevel
import uuid
from app.database.schemas import payload, vocabulary
from app.utils.verify import is_valid_uuid


async def list_all_grammars(session:AsyncSession):
    query = select(Grammar)
    result = await session.execute(query)
    response_grammars = result.scalars().all()
    return [ResponseGrammarDto(
        grammar_uuid=g.grammar_uuid,
        title=g.grammar_name,
        description=g.description,
        thumbnail=g.thumbnail,
        grammar_level=g.grammar_level,
        lessons= await get_lesson_by_grammar_id(g.id, session)
    )for g in response_grammars]


async def get_grammar_by_level(level:str, session:AsyncSession):
    if level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {level}")
    query = select(Grammar).where(Grammar.grammar_level.ilike(level))
    result = await session.execute(query)
    g = result.scalars().first() 
    if not g:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grammar not found")
    return ResponseGrammarDto(
        grammar_uuid=g.grammar_uuid,
        title=g.grammar_name,
        description=g.description,
        thumbnail=g.thumbnail,
        grammar_level=g.grammar_level,
        lessons= await get_lesson_by_grammar_id(g.id, session)
    )
async def create_grammar(gram: CreateGrammarDto, session: AsyncSession):
    # check if valid uuid of lessons
    response_lessons:ResponseLessonDto = []
    # i=0  for checking lessons uuid
    for less_uuid in gram.lesson_uuids:
        if not is_valid_uuid(less_uuid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Lesson uuid is not valid 😏")
        #  check if exited lessons
        query = select(Lesson).where(Lesson.lesson_uuid == less_uuid)
        result = await session.execute(query)
        ls = result.scalars().first()
        if not ls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson {less_uuid} is not found 😏")
        if ls.grammar_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson {less_uuid} is already assigned to another grammar 😉")
        elif ls.vocabulary_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson {less_uuid} is already assigned to another vocabulary 😉")

        if len(gram.lesson_uuids)>1:
            if i < len(gram.lesson_uuids):
                if less_uuid == gram.lesson_uuids[i+1]:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson {less_uuid} is duplicated 😏")
                i+=1

        response_lessons.append(
            await get_lesson_by_uuid(less_uuid, session)
        )

    # validate lesson uuid is not the same

    g_uuid = uuid.uuid4()
    new_grammar = Grammar(grammar_uuid=str(g_uuid), 
                          grammar_name=gram.title, 
                          description=gram.description,
                          thumbnail=gram.thumbnail,
                          grammar_level=response_lessons[0].lesson_level)
    session.add(new_grammar)
    await session.commit()
    await session.refresh(new_grammar)
    # set lesson to grammar         # update lesson id in question
    for less_uuid in gram.lesson_uuids:
        query = select(Lesson).where(Lesson.lesson_uuid == less_uuid)
        result = await session.execute(query)
        ls = result.scalars().first()
        ls.grammar_id = new_grammar.id
        await session.commit()
        await session.refresh(ls)


    return ResponseGrammarDto(
        grammar_uuid=new_grammar.grammar_uuid,
        title=new_grammar.grammar_name,
        description=new_grammar.description,
        thumbnail=new_grammar.thumbnail,
        grammar_level=new_grammar.grammar_level,
        lessons=response_lessons
    )