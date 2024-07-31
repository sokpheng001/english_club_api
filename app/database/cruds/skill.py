
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import Base
import uuid
from fastapi import HTTPException, status

from app.models.skill import Skill
from app.models.exercise import Exercise
from app.models.question import Question
from app.models.choice import Choice
from datetime import date
from app.database.schemas import skill, payload,exercise,question, choice
from app.database.schemas.english_level import MyLevel
from app.database.schemas.skii_name import Skill as sname
from app.utils.verify import is_valid_uuid


async def create_new_skill(sk:skill.CreateSkillDto, session=AsyncSession):

    # verify that skill exists
    sss = select(Skill).filter(Skill.skill_name.ilike(sk.skill_name)).filter(Skill.skill_level.ilike(sk.skill_level))
    re = await session.execute(sss)
    result_skill:Skill = re.scalars().first()
    
    if result_skill:
        for exuuid in sk.exercises_uuid:
            ex = select(Exercise).filter(Exercise.ex_uuid==exuuid)
            req = await session.execute(ex)
            req_:Exercise = req.scalars().first()
    
            if req_.skill_id==None:
                req_.skill_id = result_skill.id
                session.add(req_)
                await session.commit()
                await session.refresh(req_)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The exercise with uuid {exuuid} has already been assigned to another skill")

        await session.commit()
        await session.refresh(result_skill)
        return result_skill
            
        #raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill with name {sk.skill_name} and level {sk.skill_level} already exists")

    sk_uuid =str(uuid.uuid4())
    if sk.skill_level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill level should be one of A1 to C2, but you given {sk.skill_level}")
    if sk.skill_name.upper() not in sname.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill name should be one of READING, WRITING or LISTENING, but you given {sk.skill_name}")
        
    all_exercises_related_skil:exercise.RepsonseExerciseDto = []   
    for ex_uuid_ in sk.exercises_uuid:
        if is_valid_uuid(ex_uuid_):
            ex = select(Exercise).filter(Exercise.ex_uuid == ex_uuid_) 
            que = await session.execute(ex)
            result:Exercise = que.scalars().first()

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise not found")

            if sk.skill_level.upper() !=result.exercise_level.upper():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Quesion level should be the same as skill level, please check your exercise uuid given 🙈")

            if result.skill_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The exercise with id {ex_uuid_} been assigned to another skill.")
            if result:
                all_exercises_related_skil.append(exercise.RepsonseExerciseWithoutQuestionDto(
                    ex_uuid=result.ex_uuid,
                    title=result.title,
                    thumbnail=result.thumbnail,  
                    description=result.description,
                    tip= result.tip,
                    exercise_level=result.exercise_level
                ))
            if not result: 
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise not found")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid exercise uuid")
    

    new_skill = Skill(sk_uuid, sk.skill_name, sk.thumbnail, sk.description, sk.skill_level.upper(),False)
    try:
        session.add(new_skill) # add to database
        await session.commit()
        await session.refresh(new_skill)
        # set skill to exercise
        for ex_uuid in sk.exercises_uuid:
            ex = select(Exercise).filter(Exercise.ex_uuid == ex_uuid) 
            que = await session.execute(ex)
            result:Exercise = que.scalars().first()
            result.skill_id = new_skill.id
            await session.commit()
            await session.refresh(result)

    except (AttributeError, KeyError) as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skill.RepsonseSkillWithoutExerciseDto(
            skill_uuid=new_skill.skill_uuid,
            skill_name=new_skill.skill_name,
            thumbnail=new_skill.thumbnail,
            description=new_skill.description,
            skill_level=new_skill.skill_level,
        ),
        message=f"Created new skill successfully",
    )


async def delete_skill_by_uuid(skill_uuid:str, session=AsyncSession):
    if not is_valid_uuid(skill_uuid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill uuid is not valid")
    query = select(Skill).filter(Skill.skill_uuid == skill_uuid)
    result = await session.execute(query)
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill is not found")
    else:
        await session.delete(s)
        await session.commit()
        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_204_NO_CONTENT),
            payload=[],
            message=f"Skill deleted successfully"
        )

async def get_all_skills_by_skill_name(name:str, session=AsyncSession):
    if name.upper() not in sname.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill name should be one of READING, WRITING or LISTENING, but you given {name}")
    query = select(Skill).filter(Skill.skill_name.ilike(f"{name}")).order_by(Skill.skill_level)
    result = await session.execute(query)
    skills = result.scalars().all()
    if not skills:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill not found 😶‍🌫️")
    
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=[skill.RepsonseSkillWithoutExerciseDto(
            skill_uuid=sk.skill_uuid,
            skill_name=sk.skill_name,
            thumbnail=sk.thumbnail,
            description=sk.description,
            skill_level=sk.skill_level
        )for sk in skills] ,
        message=f"Skills found",
    )

