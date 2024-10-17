import click
from taskmaster.database import SessionLocal
from taskmaster.models import Task, Execution, ExecutionWindow, ExecutionWindowStatusEnum, TaskFrequencyEnum, Frequency, DailyFrequency, WeeklyFrequency
from sqlalchemy.exc import NoResultFound
from sqlalchemy import desc, and_
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

HELLO = "hello"
LIST = "list"
ADD = 'add'
CHOICES = [HELLO, LIST, ADD]
DATABASE = "taskmaster.sqlite"

@click.group()
def cli():
    pass

class TaskNotFound(Exception):
    def __init__(self, task_id, message="Task not found"):
        self.task_id = task_id
        self.message = f"{message}: Task ID {task_id}"
        super().__init__(self.message)

class FrequencyNotFound(Exception):
    def __init__(self, frequency_id, message="Frequency not found"):
        self.frequency_id = frequency_id
        self.message = f"{message}: Frequency ID {frequency_id}"
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
        click.echo(f'Edited Task {task.id} - {task.name}')
        session.commit()
    finally:
        session.close()

def get_frequency(frequency_id):
    session = SessionLocal()
    try:
        return session.query(Frequency).filter(Frequency.id == frequency_id).one()
    except NoResultFound:
        raise FrequencyNotFound(frequency_id)
    finally:
        session.close()

def replace_frequency(frequency):
    """ Task Frequency is stored as a polymorphic object
    so changing it involves deleting the old one first"""
    session = SessionLocal()
    existing_frequency = session.query(Frequency).filter(Frequency.task_id == frequency.task_id).one_or_none()

    try:
        if existing_frequency:
            session.delete(existing_frequency)
            session.commit()
            click.echo(f'Removed existing Frequency {existing_frequency.id}')
        session.add(frequency)
        click.echo(f'Created new Frequency {frequency.id} for Task {frequency.task_id}')
        session.commit()
    finally:
        session.close()


@click.command()
def hello():
    click.echo("Hello world")

cli.add_command(hello)

@click.command()
@click.argument('task_id')
def execute(task_id):
    session = SessionLocal()
    task = get_task(task_id)
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

    execution = Execution(task_id=task.id)
    try:
        if hit_execution_window:
            hit_execution_window.status = ExecutionWindowStatusEnum.HIT
            execution.execution_window_id = hit_execution_window.id
        session.add(hit_execution_window)
        session.add(execution)
        session.commit()
        click.echo(f'Execution {execution.id} added for Task {task.id} - {task.name}')
        if hit_execution_window:
            click.echo(f'Hit Execution Window {hit_execution_window.id}')
        return execution
    finally:
        session.close()

cli.add_command(execute)

@click.group()
def task():
    """Task management commands."""
    pass

cli.add_command(task)

def fuzzy_datetime_validator(input, raise_if_invalid = True):
    """
    This helper function will attempt to coerce an input into a datetime. Accepted input formats are:
    * '%Y-%m-%d %H:%M'
    * '%Y-%m-%d' (will set 00:00 as time)
    * '%m-%d' (will set current year and 00:00 as time)
    """
    date = None
    try:
        date = datetime.strptime(input, '%Y-%m-%d %H:%M')
    except ValueError:
        pass

    # This will assume 00:00 is the time
    try:
        date = datetime.strptime(input, '%Y-%m-%d')
    except ValueError:
        pass

    # This will set the current year and assume 00:00 is the time
    try:
        year = datetime.now().year
        input_with_year = f'{year}-{input}'
        date = datetime.strptime(input_with_year, '%Y-%m-%d')
    except ValueError:
        pass

    if not date and raise_if_invalid:
        raise ValueError(f'Provided input {input} cannot be coerced to a datetime')

    return date

@click.command()
@click.argument('task_id')
def schedule(task_id):
    session = SessionLocal()
    try:
        task = get_task(task_id)
        click.echo(f'{task.id} - {task.name}')
    except TaskNotFound as e:
        click.echo(e)
        click.Abort()

    start_datetime_input = click.prompt('Please enter the start date (YYYY-MM-DD or YYYY-MM-DD HH:mm)', type=str, default=datetime.now().strftime("%Y-%m-%d 00:00"))
    start_datetime = fuzzy_datetime_validator(start_datetime_input)

    default_end_datetime = start_datetime + timedelta(days=1)
    end_datetime_input = click.prompt('Please enter the end date (YYYY-MM-DD or YYYY-MM-DD HH:mm)', type=str, default=default_end_datetime.strftime("%Y-%m-%d 00:00"))
    end_datetime = fuzzy_datetime_validator(end_datetime_input)

    execution_window = ExecutionWindow(task_id=task.id, start=start_datetime, end=end_datetime)
    try:
        session.add(execution_window)
        session.commit()
        click.echo(f'Added an Execution Window ({execution_window.id}) for Task {task.id} - {task.name} between {execution_window.start} and {execution_window.end}')
    finally:
        session.close()

task.add_command(schedule)

@click.command()
@click.argument('task_id')
def edit(task_id):
    session = SessionLocal()
    try:
        task = get_task(task_id)
        click.echo(f'{task.id} - {task.name}')
    except TaskNotFound as e:
        click.echo(e)
        click.Abort()

    # The call to edit_task will commit the task, unbinding it from the Session
    # and making the Frequency unavailable
    old_frequency = task.frequency
    old_frequency_type = old_frequency and old_frequency.type
    old_frequency_id = old_frequency and old_frequency.id

    task.name = click.prompt('New name of task', type=str, default=task.name)
    edit_task(task)

    change_frequency = click.prompt(f'Do you want to change the task Frequency (currently {old_frequency_type})?', type=bool,
        default=False)

    if change_frequency:
        edit_frequency(str(old_frequency_id))

task.add_command(edit)

@click.command()
@click.argument('frequency_id')
def edit_frequency(frequency_id):
    """Editing a Frequency is a bit messy because this is a polymorphic object
    so if the type changes we need to delete and recreate the object entirely.
    Easier to just do this in all cases"""
    session = SessionLocal()
    try:
        old_frequency = get_frequency(frequency_id)
        click.echo(f'{old_frequency.id}')
    except FrequencyNotFound as e:
        click.echo(e)
        click.Abort()

    new_frequency_type_value = click.prompt('Choose Frequency type', type=click.Choice([e.value for e in TaskFrequencyEnum], case_sensitive=False), show_choices=True, default=TaskFrequencyEnum.DAILY.value)
    new_frequency_type = TaskFrequencyEnum(new_frequency_type_value)

    if new_frequency_type == TaskFrequencyEnum.DAILY:
        new_frequency = DailyFrequency(task_id=old_frequency.task_id)
    elif new_frequency_type == TaskFrequencyEnum.WEEKLY:
        day_of_week = click.prompt('Choose day of week (1 = Monday)', type=click.Choice(['1', '2', '3', '4', '5', '6', '7']), default='1')
        new_frequency = WeeklyFrequency(task_id=old_frequency.task_id, day_of_week=int(day_of_week))

    replace_frequency(new_frequency)

task.add_command(edit_frequency)

if __name__ == '__main__':
    cli()