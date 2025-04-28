# tests/test_basic.py

import pytest
import os
import sys
import json
from datetime import datetime, timedelta
import tempfile
from src.tasks import load_tasks, set_task_recurrence, get_next_occurrence_date, generate_next_occurrence

# Add the parent directory to path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import tasks  # Import the tasks module

class TestTaskFunctions:
    """Unit tests for the task management functions"""
    
    @pytest.fixture
    def sample_tasks(self):
        """Fixture to create a sample list of tasks for testing"""
        return [
            {
                "id": 1,
                "title": "Task 1",
                "description": "Description for task 1",
                "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "priority": "High",
                "category": "Work",
                "completed": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 2,
                "title": "Task 2",
                "description": "Description for task 2",
                "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "priority": "Medium",
                "category": "Personal",
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": 3,
                "title": "Task 3",
                "description": "Description for task 3",
                "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "priority": "Low",
                "category": "Work",
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    
    @pytest.fixture
    def temp_tasks_file(self):
        """Fixture to create a temporary tasks file for testing file operations"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_name = temp_file.name
            yield temp_name
        # Clean up the file after the test
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
    
    def test_load_tasks_empty_file(self, temp_tasks_file):
        """Test loading tasks from a non-existent file"""
        # Ensure the file doesn't exist
        if os.path.exists(temp_tasks_file):
            os.remove(temp_tasks_file)
        
        loaded_tasks = tasks.load_tasks(temp_tasks_file)
        assert loaded_tasks == []
    
    def test_load_and_save_tasks(self, sample_tasks, temp_tasks_file):
        """Test saving and loading tasks to/from a file"""
        # Save tasks to file
        tasks.save_tasks(sample_tasks, temp_tasks_file)
        
        # Load tasks from file
        loaded_tasks = tasks.load_tasks(temp_tasks_file)
        
        # Verify the loaded tasks match the saved tasks
        assert len(loaded_tasks) == len(sample_tasks)
        for original, loaded in zip(sample_tasks, loaded_tasks):
            assert original["id"] == loaded["id"]
            assert original["title"] == loaded["title"]
    
    def test_load_tasks_corrupted_json(self, temp_tasks_file):
        """Test loading tasks from a corrupted JSON file"""
        # Write invalid JSON to the file
        with open(temp_tasks_file, 'w') as f:
            f.write("This is not valid JSON")
        
        # Attempt to load tasks
        loaded_tasks = tasks.load_tasks(temp_tasks_file)
        
        # Should return empty list for corrupted file
        assert loaded_tasks == []
    
    def test_generate_unique_id(self, sample_tasks):
        """Test generating a unique ID for a new task"""
        # With existing tasks
        unique_id = tasks.generate_unique_id(sample_tasks)
        assert unique_id == 4  # Should be max ID (3) + 1
        
        # With empty task list
        unique_id = tasks.generate_unique_id([])
        assert unique_id == 1
    
    def test_filter_tasks_by_priority(self, sample_tasks):
        """Test filtering tasks by priority level"""
        # Test high priority
        high_priority = tasks.filter_tasks_by_priority(sample_tasks, "High")
        assert len(high_priority) == 1
        assert high_priority[0]["id"] == 1
        
        # Test medium priority
        medium_priority = tasks.filter_tasks_by_priority(sample_tasks, "Medium")
        assert len(medium_priority) == 1
        assert medium_priority[0]["id"] == 2
        
        # Test low priority
        low_priority = tasks.filter_tasks_by_priority(sample_tasks, "Low")
        assert len(low_priority) == 1
        assert low_priority[0]["id"] == 3
        
        # Test non-existent priority
        non_existent = tasks.filter_tasks_by_priority(sample_tasks, "Critical")
        assert len(non_existent) == 0
    
    def test_filter_tasks_by_category(self, sample_tasks):
        """Test filtering tasks by category"""
        # Test Work category
        work_tasks = tasks.filter_tasks_by_category(sample_tasks, "Work")
        assert len(work_tasks) == 2
        assert work_tasks[0]["id"] == 1
        assert work_tasks[1]["id"] == 3
        
        # Test Personal category
        personal_tasks = tasks.filter_tasks_by_category(sample_tasks, "Personal")
        assert len(personal_tasks) == 1
        assert personal_tasks[0]["id"] == 2
        
        # Test non-existent category
        non_existent = tasks.filter_tasks_by_category(sample_tasks, "Shopping")
        assert len(non_existent) == 0
    
    def test_filter_tasks_by_completion(self, sample_tasks):
        """Test filtering tasks by completion status"""
        # Test completed tasks
        completed = tasks.filter_tasks_by_completion(sample_tasks, True)
        assert len(completed) == 1
        assert completed[0]["id"] == 1
        
        # Test incomplete tasks
        incomplete = tasks.filter_tasks_by_completion(sample_tasks, False)
        assert len(incomplete) == 2
        assert incomplete[0]["id"] == 2
        assert incomplete[1]["id"] == 3
    
    def test_search_tasks(self, sample_tasks):
        """Test searching tasks by query"""
        # Test searching by title
        title_search = tasks.search_tasks(sample_tasks, "Task 1")
        assert len(title_search) == 1
        assert title_search[0]["id"] == 1
        
        # Test searching by description
        desc_search = tasks.search_tasks(sample_tasks, "description for task")
        assert len(desc_search) == 3  # All tasks contain this
        
        # Test case insensitivity
        case_search = tasks.search_tasks(sample_tasks, "TASK")
        assert len(case_search) == 3  # All tasks contain "task" in title
        
        # Test partial match
        partial_search = tasks.search_tasks(sample_tasks, "ask 2")
        assert len(partial_search) == 1
        assert partial_search[0]["id"] == 2
        
        # Test no match
        no_match = tasks.search_tasks(sample_tasks, "nonexistent")
        assert len(no_match) == 0
    
    def test_get_overdue_tasks(self):
        """Test getting overdue tasks"""
        # Create tasks with specific due dates
        test_tasks = [
            {
                "id": 1,
                "title": "Overdue Task",
                "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "completed": False
            },
            {
                "id": 2,
                "title": "Overdue but Completed",
                "due_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "completed": True
            },
            {
                "id": 3,
                "title": "Future Task",
                "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "completed": False
            },
            {
                "id": 4,
                "title": "No Due Date",
                "completed": False
            }
        ]
        
        overdue = tasks.get_overdue_tasks(test_tasks)
        
        # Only Task 1 should be overdue
        assert len(overdue) == 1
        assert overdue[0]["id"] == 1
        assert overdue[0]["title"] == "Overdue Task"

    def test_load_tasks_invalid_json(self, sample_tasks):
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"{invalid json")
            temp_path = temp_file.name
    
        try:
            # Test that it handles the error and returns an empty list
            tasks = load_tasks(temp_path)
            assert tasks == []
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_set_task_recurrence(self, sample_tasks):
        task = {"id": 1, "title": "Recurring Task"}
    
        # Set valid recurrence
        updated_task = set_task_recurrence(task, "daily")
        assert updated_task["recurrence"] == "daily"
    
        # Set invalid recurrence
        updated_task = set_task_recurrence(task, "invalid_pattern")
        assert "recurrence" not in updated_task or updated_task["recurrence"] == "daily"

    def test_get_next_occurrence_date(self, sample_tasks):
        today_str = datetime.now().strftime("%Y-%m-%d")
    
        # Test daily recurrence
        task = {"id": 1, "title": "Daily Task", "recurrence": "daily", "due_date": today_str}
        next_date = get_next_occurrence_date(task)
        expected_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert next_date == expected_date
    
        # Test weekly recurrence
        task["recurrence"] = "weekly"
        next_date = get_next_occurrence_date(task)
        expected_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        assert next_date == expected_date
    
        # Test monthly recurrence (basic test)
        task["recurrence"] = "monthly"
        next_date = get_next_occurrence_date(task)
        assert next_date is not None
    
        # Test with missing due_date
        del task["due_date"]
        assert get_next_occurrence_date(task) is None
    
        # Test with invalid date format
        task["due_date"] = "invalid-date"
        assert get_next_occurrence_date(task) is None

    def test_generate_next_occurrence(self, sample_tasks):
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
    
        task = {
            "id": 1, 
            "title": "Recurring Task", 
            "recurrence": "daily", 
            "due_date": today_str,
            "completed": True,
            "subtasks": [
                {"id": 1, "title": "Subtask", "completed": True}
            ]
        }
    
        # Generate next occurrence
        next_task = generate_next_occurrence(task)
    
        # Verify ID is different
        assert next_task["id"] != task["id"]
    
        # Verify due date is updated
        expected_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        assert next_task["due_date"] == expected_date
    
        # Verify completed status is reset
        assert next_task["completed"] == False
    
        # Verify subtasks completion status is reset
        assert next_task["subtasks"][0]["completed"] == False
    
        # Test with no recurrence
        task_no_recurrence = {"id": 2, "title": "No Recurrence", "due_date": today_str}
        assert generate_next_occurrence(task_no_recurrence) is None