from fastapi import APIRouter, Depends, HTTPException,  BackgroundTasks, status
from typing import Annotated
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.utils.logger import logger_config
from app.core.database import get_session

from app.quiz.quiz.crud import runtime_quiz_engine
from app.quiz.answersheet.crud import crud_answer_sheet, crud_answer_slot
from app.quiz.quiz.crud import quiz_setting_engine

from app.quiz.quiz.models import RuntimeQuizGenerated
from app.quiz.answersheet.models import (AnswerSheet, AnswerSlot, AnswerSlotOption,
                                         AnswerSheetCreate, AnswerSheetUpdate, AnswerSheetRead,
                                         AnswerSlotCreate, AnswerSlotUpdate, AnswerSlotRead, AttemptQuizRequest)

logger = logger_config(__name__)

router = APIRouter()

# ------------------------------
# Quiz Generation Endpoint
# ------------------------------

# Take Quiz ID and Generate Quiz For Student
# DOMAIN LEVEL = 0. Ensure student have not attempted the quiz before
# 1. Verify Student ID & Quiz ID are valid & Quiz is between Start & End Date
# 2. Generate Quiz with Randomly Shuffled Questions
# 3. Return Quiz with Questions
# DOMAIN LEVEL = 4. After calling it we will create Quiz Attempt and then return the Quiz with Questions


@router.post("/attempt", response_model=RuntimeQuizGenerated)
async def generate_runtime_quiz_for_student(attempt_ids: AttemptQuizRequest, db: Annotated[AsyncSession, Depends(get_session)]):

    logger.info(f"Generating Quiz for Student: {__name__}")

    try:
        # 0. Ensure student have not attempted the quiz before
        quiz_id: int = attempt_ids.quiz_id
        quiz_key: str = attempt_ids.quiz_key
        student_id: int = attempt_ids.student_id

        has_attempted = await crud_answer_sheet.student_answer_sheet_exists(db, user_id=student_id, quiz_id=quiz_id)
        print("\n-----has_attempted----\n", has_attempted)
        if has_attempted:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You have already attempted this quiz")

        # Checl if quiz key is valid
        quiz_key_valid = await quiz_setting_engine.validate_quiz_key(db=db, quiz_id=quiz_id, quiz_key=quiz_key)
        print("\n-----quiz_key_valid----\n", quiz_key_valid)

        runtime_quiz = await runtime_quiz_engine.generate_quiz(quiz_id=quiz_id, quiz_key=quiz_key, student_id=student_id, db=db)
        print("\n--LEN---runtime_quiz----\n", len(runtime_quiz.quiz_settings))

        # 1 TODO: Create Quiz Attempt
        quiz_attempt_response = await crud_answer_sheet.create_answer_sheet(db_session=db,
                                                                            answer_sheet_obj_in=AnswerSheetCreate(student_id == student_id,
                                                                                                                  quiz_id=quiz_id, quiz_key=quiz_key,
                                                                                                                  time_limit=runtime_quiz.quiz_settings[
                                                                                                                      0].time_limit,
                                                                                                                  total_points=runtime_quiz.total_points,
                                                                                                                  time_start=datetime.now()))

        runtime_quiz.answer_sheet = quiz_attempt_response
        runtime_quiz.instructions = runtime_quiz.quiz_settings[0].instructions

        return runtime_quiz
    except HTTPException as http_err:
        logger.error(f"generate_quiz Error: {http_err}")
        raise http_err

    except Exception as err:
        logger.error(f"generate_quiz Error: {err}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")


# ~ Get Quiz Attempt By ID
@router.get("/{quiz_attempt_id}", response_model=AnswerSheetRead)
async def get_quiz_attempt_by_id(
        quiz_attempt_id: int,
        db: Annotated[AsyncSession, Depends(get_session)]):
    """
    Gets a Quiz Answer Sheet by its id
    """
    try:

        is_active = await crud_answer_sheet.is_answer_sheet_active(db_session=db, answer_sheet_id=quiz_attempt_id)
        print("\n------------ is_active ------------\n", is_active)

        quiz_attempt = await crud_answer_sheet.get_answer_sheet_by_id(db, quiz_attempt_id)
        return quiz_attempt

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ~ Update Quiz Attempt - Finish Quiz


@router.patch("/{quiz_attempt_id}/finish")
async def update_quiz_attempt(
        quiz_attempt_id: str,
        db_session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Update Quiz Attempt
    """
    try:
        quiz_attempt_response = await crud_answer_sheet.finish_answer_sheet_attempt(db_session, quiz_attempt_id)
        return quiz_attempt_response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# # ---------------------
# # QuizAnswerSlot
# # ---------------------


@router.post("/answer_slot/save", response_model=AnswerSlotRead)
async def save_quiz_answer_slot(
        background_tasks: BackgroundTasks,
        quiz_answer_slot: AnswerSlotCreate,
        db_session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Saves a student attempted Quiz Answer Slot
    """
    try:
        # 1. ValidateIf Quiz is Active & Quiz Attempt ID is Valid
        quiz_attempt = await crud_answer_sheet.is_answer_sheet_active(db_session, quiz_answer_slot.quiz_attempt_id)
        if not quiz_attempt:
            raise ValueError("Quiz Time has Ended or Invalid Quiz Attempt ID")

        # 2. Save Quiz Answer Slot
        quiz_answer_slot_response = await crud_answer_slot.create_quiz_answer_slot(db_session, quiz_answer_slot)

        # 2.1 RUN A BACKGROUND TASK TO UPDATE THE POINTS AWARDED
        background_tasks.add_task(
            crud_answer_slot.grade_quiz_answer_slot, db_session, quiz_answer_slot_response)

        # 3. Return Quiz Answer Slot
        return quiz_answer_slot_response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
