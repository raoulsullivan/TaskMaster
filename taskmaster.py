import argparse
import sqlite3
from database import SessionLocal
from models import Task

HELLO = "hello"
LIST = "list"
CHOICES = [HELLO, LIST]
DATABASE = "taskmaster.sqlite"

def get_tasks():
    session = SessionLocal()
    try:
        tasks = session.query(Task).all()
    finally:
        session.close()
    return tasks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TaskMaster')
    parser.add_argument('command', type=str, choices=CHOICES, 
                        help='The command for TaskMaster to run.')
    args = parser.parse_args()
    match args.command:
        case 'hello':
            print("hello world")
        case 'list':
            for task in get_tasks():
                print(task['name'])
        case _:
            raise NotImplementedError("Missing default action")