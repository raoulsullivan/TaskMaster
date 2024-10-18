"""
This module provides the CLI interface to TaskMaster

We'll use the Click library for this.
"""

import click
from taskmaster.taskmaster import get_tasks, create_task, get_task, edit_task, TaskNotFound, get_frequency_by_task_id, FrequencyNotFound, replace_frequency, execute_task, add_execution_window
from taskmaster.models import TaskFrequencyEnum, WeeklyFrequency, DailyFrequency, ExecutionWindow
from taskmaster.utils import fuzzy_datetime_validator
from datetime import datetime, timedelta

@click.group()
def cli():
    pass

@click.group()
def tasks():
    """Task management commands."""
    pass

cli.add_command(tasks)

@click.command()
def list():
    tasks = get_tasks()
    for task in tasks:
        click.echo(f'{task.id} - {task.name}')

tasks.add_command(list)

@click.command()
@click.argument('name')
def new(name):
    task = create_task(name)
    click.echo(f'Created {task.id} - {task.name}')

tasks.add_command(new)

@click.group()
@click.argument('task_id')
@click.pass_context
def task(ctx, task_id):
    try:
        task = get_task(task_id)
        ctx.obj = {'task': task}
        click.echo(f'Task {task.id} - {task.name}')
    except TaskNotFound as e:
        click.echo(e)
        raise click.Abort()

cli.add_command(task)

@click.command()
@click.pass_context
def show(ctx):
    task = ctx.obj['task']
    click.echo()
    click.echo('Frequency:')
    click.echo(task.frequency.type)
    click.echo()
    click.echo('Execution Windows:')
    for execution_window in task.execution_windows:
        click.echo(f'{execution_window.id} - {execution_window.start.strftime("%Y-%m-%d %H:%M")} to {execution_window.end.strftime("%Y-%m-%d %H:%M")} - ', nl=False)
        click.secho(execution_window.status.value.upper(), fg='green')
    click.echo()
    click.echo('Executions:')
    for execution in task.executions:
        click.echo(f'{execution.executed_at.strftime("%Y-%m-%d %H:%M")}')

task.add_command(show)

@click.command()
@click.pass_context
def edit(ctx):
    task = ctx.obj['task']

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
        ctx.invoke(edit_frequency)

task.add_command(edit)

@click.command()
@click.pass_context
def edit_frequency(ctx):
    """Editing a Frequency is a bit messy because this is a polymorphic object
    so if the type changes we need to delete and recreate the object entirely.
    Easier to just do this in all cases"""
    task = ctx.obj['task']

    try:
        old_frequency = get_frequency_by_task_id(task.id)
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

@click.command()
@click.pass_context
def execute(ctx):
    task = ctx.obj['task']
    execution = execute_task(task.id)
    click.echo(f'Execution {execution.id} added for Task {task.id} - {task.name}')
    if execution.execution_window:
        click.echo(f'Hit Execution Window {execution.execution_window.id}')

task.add_command(execute)

@click.command()
@click.pass_context
def schedule(ctx):
    task = ctx.obj['task']

    start_datetime_input = click.prompt('Please enter the start date (YYYY-MM-DD or YYYY-MM-DD HH:mm)', type=str, default=datetime.now().strftime("%Y-%m-%d 00:00"))
    start_datetime = fuzzy_datetime_validator(start_datetime_input)

    default_end_datetime = start_datetime + timedelta(days=1)
    end_datetime_input = click.prompt('Please enter the end date (YYYY-MM-DD or YYYY-MM-DD HH:mm)', type=str, default=default_end_datetime.strftime("%Y-%m-%d 00:00"))
    end_datetime = fuzzy_datetime_validator(end_datetime_input)

    execution_window = ExecutionWindow(task_id=task.id, start=start_datetime, end=end_datetime)
    add_execution_window(execution_window)
    click.echo(f'Added an Execution Window ({execution_window.id}) for Task {task.id} - {task.name} between {execution_window.start} and {execution_window.end}')

task.add_command(schedule)