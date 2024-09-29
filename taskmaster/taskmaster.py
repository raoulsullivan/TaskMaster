import click
from taskmaster.database import SessionLocal
from taskmaster.models import Task, Execution, ExecutionWindow, ExecutionWindowStatusEnum
from sqlalchemy.exc import NoResultFound
from sqlalchemy import desc, and_
from datetime import datetime, timedelta

HELLO = "hello"
LIST = "list"
ADD = 'add'
CHOICES = [HELLO, LIST, ADD]
DATABASE = "taskmaster.sqlite"

@click.group()
def cli():
    pass

def get_tasks():
    session = SessionLocal()
    try:
        tasks = session.query(Task).all()
    finally:
        session.close()
    return tasks

@click.command()
def hello():
    click.echo("Hello world")

cli.add_command(hello)

@click.command()
def list():
    tasks = get_tasks()
    for task in tasks:
        click.echo(f'{task.id} - {task.name}')

cli.add_command(list)

@click.command()
@click.argument('task_id')
def show(task_id):
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).one()
        executions = session.query(Execution).filter(Execution.task_id == task.id).order_by(desc(Execution.executed_at)).all()
        click.echo(f'{task.id} - {task.name}')
        click.echo()
        click.echo('Executions:')
        for execution in executions:
            click.echo(f'{execution.executed_at.strftime("%Y-%m-%d %H:%M")}')
    except NoResultFound:
        click.echo(f'Task with id {task_id} not found')

cli.add_command(show)

@click.command()
@click.argument('name')
def add_task(name):
    session = SessionLocal()
    task = Task(name=name)
    try:
        session.add(task)
        session.commit()
        return task
    finally:
        session.close()

cli.add_command(add_task)

@click.command()
@click.argument('task_id')
def execute(task_id):
    session = SessionLocal()
    task = session.query(Task).filter(Task.id == task_id).one()
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
        task = session.query(Task).filter(Task.id == task_id).one()
        click.echo(f'{task.id} - {task.name}')
    except NoResultFound:
        click.echo(f'Task with id {task_id} not found')
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

if __name__ == '__main__':
    cli()