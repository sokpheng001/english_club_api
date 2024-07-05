
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.database.schemas import submit_answer
from app.database.cruds.user import find_user_by_uuid
from app.database.cruds.question import get_question_by_uuid
from app.models.user import User
from app.models.question import Question
from app.models.exercise import Exercise
from app.utils.verify import is_valid_uuid
from app.database.schemas.exercise_complete import ExerciseCompleteDto,ResponseExerciseCompleteDto
from datetime import datetime


async def answer_submission(exercise_uuid:str,answer:submit_answer.SubmitAnswerDto, session=AsyncSession):

    # Implement the logic to submit the answer to the database
    based_score = 100
    user_score = 0
    number_of_correct_answers = 0
    total_answers = 0
    us = None
    if find_user_by_uuid(answer.user_uuid, session):
        ru = select(User).where(User.uuid == answer.user_uuid)
        re = await session.execute(ru)
        user = re.scalars().first()
        us = user
    
    #  find exercise
    if not is_valid_uuid(exercise_uuid):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid exercise uuid 😏")
    #  
    e = select(Exercise).where(Exercise.ex_uuid==exercise_uuid)
    re = await session.execute(e)
    ex:Exercise = re.scalars().first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    
    #  find number of questions in exercise
    que = select(Question).filter(Question.exercise_id==ex.id)
    re = await session.execute(que)
    qs:Question = re.scalars().all()
    if not qs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This exercise does not have questions you provided 🥲")
    
    #  verify uuid of question was assigned to the exercise
    database_q_uuid = []
    for q1 in qs:
        database_q_uuid.append(q1.q_uuid)
        total_answers+=len(q1.correct_answer)
    database_q_uuid = set(database_q_uuid) 
    # 
    user_q_uuid = []
    for usq in answer.user_answer:
        user_q_uuid.append(usq.q_uuid)
    user_q_uuid = set(user_q_uuid)

    verify = user_q_uuid - database_q_uuid
    if verify:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Question uuid ' {verify} ' is not in this exercise")
    
    #  verify uuid of question in exercise
    if len(qs) !=len(answer.user_answer):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Number of question uuids is not enough for this exercise. This exercise included with {len(qs)} question")
    
    # validate number of answers user submitted
    total_user_answers = 0
    total_database_answers = 0
    for a in answer.user_answer:
        if not is_valid_uuid(a.q_uuid):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid question uuid ' {a.q_uuid} '")
        #  find questions in exercise
        q = select(Question).where(Question.q_uuid==a.q_uuid)
        re = await session.execute(q)
        question:Question = re.scalars().first()
        if not question: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question  with uuid ' {a.q_uuid} ' not found in this exercise")
        
        # conver from list to dictionary
        # print(question.correct_answer)
        if isinstance(question.correct_answer, list):
            q = question.correct_answer
            dict_from_list = {index: entry for index, entry in enumerate(q)}
            for an in a.answers:
                for index, entry in dict_from_list.items():
                    if an.lower()==entry["answer"].lower():
                        number_of_correct_answers+=1
            total_user_answers+=len(a.answers)
            #  validate the number of correct answers user provided with the number of correct answers in database
            if len(question.correct_answer)>len(a.answers):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Number of answers for question uuid ' {a.q_uuid} ' is not enough")
            # we can validate number of answers user provided when it is greater than number correct answers in database
            # here just write if statement contrast above
        total_database_answers+=len(question.correct_answer)
            # find score based on number of correct answer


    user_score = round(((number_of_correct_answers*10)/total_answers),2) # ទុកក្រោយ ក្បៀស ២ ខ្ទង់
    return ResponseExerciseCompleteDto(
        user_uuid=answer.user_uuid,
        complete_date=datetime.utcnow(),
        exercises= ExerciseCompleteDto(
            ex_uuid=ex.ex_uuid,
            ex_title=ex.title,
            ex_level=ex.exercise_level,
            ex_description=ex.description,
            ex_thumbnail=ex.thumbnail
        ),
        scores=str(user_score)
    )