
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.exercise import Exercise
from app.models.question import Question
from app.models.choice import Choice
import json

from app.models.skill import Skill
import uuid
from fastapi import HTTPException, status
from datetime import date
from app.database.schemas import payload, question, choice
from app.database.schemas.exercise import CreateExerciseDto, RepsonseExerciseDto
from app.utils.verify import is_valid_uuid
from app.database.schemas.english_level import MyLevel
from app.database.schemas.english_level_template import Level
from app.utils.verify import is_valid_uuid

class LevelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Level):
            return obj.__dict__  # Convert Level object to a dictionary
        return super().default(obj)

async def create_exercise(ex:CreateExerciseDto, session:AsyncSession):
    
    # if ex.exercise_level.upper() not in MyLevel.__members__:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Exercise level should be one of A1 to C2, but you given {ex.exercise_level}")
    try:
        exercise_levels_follow_question_levels:Level = []
        # fetch question for the exercise
        if is_valid_uuid(ex.q_uuids[0]):
            list_of_questions:question.ResponseQuestionDto = []
            for qid in ex.q_uuids:
                qq = select(Question).where(Question.q_uuid == qid)
                req = await session.execute(qq)
                q = req.scalars().first()
                #check if the question is already assigned to the exercise
                if not q:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question {qid} does not exist 😶‍🌫️")
                if q.exercise_id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question {q.q_uuid} is already assigned to the exercise 😶‍🌫️")
                # get all  choices for the each question
                ch = select(Choice).where(Choice.question_id == q.id)
                req = await session.execute(ch)
                all_choices_for_each_question = req.scalars().all()
                response_for_choices:choice.ResponseChoiceDto = []
                for cho in all_choices_for_each_question:
                    response_for_choices.append(choice.ResponseChoiceDto(
                        choice_uuid=cho.choice_uuid,
                        text=cho.choice_text,
                        is_correct=cho.is_correct
                    ))
                exercise_levels_follow_question_levels.append(Level(level=q.question_level))
                list_of_questions.append(question.ResponseQuestionDto(
                    q_uuid= q.q_uuid,
                    question_text = q.text,
                    voice= q.voice,
                    video= q.video,
                    type= q.type,
                    question_level=q.question_level,
                    correct_answer= q.correct_answer,
                    choices=response_for_choices
                ))
        
            exercise_uuid =str(uuid.uuid4()) # generate unique identifier for the exercise

            new_exercise  = None
            level = [ans.dict() for ans in exercise_levels_follow_question_levels]
            new_exercise =  Exercise(exercise_uuid, ex.title,ex.thumbnail ,
                                         ex.description,
                                         exercise_level=level)
            session.add(new_exercise) # add to database
            await session.commit()
            await session.refresh(new_exercise)
            # update exercise id in question
            for qid in ex.q_uuids:
                qq = select(Question).filter(Question.q_uuid == qid)
                req = await session.execute(qq)
                q = req.scalars().first()
                if q:
                    if not q.exercise_id:
                        q.exercise_id = new_exercise.id
                        await session.commit()
                        await session.refresh(q)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question uuid for exercise 😏")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload= RepsonseExerciseDto(
            ex_uuid =new_exercise.ex_uuid,
            title=new_exercise.title,
            thumbnail=new_exercise.thumbnail,
            description=new_exercise.description,  
            exercise_level=exercise_levels_follow_question_levels,
            questions=list_of_questions
        ),
        message="Exercise has been created successfully"
    )



async def delete_exercise_by_uuid(id:str, session:AsyncSession):
    if not is_valid_uuid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid exercise uuid {id} 😏")
    que = select(Exercise).where(Exercise.ex_uuid ==id)
    result = await session.execute(que)
    ex = result.scalars().first()

    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise with uuid {id} does not exist 😶‍🌫️")
    if ex.skill_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete because the question is belonging to another skill 😉")

    await session.delete(ex)
    await session.commit()

    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=[],
        message="Exercise has been deleted successfully"
    )


async def list_all_exercises(session:AsyncSession):
    try:
        query = select(Exercise)
        result = await session.execute(query)
        exercises = result.scalars().all()   
        
        #get questions for each exercise
        all_questions:question.ResponseQuestionDto = []
        for exercise in exercises:     
            que = select(Question).where(Question.exercise_id==exercise.id)
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
                    question_level=qu.question_level
                ))
        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_200_OK),
            payload= [RepsonseExerciseDto(
                ex_uuid =ex.ex_uuid,
                title=ex.title,
                thumbnail=ex.thumbnail,
                description=ex.description,
                # skill_uuid = str(None if ex.skill_id==None else ex.skill_id),
                questions= all_questions,
                exercise_level= ex.exercise_level
            ) for ex in exercises],
            message="List all exercises"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

async def get_exercises_by_skill_id(skill_id:str, session:AsyncSession):
    sk = select(Skill).where(Skill.skill_uuid == skill_id)
    re = await session.execute(sk)
    skl = re.scalars(re).first()

    # get all exercises for the skill
    ex = select(Exercise).where(Exercise.skill_id == skl.id)
    re = await session.execute(ex)
    all_exercises = re.scalars(re).all()



    all_questions:question.ResponseQuestionDto = []
    for exercise in all_exercises:     
        que = select(Question).where(Question.exercise_id==exercise.id)
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


    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload= [RepsonseExerciseDto(
            ex_uuid =ex.ex_uuid,
            title=ex.title,
            thumbnail=ex.thumbnail,
            description=ex.description,
            # skill_uuid = str(None if ex.skill_id==None else ex.skill_id),
            questions= all_questions
        ) for ex in all_exercises],
        message="Exercise has been created successfully"
    )

        

    
