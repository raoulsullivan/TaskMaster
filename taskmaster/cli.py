"""
This module provides the CLI interface to TaskMaster

We'll use the Click library for this.
"""

import click
from taskmaster.taskmaster import get_tasks

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