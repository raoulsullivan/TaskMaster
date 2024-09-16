import argparse
import sqlite3
from database import SessionLocal
from models import Task

HELLO = "hello"
LIST = "list"
ADD = 'add'
CHOICES = [HELLO, LIST, ADD]
DATABASE = "taskmaster.sqlite"

def get_tasks():
    session = SessionLocal()
    try:
        tasks = session.query(Task).all()
    finally:
        session.close()
    return tasks

def add_task(name):
    session = SessionLocal()
    task = Task(name=name)
    try:
        session.add(task)
        session.commit()
    finally:
        session.close()
    return task
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TaskMaster')
    parser.add_argument('command', type=str, choices=CHOICES, 
                        help='The command for TaskMaster to run.')
    parser.add_argument('-n', '--name', type=str, 
                        help='The name of the task to add')
    args = parser.parse_args()
    match args.command:
        case 'hello':
            print("hello world")
        case 'list':
            for task in get_tasks():
                print(task.name)
        case 'add':
            name = args.name
            if not name:
                raise ValueError("Name cannot be None")
            add_task(name)
            print(f'Task {name} added')
        case _:
            raise NotImplementedError("Missing default action")