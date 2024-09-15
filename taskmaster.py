import argparse
import sqlite3

HELLO = "hello"
LIST = "list"
CHOICES = [HELLO, LIST]
DATABASE = "taskmaster.sqlite"

def get_tasks():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    with con:
        res = con.execute('SELECT "test" AS name')
        tasks = res.fetchall()
    con.close()
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