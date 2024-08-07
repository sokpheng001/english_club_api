from psycopg2 import Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from fastapi import HTTPException, status
from datetime import date
from app.database.schemas import payload,  question, choice
from app.models.question import Question
from app.models.choice import Choice
from app.models.exercise import Exercise
from app.utils.verify import is_valid_uuid
from app.database.schemas.english_level import MyLevel
from app.database.schemas.question_type import QuestionType


async def add_question(q:question.CreateQuestionDto, session:AsyncSession):

    if q.type.upper() not in QuestionType.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Type should be one of 'TRUE_OR_FALSE', 'MULTIPLE_CHOICES', 'FILL_IN_THE_BLANK', but you given {q.type}")
    if q.question_level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {q.question_level}")
    correct_answer = [ans.dict() for ans in q.correct_answer]

    try:
        question_uuid = str(uuid.uuid4())
        new_question =  Question(str(question_uuid),q.question_text, q.voice, q.video, q.image,q.type,correct_answer, question_level=q.question_level.upper())
        
        session.add(new_question)
        await session.commit()
        await session.refresh(new_question)
            #  array of object
        array_of_choices:choice.ResponseChoiceDto = []
        
        for ch in q.choices:
            ch_uuid = str(uuid.uuid4())
            _ch = Choice(ch_uuid,ch.text,ch.is_correct,new_question.id)
            session.add(_ch)
            await session.commit()
            await session.refresh(_ch)
            array_of_choices.append(choice.ResponseChoiceDto(choice_uuid=_ch.choice_uuid, text=_ch.choice_text, is_correct=_ch.is_correct))
        
        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_200_OK),
            payload=question.ResponseQuestionDto(
                q_uuid=new_question.q_uuid,
                question_text=new_question.text,
                voice=new_question.voice,
                video=new_question.video,
                type=new_question.type,
                image=new_question.image,
                question_level=new_question.question_level,
                correct_answer=new_question.correct_answer,
                choices=array_of_choices
            ),
            message= "Question has been created successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

async def get_question_by_level(level:str, session=AsyncSession):
    if level.upper() not in MyLevel.__members__:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Level should be one of A1 to C2, but you given {level}")
    
    qq  = select(Question).filter(Question.question_level.ilike(level))
    result = await session.execute(qq)
    questions = result.scalars().all()


    if not questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question not found")
    
    questions_repsonse:question.ResponseQuestionDto= []

    for q in questions:
        get_all_choices:choice.ResponseChoiceDto = []
        all_choices = select(Choice).filter(Choice.question_id == q.id)
        _all_choices = await session.execute(all_choices)
        get_choices = _all_choices.scalars().all()
        for ch in get_choices:
            get_all_choices.append(choice.ResponseChoiceDto(
                choice_uuid= ch.choice_uuid,
                text=ch.choice_text,
                
                is_correct=ch.is_correct
            ))
        questions_repsonse.append(question.ResponseQuestionDto(
            q_uuid=q.q_uuid,
            question_text=q.text,
            voice=q.voice,
            video=q.video,
            image=q.image,
            type=q.type,
            question_level=q.question_level,
            correct_answer=q.correct_answer,
            choices=get_all_choices
        ))
    
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=questions_repsonse,
        message= "Questions have been found."
    )


async def list_all_questions(session:AsyncSession):
    try:
        query= select(Question).order_by(Question.question_level)
        result = await session.execute(query)
        questions = result.scalars().all()
        quests:Question = []
        for q in questions:
            quests.append(q)
        response:question.ResponseQuestionDto= []
    
        for q in quests:
            get_all_choices:choice.ResponseChoiceDto = []
            all_choices = select(Choice).filter(Choice.question_id == q.id)
            _all_choices = await session.execute(all_choices)
            get_choices = _all_choices.scalars().all()
            for ch in get_choices:
                get_all_choices.append(choice.ResponseChoiceDto(
                    choice_uuid= ch.choice_uuid,
                    text=ch.choice_text,
                    is_correct=ch.is_correct
                ))
            response.append(question.ResponseQuestionDto(
                q_uuid=q.q_uuid,
                question_text=q.text,
                voice=q.voice,
                video=q.video,
                image=q.image,
                type=q.type,
                question_level=q.question_level,
                correct_answer=q.correct_answer,
                choices= get_all_choices
            ))
        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_200_OK),
            payload=response,
            message= "Questions have been retrieved."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_question_by_uuid(id:str, session:AsyncSession):
    if not is_valid_uuid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid uuid provided 😏")
    query = select(Question).filter(Question.q_uuid == id)
    result = await session.execute(query)
    q = result.scalars().first()

    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question is not found")
    if q.exercise_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete question because it is belonging to another excercise 😉")
    else:
        # delete all choices related to the question
        query = select(Choice).filter(Choice.question_id == q.id)
        result = await session.execute(query)
        choices = result.scalars().all()
        for ch in choices:
            await session.delete(ch)
            await session.commit()

        await session.delete(q)
        await session.commit()
        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_204_NO_CONTENT),
            payload=None,
            message= "Question has been deleted successfully."
        )
    
async def get_question_by_uuid(id: str, session=AsyncSession):
    if is_valid_uuid(id):
        q = select(Question).filter(Question.q_uuid==id)
        result = await session.execute(q)
        data:Question =  result.scalars().first()

        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question is not found 😶‍🌫️")

        ch = select(Choice).filter(Choice.question_id == data.id)
        result1 = await session.execute(ch)
        choices = result1.scalars().all()
        
        response:question.ResponseQuestionDto = question.ResponseQuestionDto(
            q_uuid=data.q_uuid,
            question_text=data.text,
            voice=data.voice,
            video=data.video,
            image=data.image,
            type=data.type,
            question_level=data.question_level,
            correct_answer=data.correct_answer,
            choices=[choice.ResponseChoiceDto(
                choice_uuid=ch.choice_uuid,
                text=ch.choice_text,
                is_correct=ch.is_correct
            ) for ch in choices]
        )
        return payload.BaseResponse(
            date=date.today(),
            status=int(status.HTTP_200_OK),
            payload=response,
            message= "Question has been retrieved successfully."
        )
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question uuid is invalid 😏")
    