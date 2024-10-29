"""
This module contains the application logic for Taskmaster
including the functions that speak to the database.

Call the functions here from the modules that contain the interfaces
"""

from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from taskmaster.database import SessionLocal
from taskmaster.models import (DailyFrequency, Execution, ExecutionWindow,
                               ExecutionWindowStatusEnum, Frequency, Task)


DATABASE = "taskmaster.sqlite"


class TaskNotFound(Exception):
    def __init__(self, task_id, message="Task not found"):
        self.task_id = task_id
        self.message = f"{message}: Task ID {task_id}"
        super().__init__(self.message)


class FrequencyNotFound(Exception):
    def __init__(self, task_id, message="Frequency not found for Task"):
        self.task_id = task_id
        self.message = f"{message}: Task ID {task_id}"
        super().__init__(self.message)


def get_tasks():
    session = SessionLocal()
    try:
        tasks = session.query(Task).all()
    finally:
        session.close()
    return tasks


def create_task(name):
    session = SessionLocal()
    task = Task(name=name)
    task.frequency = DailyFrequency()
    try:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    finally:
        session.close()


def get_task(task_id):
    session = SessionLocal()
    try:
        return session.query(Task).options(
            joinedload(Task.executions),
            joinedload(Task.execution_windows),
            joinedload(Task.frequency)
        ).filter(Task.id == task_id).one()
    except NoResultFound:
        raise TaskNotFound(task_id)
    finally:
        session.close()


def edit_task(task):
    session = SessionLocal()
    try:
        session.add(task)
        session.commit()
    finally:
        session.close()


def get_frequency_by_task_id(task_id):
    session = SessionLocal()
    try:
        return (session.query(Frequency)
                .filter(Frequency.task_id == task_id).one())
    except NoResultFound:
        raise FrequencyNotFound(task_id)
    finally:
        session.close()


def replace_frequency(frequency):
    """ Task Frequency is stored as a polymorphic object
    so changing it involves deleting the old one first"""
    session = SessionLocal()
    existing_frequency = (session.query(Frequency)
                          .filter(Frequency.task_id == frequency.task_id)
                          .one_or_none())

    try:
        if existing_frequency:
            session.delete(existing_frequency)
            session.commit()
        session.add(frequency)
        session.commit()
    finally:
        session.close()


def execute_task(task_id):
    """Creates an execution, also marks any open execution window as hit"""
    session = SessionLocal()
    current_time = datetime.utcnow()

    # The "hit" execution window is the one for this task that's currently open
    hit_execution_window = session.query(ExecutionWindow).filter(
        and_(
            ExecutionWindow.task_id == task_id,
            ExecutionWindow.status == ExecutionWindowStatusEnum.OPEN,
            ExecutionWindow.start <= current_time,
            ExecutionWindow.end >= current_time
            )
        ).one_or_none()
    execution = Execution(task_id=task_id)
    try:
        if hit_execution_window:
            hit_execution_window.status = ExecutionWindowStatusEnum.HIT
            execution.execution_window = hit_execution_window
            session.add(hit_execution_window)
        session.add(execution)
        session.commit()
        # Reload to get the execution window
        execution = session.query(Execution).options(
            joinedload(Execution.execution_window)
        ).filter(Execution.id == execution.id).one()
        return execution
    finally:
        session.close()


def add_execution_window(execution_window):
    session = SessionLocal()
    try:
        session.add(execution_window)
        session.commit()
    finally:
        session.close()
