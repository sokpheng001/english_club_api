
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.exercise import Exercise
from app.models.question import Question
from app.models.skill import Skill
import uuid
from fastapi import HTTPException, status
from datetime import date
from app.database.schemas import payload, question
from app.database.schemas.exercise import CreateExerciseDto, RepsonseExerciseDto


async def create_exercise(ex:CreateExerciseDto, session:AsyncSession):

    try:
        sq = select(Skill).where(Skill.skill_uuid== ex.skill_uuid)
        re = await session.execute(sq)
        sk:Skill = re.scalars().first()
        
        # fetch question for the exercise
        list_of_questions:question.ResponseQuestionDto = []
        for qid in ex.q_uuids:
            qq = select(Question).where(Question.q_uuid == qid)
            req = await session.execute(qq)
            q = req.scalars().first()
            list_of_questions.append(question.ResponseQuestionDto(
                q_uuid= q.q_uuid,
                text = q.text,
                voice= q.voice,
                video= q.video,
                type= q.type,
                correct_answer= q.correct_answer,
                choices=[]
            ))
    
        exercise_uuid =str(uuid.uuid4()) # generate unique identifier for the exercise
        new_exercise = Exercise(exercise_uuid, ex.title,ex.thumbnail ,ex.description,skill_id=sk.id)

        session.add(new_exercise) # add to database
        await session.commit()
        await session.refresh(new_exercise)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing any field")
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload= RepsonseExerciseDto(
            ex_uuid =new_exercise.ex_uuid,
            title=new_exercise.title,
            thumbnail=new_exercise.thumbnail,
            description=new_exercise.description,
            skill_uuid=sk.skill_uuid,
            questions=list_of_questions
        ),
        message="Exercise has been created successfully"
    )
