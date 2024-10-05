import unittest
from unittest.mock import patch, MagicMock
import click
from click.testing import CliRunner

from taskmaster.taskmaster import list

class TestListCommand(unittest.TestCase):
    
    @patch('taskmaster.taskmaster.get_tasks')
    @patch('taskmaster.taskmaster.click.echo')
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