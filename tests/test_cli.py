import unittest
from unittest.mock import patch, MagicMock
import click
from click.testing import CliRunner

from taskmaster.cli import list, new, cli

class TestCliTasksListCommand(unittest.TestCase):
    
    @patch('taskmaster.cli.get_tasks')
    @patch('taskmaster.cli.click.echo')
    def test_list_command(self, mock_echo, mock_get_tasks):
        # Mock the tasks that get_tasks() should return
        mock_task_1 = MagicMock(id=1)
        mock_task_1.name = 'Task 1'
        mock_task_2 = MagicMock(id=2)
        mock_task_2.name = 'Task 2'
        mock_get_tasks.return_value = [
            mock_task_1, mock_task_2
        ]

        # Use CliRunner to invoke the Click command
        runner = CliRunner()
        result = runner.invoke(list)

        # Assert that the command executed successfully
        self.assertEqual(result.exit_code, 0)

        # Check that click.echo was called with the correct output
        mock_echo.assert_any_call('1 - Task 1')
        mock_echo.assert_any_call('2 - Task 2')
        
        # Assert that echo was called twice (once for each task)
        self.assertEqual(mock_echo.call_count, 2)

class TestCliTasksNewCommand(unittest.TestCase):

    @patch('taskmaster.cli.create_task')
    @patch('taskmaster.cli.click.echo')
    def test_new_command(self, mock_echo, mock_create_task):
        task_name = 'Some task'
        mock_task_1 = MagicMock(id=1)
        mock_task_1.name = task_name
        mock_create_task.return_value = mock_task_1

        runner = CliRunner()
        result = runner.invoke(new, [task_name])

        self.assertEqual(result.exit_code, 0)

        mock_echo.assert_called_once_with(f'Created 1 - {task_name}')


class TestCliTaskShowCommand(unittest.TestCase):

    @patch('taskmaster.cli.get_task')
    @patch('taskmaster.cli.click.echo')
    def test_task_group(self, mock_echo, mock_get_task):
        task_name = 'Some task'
        mock_task_1 = MagicMock(id=1)
        mock_task_1.name = task_name
        mock_get_task.return_value = mock_task_1

        runner = CliRunner()
        result = runner.invoke(cli, ['task', '1', 'show'])

        self.assertEqual(result.exit_code, 0)
