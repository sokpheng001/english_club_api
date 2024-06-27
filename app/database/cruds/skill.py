
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import Base
import uuid
from fastapi import HTTPException, status
from sqlalchemy import exc
from app.models.skill import Skill
from app.models.exercise import Exercise
from app.models.question import Question
from app.models.choice import Choice
from datetime import date
from app.database.schemas import skill, payload,exercise,question, choice
from app.database.schemas.english_level import MyLevel


async def create_new_skill(sk:skill.CreateSkillDto, session=AsyncSession):
    sk_uuid =str(uuid.uuid4())

    if sk.skill_level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Skill level should be one of A1 to C2, but you given {sk.skill_level}")
        
    new_skill = Skill(sk_uuid, sk.skill_name, sk.thumbnail, sk.description, sk.skill_level,False)
    try:
        session.add(new_skill) # add to database
        await session.commit()
        await session.refresh(new_skill)
    except (AttributeError, KeyError) as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skill.ResponseSkillDto(
            skill_uuid=new_skill.skill_uuid,
            skill_name=new_skill.skill_name,
            thumbnail=new_skill.thumbnail,
            description=new_skill.description,
            skill_level=new_skill.skill_level,
            is_deleted=new_skill.is_deleted,
            exercises=[]
        ),
        message=f"Created new skill successfully",
    )

async def list_all_skills(session:AsyncSession):
    query = select(Skill).where(Skill.is_deleted == False)
    re = await session.execute(query)
    skills = re.scalars().all()
    skls:skill.ResponseSkillDto = []
    # get all exercises for each skill
    exercise_response:exercise.RepsonseExerciseDto =[]
    for skl in skills:
        que = select(Exercise).where(Exercise.skill_id == skl.id)
        res = await session.execute(que)
        exercises = res.scalars().all()

        # get all questions for each exercise
        all_questions:question.ResponseQuestionDto = []

        for ex in exercises:
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
                    choices= response_for_choices
                ))
            exercise_response.append(exercise.RepsonseExerciseDto(
                ex_uuid= ex.ex_uuid,
                title=ex.title,
                thumbnail=ex.thumbnail,
                description=ex.description,
                skill_uuid=None,
                questions=all_questions
            ))


    for sk in skills:
        skls.append(skill.ResponseSkillDto(
            skill_uuid=sk.skill_uuid,
            skill_name=sk.skill_name,
            thumbnail=sk.thumbnail,
            description=sk.description,
            skill_level=sk.skill_level,
            is_deleted=sk.is_deleted,
            exercises=exercise_response
        ))
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=skls,
        message=f"List all skills",
    )