async def get_skill_by_name_and_level(name, level, session=AsyncSession):
    if name.upper() not in sname.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill name should be one of READING, WRITING or LISTENING, but you given {name}")
    if level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill level should be one of A1 to C2, but you given {level}")
    query = select(Skill).filter(Skill.skill_name.ilike(f"%{name}%")).filter(Skill.skill_level.ilike(f"%{level}%"))
    result = await session.execute(query)
    skills = result.scalars().all()
    skls:skill.ResponseSkillDto = []

    if not skills:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skills not found")
    

    # get all exercises for each skill
    exercise_response:exercise.RepsonseExerciseWithoutQuestionDto =[]
    for skl in skills:
        que = select(Exercise).filter(Exercise.skill_id == skl.id)
        res = await session.execute(que)
        exercises = res.scalars().all()

        # get all questions for each exercise
        all_questions:question.ResponseQuestionDto = []
        for ex in exercises:
            if skl.id == ex.skill_id:

                exercise_response.append(exercise.RepsonseExerciseWithoutQuestionDto(
                    ex_uuid= ex.ex_uuid,
                    title=ex.title,
                    thumbnail=ex.thumbnail,
                    description=ex.description,
                    skill_uuid=None,
                    exercise_level= ex.exercise_level,
                    tip=ex.tip
                ))

        skls.append(skill.ResponseSkillWithoutQuestionDto(
            skill_uuid=skl.skill_uuid,
            skill_name=skl.skill_name,
            thumbnail=skl.thumbnail,
            description=skl.description,
            skill_level=skl.skill_level,
            is_deleted=skl.is_deleted,
            exercises=exercise_response
        ))
        exercise_response=[] # clear all the exercises

    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skls,
        message=f"List all skills",
    )


async def list_all_skills(session:AsyncSession):
    query = select(Skill).order_by(Skill.skill_level)
    re = await session.execute(query)
    skills = re.scalars().all()
    skls:skill.ResponseSkillDto = []
    # get all exercises for each skill
    exercise_response:exercise.RepsonseExerciseDto =[]
    for skl in skills:
        que = select(Exercise).filter(Exercise.skill_id == skl.id)
        res = await session.execute(que)
        exercises = res.scalars().all()

        # get all questions for each exercise
        all_questions:question.ResponseQuestionDto = []
        for ex in exercises:
            if skl.id == ex.skill_id:
                que = select(Question).where(Question.exercise_id==ex.id)
                req = await session.execute(que)
                q = req.scalars().all()
                for qu in q:
                    # get all  choices for the each question
                    ch = select(Choice).where(Choice.question_id == qu.id)
                    req = await session.execute(ch)
                    all_choices_for_each_question = req.scalars().all()
                    response_for_choices:choice.ResponseChoiceDto = []
                    for cho in all_choices_for_each_question:
                        response_for_choices.append(choice.ResponseChoiceDto(
                            choice_uuid=cho.choice_uuid,
                            text=cho.choice_text,
                            is_correct=cho.is_correct
                        ))
                    all_questions.append(question.ResponseQuestionDto(
                        q_uuid= qu.q_uuid,
                        question_text = qu.text,
                        voice= qu.voice,
                        video= qu.video,
                        type= qu.type,
                        correct_answer = qu.correct_answer,
                        choices= response_for_choices,
                        question_level= qu.question_level
                    ))
                exercise_response.append(exercise.RepsonseExerciseDto(
                    ex_uuid= ex.ex_uuid,
                    title=ex.title,
                    thumbnail=ex.thumbnail,
                    description=ex.description,
                    skill_uuid=None,
                    questions=all_questions,
                    exercise_level= ex.exercise_level,
                    tip=ex.tip
                ))
                all_questions = [] # clear all questions


        skls.append(skill.ResponseSkillDto(
            skill_uuid=skl.skill_uuid,
            skill_name=skl.skill_name,
            thumbnail=skl.thumbnail,
            description=skl.description,
            skill_level=skl.skill_level,
            is_deleted=skl.is_deleted,
            exercises=exercise_response
        ))
        exercise_response=[] # clear all the exercises

    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skls,
        message=f"List all skills",
    )