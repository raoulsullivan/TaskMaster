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

class TaskFrequencyEnum(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    #MONTHLY = "monthly-date" # e.g. "1st of every month"
    #MONTHLY = "monthly-day" # e.g. "Last Sunday of every month"

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    executions = relationship('Execution', backref='task')
    frequency = relationship('Frequency', backref='task', uselist=False, cascade="all, delete-orphan")

class Frequency(Base):
    """Frequencies determine how often a task should be performed"""
    __tablename__ = "frequencies"
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': 'frequency'
    }
    id = Column(Integer, primary_key=True)
    type = Column(Enum(TaskFrequencyEnum), default=TaskFrequencyEnum.DAILY, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), unique=True, nullable=False)

class DailyFrequency(Frequency):
    __tablename__ = "daily_frequencies"
    __mapper_args__ = {
        'polymorphic_identity': TaskFrequencyEnum.DAILY
    }
    id = Column(Integer, ForeignKey('frequencies.id'), primary_key=True)

class WeeklyFrequency(Frequency):
    __tablename__ = "weekly_frequencies"
    __mapper_args__ = {
        'polymorphic_identity': TaskFrequencyEnum.WEEKLY
    }
    id = Column(Integer, ForeignKey('frequencies.id'), primary_key=True)
    day_of_week = Column(Integer)

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