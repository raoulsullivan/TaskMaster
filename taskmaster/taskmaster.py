import click
from taskmaster.database import SessionLocal
from taskmaster.models import Task

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
@click.argument('name')
def add_task(name):
    session = SessionLocal()
    task = Task(name=name)
    try:
        session.add(task)
        session.commit()
    finally:
        session.close()
    return task

cli.add_command(add_task)

if __name__ == '__main__':
    cli()