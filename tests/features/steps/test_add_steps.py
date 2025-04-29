import os
import tempfile
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import sys

# Add the parent directory to path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.tasks import (
    load_tasks, save_tasks, filter_tasks_by_priority, 
    search_tasks, add_tags_to_task
)

# Load scenarios from feature file
scenarios('../add_task.feature')

# Fixture for temporary task file
@pytest.fixture
def task_file():
    """Create a temporary file for tasks."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    file_path = temp_file.name
    temp_file.close()
    
    # Create empty tasks list
    save_tasks([], file_path)
    
    yield file_path
    
    # Clean up
    if os.path.exists(file_path):
        os.unlink(file_path)

# --- Given Steps ---

@given("the task list is empty", target_fixture="empty_tasks_file")
def empty_task_list(task_file):
    tasks = load_tasks(task_file)
    assert len(tasks) == 0
    return {"file": task_file, "tasks": []}

@given("I have tasks with different priorities", target_fixture="priority_tasks")
def task_list_with_priorities(task_file):
    tasks = [
        {"id": 1, "title": "High task", "priority": "High", "completed": False},
        {"id": 2, "title": "Medium task", "priority": "Medium", "completed": False},
        {"id": 3, "title": "Low task", "priority": "Low", "completed": False}
    ]
    save_tasks(tasks, task_file)
    return {"file": task_file, "tasks": tasks}

@given(parsers.parse("I have a task with title \"{title}\""), target_fixture="single_task")
def task_with_title(task_file, title):
    task = {
        "id": 1,
        "title": title,
        "completed": False
    }
    save_tasks([task], task_file)
    return {"file": task_file, "tasks": [task]}

@given("I have the following tasks", target_fixture="multiple_tasks")
def setup_multiple_tasks(task_file):
    tasks = [
        {"id": 1, "title": "Buy milk", "description": "From the store", "completed": False},
        {"id": 2, "title": "Pay bills", "description": "Electric and gas", "completed": False},
        {"id": 3, "title": "Call mom", "description": "For her birthday", "completed": False}
    ]
    save_tasks(tasks, task_file)
    return {"file": task_file, "tasks": tasks}

# --- When Steps ---

@when(parsers.parse("I add a task with title \"{title}\" and priority \"{priority}\""))
def add_task(empty_tasks_file, title, priority):
    new_task = {
        "id": 1,
        "title": title,
        "priority": priority,
        "completed": False
    }
    empty_tasks_file["tasks"].append(new_task)
    save_tasks(empty_tasks_file["tasks"], empty_tasks_file["file"])

@when(parsers.parse("I filter tasks by priority \"{priority}\""), target_fixture="filtered_results")
def filter_by_priority(priority_tasks, priority):
    return filter_tasks_by_priority(priority_tasks["tasks"], priority)

@when("I mark the task as completed")
def mark_task_completed(single_task):
    single_task["tasks"][0]["completed"] = True
    save_tasks(single_task["tasks"], single_task["file"])

@when(parsers.parse("I search for \"{query}\""), target_fixture="search_results")
def search_for_task(multiple_tasks, query):
    return search_tasks(multiple_tasks["tasks"], query)

@when(parsers.parse("I add tags \"{tags}\" to the task"), target_fixture="tagged_task")
def add_tags(single_task, tags):
    tag_list = tags.split(',')
    updated_task = add_tags_to_task(single_task["tasks"][0], tag_list)
    
    # Update the task in the list and save
    single_task["tasks"][0] = updated_task
    save_tasks(single_task["tasks"], single_task["file"])
    
    return updated_task

# --- Then Steps ---

@then(parsers.parse("the task list should contain {count:d} task"))
def task_list_count(empty_tasks_file, count):
    tasks = load_tasks(empty_tasks_file["file"])
    assert len(tasks) == count

@then(parsers.parse("the task should have title \"{title}\""))
def task_has_title(empty_tasks_file, title):
    tasks = load_tasks(empty_tasks_file["file"])
    assert tasks[0]["title"] == title

@then(parsers.parse("the task should have priority \"{priority}\""))
def task_has_priority(empty_tasks_file, priority):
    tasks = load_tasks(empty_tasks_file["file"])
    assert tasks[0]["priority"] == priority

@then("the task should not be marked as completed")
def task_not_completed(empty_tasks_file):
    tasks = load_tasks(empty_tasks_file["file"])
    assert tasks[0]["completed"] == False

@then(parsers.parse("I should see {count:d} task in the filtered list"))
def filtered_list_count(filtered_results, count):
    assert len(filtered_results) == count

@then(parsers.parse("the filtered list should contain a task with title \"{title}\""))
def filtered_list_contains_title(filtered_results, title):
    titles = [task["title"] for task in filtered_results]
    assert title in titles

@then("the task should be marked as completed")
def task_is_completed(single_task):
    tasks = load_tasks(single_task["file"])
    assert tasks[0]["completed"] == True

@then(parsers.parse("I should see {count:d} task in the results"))
def search_results_count(search_results, count):
    assert len(search_results) == count

@then(parsers.parse("the results should contain a task with title \"{title}\""))
def search_results_contain_title(search_results, title):
    titles = [task["title"] for task in search_results]
    assert title in titles

@then(parsers.parse("the task should have {count:d} tags"))
def task_has_tags_count(tagged_task, count):
    assert len(tagged_task["tags"]) == count

@then(parsers.parse("the task tags should include \"{tag}\""))
def task_tags_include(tagged_task, tag):
    assert tag in tagged_task["tags"]