
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.schemas.lesson import CreateLessonDto
from fastapi import HTTPException, status
from app.models.lesson import Lesson
from app.models.section import Section
from app.database.schemas.section import ResponseSectionDto
from app.database.schemas.exercise import RepsonseExerciseDto
from app.models.exercise import Exercise
from app.database.cruds.exercise import find_exercise_by_uuid
from datetime import date
from app.database.schemas.english_level import MyLevel
import uuid
from app.database.schemas import payload, lesson
from app.utils.verify import is_valid_uuid





async def get_lesson_by_vocabulary_id(vocab_id:int, session:AsyncSession):
    query = select(Lesson).filter(Lesson.vocabulary_id == vocab_id)
    result = await session.execute(query)
    less:Lesson = result.scalars().all()
    if not less:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson not found 😶‍🌫️")
    
    all_lessons:lesson.ResponseLessonDto = []
    for les in less:
        list_of_sections:ResponseSectionDto = []
        qs = select(Section).filter(Section.lesson_id==les.id)
        result = await session.execute(qs)
        sections = result.scalars().all()
        for sec in sections:
            list_of_sections.append(ResponseSectionDto(
                section_uuid=sec.section_uuid,
                title=sec.section_name,
                description=sec.description,
                thumbnail_url=sec.thumbnail,
                section_level=sec.section_level,
                examples=sec.examples
            ))
        all_lessons.append(
            lesson.ResponseLessonDto(
                lesson_uuid=les.lesson_uuid,
                lesson_title=les.name,
                description=les.description,
                thumbnail=les.thumbnail,
                sections=list_of_sections,
                lesson_level=les.lesson_level
        ) )
    return all_lessons
async def get_lesson_by_grammar_id(grammar_id:int, session:AsyncSession):
    query = select(Lesson).filter(Lesson.grammar_id==grammar_id)
    result = await session.execute(query)
    less:Lesson = result.scalars().all()
    if not less:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson not found 😶‍🌫️")
    
    all_lessons:lesson.ResponseLessonDto = []
    for les in less:
        list_of_sections:ResponseSectionDto = []
        qs = select(Section).filter(Section.lesson_id==les.id)
        result = await session.execute(qs)
        sections = result.scalars().all()
        for sec in sections:
            list_of_sections.append(ResponseSectionDto(
                section_uuid=sec.section_uuid,
                title=sec.section_name,
                description=sec.description,
                thumbnail_url=sec.thumbnail,
                section_level=sec.section_level,
                examples=sec.examples
            ))
        all_lessons.append(
            lesson.ResponseLessonDto(
                lesson_uuid=les.lesson_uuid,
                lesson_title=les.name,
                description=les.description,
                thumbnail=les.thumbnail,
                sections=list_of_sections,
                lesson_level=les.lesson_level
        ) )
    return all_lessons
async def create_new_lessons(is_included_exercies:bool,less:CreateLessonDto, session: AsyncSession):

    # verify that lesson not existing
    sss = select(Lesson).filter(Lesson.name.ilike(less.name))
    re = await session.execute(sss)
    result_lesson:Lesson = re.scalars().first()
    if result_lesson:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Lesson ' {result_lesson.name} ' already exists 🙈")
        
    list_of_sections:ResponseSectionDto = []
    list_of_exercises:RepsonseExerciseDto = []
    for sec_uuid in less.sections_uuids:
        if not is_valid_uuid(sec_uuid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid section uuid 😒")
        s = select(Section).filter(Section.section_uuid == sec_uuid)
        re = await session.execute(s)
        sec = re.scalars().first()
        if not sec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Section {sec_uuid} is not found 🙈")
        
        if sec.lesson_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Section {sec_uuid} is already belonging to another lesson 😉")
        
        list_of_sections.append(ResponseSectionDto(
            section_uuid=sec.section_uuid,
            title=sec.section_name,
            description=sec.description,
            thumbnail_url=sec.thumbnail,
            section_level=sec.section_level,
            examples=sec.examples
        ))
        # check section level - must be the same
    i = 1
    if len(list_of_sections)>1:
        for s in list_of_sections:
            if s.section_level!=list_of_sections[0].section_level:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"All sections must have the same level 😎")
            if i!= len(list_of_sections):
                if s.section_uuid==list_of_sections[i].section_uuid:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"All sections must not have the same uuid 😏")
                i+=i
    
    if is_included_exercies is True:
        for ex_uuid in less.exercises_uuids:
            if not is_valid_uuid(ex_uuid):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid exercise uuid 😒")
            s = select(Exercise).filter(Exercise.ex_uuid == ex_uuid)
            re = await session.execute(s)
            ex = re.scalars().first()
            if not ex:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise {ex_uuid} is not found 🙈")
            
            if ex.lesson_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Exercise {ex_uuid} is already belonging to another lesson 😉")
            
            list_of_exercises.append(await find_exercise_by_uuid(ex_uuid, session))

  
    les_uuid = uuid.uuid4()
    new_lesson = Lesson(lesson_uuid = str(les_uuid),
                        name=less.name, 
                        description=less.description,
                        thumbnail=less.thumbnail,
                        lesson_level=list_of_sections[0].section_level,
                        is_deleted=False)
    session.add(new_lesson)
    await session.commit()
    await session.refresh(new_lesson)
    # update lesson id in section table
    for sec_uuid in less.sections_uuids:
        s = select(Section).filter(Section.section_uuid == sec_uuid)
        re = await session.execute(s)
        sec = re.scalars().first()
        # 
        sec.lesson_id = new_lesson.id
        await session.commit()
        await session.refresh(sec)
    
    if is_included_exercies is True:
        # upate lession in exercise table
        for ex_uuid in less.exercises_uuids:
            ex = select(Exercise).filter(Exercise.ex_uuid==ex_uuid)
            re = await session.execute(ex)
            ex = re.scalars().first()
            ex.lesson_id = new_lesson.id
            await session.commit()
            await session.refresh(ex)
    # 
    return lesson.ResponseLessonDto(
            lesson_uuid=new_lesson.lesson_uuid,
            lesson_title=new_lesson.name,
            description=new_lesson.description,
            thumbnail=new_lesson.thumbnail,
            sections=list_of_sections,
            exercises=list_of_exercises,
            lesson_level=new_lesson.lesson_level
        )

