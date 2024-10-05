from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import enum

Base = declarative_base()


class ExecutionWindowStatusEnum(enum.Enum):
    OPEN = "open"
    HIT = "hit"
    SKIPPED = "skipped"
    MISSED = "missed"

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    executions = relationship('Execution', backref='task')

class Execution(Base):
    __tablename__ = 'executions'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='RESTRICT'), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    execution_window_id = Column(Integer, ForeignKey('execution_windows.id', ondelete='RESTRICT'), nullable=True)

class ExecutionWindow(Base):
    """
    This fellow represents a period of time during which a task should be executed.
    """
    __tablename__ = 'execution_windows'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='RESTRICT'), nullable=False)
    start = Column(DateTime, default=datetime.utcnow, nullable=False)
    end = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(ExecutionWindowStatusEnum), default=ExecutionWindowStatusEnum.OPEN, nullable=False)

    executions = relationship('Execution', backref='execution_window')