
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
    # fetch question for the exercise
    # check if uuid of question is valid
    for quuid in ex.q_uuids:
        if not is_valid_uuid(quuid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid question UUID 😏")
    if len(ex.q_uuids) > 1:
        if all(x==ex.q_uuids[0] for x in ex.q_uuids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question UUIDs are same 😏")
    list_of_questions:question.ResponseQuestionDto = []
    for qid in ex.q_uuids:
        qq = select(Question).filter(Question.q_uuid == qid)
        req = await session.execute(qq)
        q = req.scalars().first()
        #check if the question is already assigned to the exercise
        if not q:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question {qid} is not found 😶‍🌫️")
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
    # check if all questions have different levels
    if len(list_of_questions) >1:
        for qq in list_of_questions:
            if qq.question_level != list_of_questions[0].question_level:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"All questions must be in the same level 😉, please check question before input.")
    #create a question
    exercise_uuid =str(uuid.uuid4()) # generate unique identifier for the exercise
    new_exercise  = None
    new_exercise =  Exercise(exercise_uuid, ex.title,ex.thumbnail,
                                 ex.description,
                                 tip = ex.tip,
                                 exercise_level=q.question_level,
                                 reading_text=ex.reading_text,voice=ex.voice,transcript=ex.transcript
                                 )
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
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload= RepsonseExerciseDto(
            ex_uuid =new_exercise.ex_uuid,
            title=new_exercise.title,
            thumbnail=new_exercise.thumbnail,
            description=new_exercise.description,  
            tip=new_exercise.tip,
            exercise_level=q.question_level,
            questions=list_of_questions
        ),
        message="Exercise has been created successfully"
    )


async def delete_exercise_by_uuid(id:str, session:AsyncSession):
    if not is_valid_uuid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid exercise uuid 😏")
    que = select(Exercise).where(Exercise.ex_uuid ==id)
    result = await session.execute(que)
    ex = result.scalars().first()

    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise with uuid {id} not found 😶‍🌫️")
    if ex.skill_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete because the question is belonging to another skill 😉")

    await session.delete(ex)
    await session.commit()

    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_204_NO_CONTENT),
        payload=id,
        message="Exercise has been deleted successfully"
    )


async def list_all_exercises(session:AsyncSession):
    try:
        query = select(Exercise).order_by(Exercise.exercise_level)
        result = await session.execute(query)
        exercises = result.scalars().all()   
        
        all_exercises:RepsonseExerciseDto = []

        for exercise in exercises:     
            que = select(Question).where(Question.exercise_id==exercise.id)
            req = await session.execute(que)
            q = req.scalars().all()
            #get questions for each exercise
            all_questions:question.ResponseQuestionDto = []
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
            all_exercises.append(RepsonseExerciseDto(
                ex_uuid =exercise.ex_uuid,
                title=exercise.title,
                thumbnail=exercise.thumbnail,
                description=exercise.description,
                tip=exercise.tip,
                reading_text=exercise.reading_text,
                voice=exercise.voice,
                transcript=exercise.transcript,
                # skill_uuid = str(None if ex.skill_id==None else ex.skill_id),
                questions= all_questions,
                exercise_level= exercise.exercise_level
            )) # clear all questions because don't want to use them again for new exercises


        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_200_OK),
            payload= all_exercises,
            message="List all exercises"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

async def find_exercise_by_uuid(id:str, session=AsyncSession)->RepsonseExerciseDto:
    if not is_valid_uuid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid exercise uuid {id} 😏")
    que = select(Exercise).where(Exercise.ex_uuid ==id)
    result = await session.execute(que)
    ex:Exercise = result.scalars().first()

    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exercise with uuid {id} not found 😶‍🌫️")
    
    # get question throught exercise
    que = select(Question).filter(Question.exercise_id==ex.id)
    req = await session.execute(que)
    qs = req.scalars().all()
    all_questions:question.ResponseQuestionDto = []

    if qs:
        for  q in qs:
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
            all_questions.append(question.ResponseQuestionDto(
                q_uuid= q.q_uuid,
                question_text = q.text,
                voice= q.voice,
                video= q.video,
                type= q.type,
                correct_answer = q.correct_answer,
                choices= response_for_choices,
                question_level=q.question_level
            ))
    return RepsonseExerciseDto(
            ex_uuid =ex.ex_uuid,
            title=ex.title,
            thumbnail=ex.thumbnail,
            description=ex.description,
            tip=ex.tip,
            # skill_uuid = str(None if ex.skill_id==None else ex.skill_id),
            questions=all_questions,
            exercise_level= ex.exercise_level,
            reading_text=ex.reading_text,
            transcript=ex.transcript,
            voice=ex.voice
        )



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
            tip=ex.tip,
            reading_text=ex.reading_text,
            transcript=ex.transcript,
            voice=ex.voice,
            # skill_uuid = str(None if ex.skill_id==None else ex.skill_id),
            questions= all_questions
        ) for ex in all_exercises],
        message="Exercise has been created successfully"
    )

        

    