async def get_lesson_by_level(level:str, session:AsyncSession):
    if level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {level}")
    
    query = select(Lesson).filter(Lesson.lesson_level.ilike(level))
    result = await session.execute(query)
    less:Lesson = result.scalars().first()
    if not less:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson not found 😶‍🌫️")
    
    qs = select(Section).filter(Section.lesson_id==less.id)
    result = await session.execute(qs)
    sections = result.scalars().all()
    list_of_sections:ResponseSectionDto = []
    for sec in sections:
        list_of_sections.append(ResponseSectionDto(
            section_uuid=sec.section_uuid,
            title=sec.section_name,
            description=sec.description,
            thumbnail_url=sec.thumbnail,
            section_level=sec.section_level,
            examples=sec.examples
        ))
    return lesson.ResponseLessonDto(
            lesson_uuid=less.lesson_uuid,
            lesson_title=less.name,
            description=less.description,
            thumbnail=less.thumbnail,
            sections=list_of_sections,
            lesson_level=less.lesson_level
        )

async def get_lesson_by_uuid(ls_uuid, session:AsyncSession)->lesson.ResponseLessonDto:
    query = select(Lesson).filter(Lesson.lesson_uuid==ls_uuid)
    result = await session.execute(query)
    less:Lesson = result.scalars().first()
    if not less:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson not found 😶‍🌫️")
    
    qs = select(Section).filter(Section.lesson_id==less.id)
    result = await session.execute(qs)
    sections = result.scalars().all()
    list_of_sections:ResponseSectionDto = []
    for sec in sections:
        list_of_sections.append(ResponseSectionDto(
            section_uuid=sec.section_uuid,
            title=sec.section_name,
            description=sec.description,
            thumbnail_url=sec.thumbnail,
            section_level=sec.section_level,
            examples=sec.examples
        ))
    return lesson.ResponseLessonDto(
            lesson_uuid=less.lesson_uuid,
            lesson_title=less.name,
            description=less.description,
            thumbnail=less.thumbnail,
            sections=list_of_sections,
            lesson_level=less.lesson_level
        )


async def delete_lesson_by_uuid(u_uuid:str, session:AsyncSession):
    if not is_valid_uuid(u_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid lesson uuid 😒")
    query = select(Lesson).where(Lesson.lesson_uuid == u_uuid)
    result = await session.execute(query)
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lesson {u_uuid} is not found 🙈")
    
    await session.delete(lesson)
    await session.commit()
    return u_uuid

async def lis_all_lessons(session: AsyncSession):
    try:
        query = select(Lesson).order_by(Lesson.lesson_level)
        result = await session.execute(query)
        lessons = result.scalars().all()
        response_lessons:lesson.ResponseLessonDto = []
        for less in lessons:
            query = select(Section).where(Section.lesson_id == less.id)
            result = await session.execute(query)
            sections = result.scalars().all()
            list_of_sections:ResponseSectionDto = []
            for sec in sections:
                list_of_sections.append(ResponseSectionDto(
                    section_uuid=sec.section_uuid,
                    title=sec.section_name,
                    description=sec.description,
                    thumbnail_url=sec.thumbnail,
                    section_level=sec.section_level,
                    examples=sec.examples
                ))
            
            exs = select(Exercise).filter(Exercise.lesson_id == less.id)
            result = await session.execute(exs)
            exercises = result.scalars().all()
            list_of_exercises:RepsonseExerciseDto = []
            for ex in exercises:
                list_of_exercises.append(
                    await find_exercise_by_uuid(ex.ex_uuid, session)
                )

            response_lessons.append(lesson.ResponseLessonDto(
                lesson_uuid =less.lesson_uuid,
                lesson_title=less.name,
                description=less.description,
                thumbnail=less.thumbnail,
                sections=list_of_sections,
                lesson_level=less.lesson_level,
                exercises=list_of_exercises
                )
            )
        return response_lessons

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))