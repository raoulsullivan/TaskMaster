import click
from taskmaster.database import SessionLocal
from taskmaster.models import Task, Execution
from sqlalchemy.exc import NoResultFound
from sqlalchemy import desc

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
    execution = Execution(task_id=task.id)
    try:
        session.add(execution)
        session.commit()
        click.echo(f'Execution {execution.id} added for Task {task.id} - {task.name}')
        return execution
    finally:
        session.close()

cli.add_command(execute)

if __name__ == '__main__':
    cli()