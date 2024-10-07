"""
This module provides the CLI interface to TaskMaster

We'll use the Click library for this.
"""

import click
from taskmaster.taskmaster import get_tasks, create_task, get_task, TaskNotFound

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