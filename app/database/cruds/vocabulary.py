from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.database.schemas.vocabulary import CreateVocabularyDto, ResponseVocabularyDto
from app.database.schemas.lesson import ResponseLessonDto
from app.models.lesson import Lesson
from app.models.vocabulary import Vocabulary
from app.database.cruds.lesson import get_lesson_by_vocabulary_id, get_lesson_by_uuid
from app.utils.verify import is_valid_uuid
from app.database.schemas.english_level import MyLevel
import uuid


async def find_vocabulary_by_level(v_level:str, session:AsyncSession):
    if v_level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {v_level}")
    query = select(Vocabulary).where(Vocabulary.vocabulary_level.ilike(v_level))
    result = await session.execute(query)
    vs:Vocabulary = result.scalars().all()
    if not vs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vocabulary not found")
    all_vocabularies:ResponseVocabularyDto= []
    # get all lessons in vocabularies
    for v in vs:
        all_vocabularies.append(ResponseVocabularyDto(
            vocabulary_uuid=v.vocabulary_uuid,
            titles=v.vocabulary_name,
            description=v.description,
            thumbnail_url=v.thumbnail,
            lessons= get_lesson_by_vocabulary_id(v.id)
        ))
    return all_vocabularies

async def get_all_vocabularies(session:AsyncSession):
    query = select(Vocabulary).order_by(Vocabulary.vocabulary_level)
    result = await session.execute(query)
    vs:Vocabulary = result.scalars().all()
    all_vocabularies:ResponseVocabularyDto= []
    # get all lessons in vocabularies
    for v in vs:
        
        all_vocabularies.append(ResponseVocabularyDto(
            vocabulary_uuid=v.vocab_uuid,
            titles=v.vocab_name,
            description=v.description,
            thumbnail_url=v.thumbnail,
            lessons= await get_lesson_by_vocabulary_id(v.id, session=session)
        ))
    return all_vocabularies
async def create_vocabulary(vo:CreateVocabularyDto, session:AssertionError):
        # check if valid uuid of lessons
    response_lessons:ResponseLessonDto = []
    # i=0  for checking lessons uuid
    for less_uuid in vo.lesson_uuids:
        if not is_valid_uuid(less_uuid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Lesson uuid is not valid 😏")
        #  check if exited lessons
        query = select(Lesson).where(Lesson.lesson_uuid == less_uuid)
        result = await session.execute(query)
        ls = result.scalars().first()
        if not ls:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson {less_uuid} is not found 😏")
        if ls.vocabulary_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson {less_uuid} is already assigned to another grammar 😉")
        elif ls.vocabulary_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson {less_uuid} is already assigned to another vocabulary 😉")

        # if len(vo.lesson_uuids)>1:
        #     if i < len(vo.lesson_uuids):
        #         if less_uuid == vo.lesson_uuids[i+1]:
        #             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson {less_uuid} is duplicated 😏")
        #         i+=1

        response_lessons.append(
            await get_lesson_by_uuid(less_uuid, session)
        )
    
        # validate lesson uuid is not the same

    v_uuid = uuid.uuid4()
    new_vocab = Vocabulary(vocab_uuid=str(v_uuid), vocabulary_name=vo.title, description=vo.description, thumbnail=vo.thumbnail_url)

    session.add(new_vocab)
    await session.commit()
    await session.refresh(new_vocab)
    # set lesson to grammar         # update lesson id in question
    for less_uuid in vo.lesson_uuids:
        query = select(Lesson).where(Lesson.lesson_uuid == less_uuid)
        result = await session.execute(query)
        ls:Lesson = result.scalars().first()
        ls.vocabulary_id = new_vocab.id
        await session.commit()
        await session.refresh(ls)

    return ResponseVocabularyDto(
        vocabulary_uuid=new_vocab.vocab_uuid,
        titles=new_vocab.vocab_name,
        description=new_vocab.description,
        thumbnail_url=new_vocab.thumbnail,
        lessons=response_lessons
    )
    
