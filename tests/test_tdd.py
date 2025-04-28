import unittest
from datetime import datetime
from src.tasks import (
    add_tags_to_task,
    get_tasks_by_tag,
    add_subtask,
    complete_subtask,
    set_task_recurrence,
    get_next_occurrence_date,
    generate_next_occurrence,
    load_tasks,
    save_tasks,
    generate_unique_id,
    filter_tasks_by_priority,
    filter_tasks_by_category,
    filter_tasks_by_completion,
    search_tasks,
    get_overdue_tasks,
)

class TestTasks(unittest.TestCase):

    def test_add_tags_to_task(self):
        task = {"id": 1, "title": "Test Task"}
        tags = ["urgent", "work"]
        updated_task = add_tags_to_task(task, tags)
        self.assertIn("tags", updated_task)
        self.assertEqual(updated_task["tags"], tags)

    def test_get_tasks_by_tag(self):
        tasks = [
            {"id": 1, "title": "Test Task 1", "tags": ["urgent"]},
            {"id": 2, "title": "Test Task 2", "tags": ["work"]},
        ]
        filtered_tasks = get_tasks_by_tag(tasks, "urgent")
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0]["title"], "Test Task 1")

    def test_add_subtask(self):
        task = {"id": 1, "title": "Test Task"}
        subtask_data = {"title": "Test Subtask", "completed": False}
        updated_task = add_subtask(task, subtask_data)
        self.assertIn("subtasks", updated_task)
        self.assertEqual(len(updated_task["subtasks"]), 1)

    def test_complete_subtask(self):
        task = {"id": 1, "title": "Test Task", "subtasks": [{"id": 1, "completed": False}]}
        updated_task = complete_subtask(task, 1)
        self.assertTrue(updated_task["subtasks"][0]["completed"])

    def test_set_task_recurrence(self):
        task = {"id": 1, "title": "Test Task"}
        updated_task = set_task_recurrence(task, "weekly")
        self.assertEqual(updated_task["recurrence"], "weekly")

    def test_get_next_occurrence_date(self):
        task = {"id": 1, "title": "Test Task", "due_date": "2025-04-25", "recurrence": "daily"}
        next_date = get_next_occurrence_date(task)
        self.assertEqual(next_date, "2025-04-26")

    def test_generate_next_occurrence(self):
        task = {"id": 1, "title": "Test Task", "due_date": "2025-04-25", "recurrence": "daily"}
        next_task = generate_next_occurrence(task)
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task["due_date"], "2025-04-26")

    def test_load_and_save_tasks(self):
        tasks = [{"id": 1, "title": "Test Task", "completed": False}]
        save_tasks(tasks)
        loaded_tasks = load_tasks()
        self.assertEqual(len(loaded_tasks), 1)
        self.assertEqual(loaded_tasks[0]["title"], "Test Task")

    def test_generate_unique_id(self):
        tasks = [{"id": 1}, {"id": 2}]
        new_id = generate_unique_id(tasks)
        self.assertEqual(new_id, 3)

    def test_filter_tasks_by_priority(self):
        tasks = [
            {"id": 1, "title": "Task 1", "priority": "High"},
            {"id": 2, "title": "Task 2", "priority": "Medium"},
        ]
        filtered_tasks = filter_tasks_by_priority(tasks, "High")
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0]["priority"], "High")

    def test_filter_tasks_by_category(self):
        tasks = [
            {"id": 1, "title": "Task 1", "category": "Work"},
            {"id": 2, "title": "Task 2", "category": "Personal"},
        ]
        filtered_tasks = filter_tasks_by_category(tasks, "Work")
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0]["category"], "Work")

    def test_filter_tasks_by_completion(self):
        tasks = [
            {"id": 1, "title": "Task 1", "completed": False},
            {"id": 2, "title": "Task 2", "completed": True},
        ]
        filtered_tasks = filter_tasks_by_completion(tasks, True)
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0]["completed"], True)

    def test_search_tasks(self):
        tasks = [
            {"id": 1, "title": "Task 1", "description": "Test description"},
            {"id": 2, "title": "Task 2", "description": "Another description"},
        ]
        filtered_tasks = search_tasks(tasks, "test")
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0]["title"], "Task 1")

    def test_get_overdue_tasks(self):
        today = datetime.now().date()
        tasks = [
            {"id": 1, "title": "Task 1", "due_date": str(today), "completed": False},
            {"id": 2, "title": "Task 2", "due_date": str(today), "completed": True},
        ]
        overdue_tasks = get_overdue_tasks(tasks)
        self.assertEqual(len(overdue_tasks), 0)

if __name__ == "__main__":
    unittest.main()
