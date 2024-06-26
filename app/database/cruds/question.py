from psycopg2 import Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import Base
import uuid
from fastapi import HTTPException, status
from sqlalchemy import exc
from datetime import date
from app.database.schemas import payload,  question, choice
from app.models.question import Question
from app.models.choice import Choice


async def add_question(q:question.CreateQuestionDto, session:AsyncSession):

    correct_answer = [ans.dict() for ans in q.correct_answer]
    try:
        question_uuid = str(uuid.uuid4())
        new_question = Question(question_uuid,q.text, q.voice, q.video, q.type,correct_answer)
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
                text=new_question.text,
                voice=new_question.voice,
                video=new_question.video,
                type=new_question.type,
                correct_answer=new_question.correct_answer,
                choices=array_of_choices
            ),
            message= "Question has been created successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
async def list_all_questions(session:AsyncSession):
    query= select(Question)
    result = await session.execute(query)
    questions = result.scalars().all()
    response:question.ResponseQuestionDto= []
    for q in questions:
        response.append(question.ResponseQuestionDto(
            q_uuid=q.q_uuid,
            text=q.text,
            voice=q.voice,
            video=q.video,
            type=q.type,
            correct_answer=q.correct_answer,
            choices=q.choices
        ))
    return payload.BaseResponse(
        date=date.today(),
        status=int(status.HTTP_200_OK),
        payload=[],
        message= "Questions has been retrieved successfully."
    )
    