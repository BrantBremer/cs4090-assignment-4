import json
import os
import tempfile
from behave import given, when, then
import sys

# Add the parent directory to path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tasks import (
    load_tasks, save_tasks, filter_tasks_by_priority, 
    search_tasks, add_tags_to_task
)

@given('the task list is empty')
def step_impl(context):
    context.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    context.tasks_file = context.temp_file.name
    context.temp_file.close()
    
    # Create empty tasks list
    save_tasks([], context.tasks_file)
    context.tasks = load_tasks(context.tasks_file)
    assert len(context.tasks) == 0

@when('I add a task with title "{title}" and priority "{priority}"')
def step_impl(context, title, priority):
    new_task = {
        "id": 1,
        "title": title,
        "priority": priority,
        "completed": False
    }
    context.tasks.append(new_task)
    save_tasks(context.tasks, context.tasks_file)

@then('the task list should contain {count:d} task')
def step_impl(context, count):
    context.tasks = load_tasks(context.tasks_file)
    assert len(context.tasks) == count

@then('the task should have title "{title}"')
def step_impl(context, title):
    assert context.tasks[0]["title"] == title

@then('the task should have priority "{priority}"')
def step_impl(context, priority):
    assert context.tasks[0]["priority"] == priority

@then('the task should not be marked as completed')
def step_impl(context):
    assert context.tasks[0]["completed"] == False

@given('I have tasks with different priorities')
def step_impl(context):
    context.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    context.tasks_file = context.temp_file.name
    context.temp_file.close()
    
    tasks = []
    for row in context.table:
        tasks.append({
            "id": len(tasks) + 1,
            "title": row['title'],
            "priority": row['priority'],
            "completed": False
        })
    
    save_tasks(tasks, context.tasks_file)
    context.tasks = tasks

@when('I filter tasks by priority "{priority}"')
def step_impl(context, priority):
    context.filtered_tasks = filter_tasks_by_priority(context.tasks, priority)

@then('I should see {count:d} task in the filtered list')
def step_impl(context, count):
    assert len(context.filtered_tasks) == count

@then('the filtered list should contain a task with title "{title}"')
def step_impl(context, title):
    titles = [task["title"] for task in context.filtered_tasks]
    assert title in titles

@given('I have a task with title "{title}"')
def step_impl(context, title):
    context.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    context.tasks_file = context.temp_file.name
    context.temp_file.close()
    
    task = {
        "id": 1,
        "title": title,
        "completed": False
    }
    context.tasks = [task]
    save_tasks(context.tasks, context.tasks_file)

@when('I mark the task as completed')
def step_impl(context):
    context.tasks[0]["completed"] = True
    save_tasks(context.tasks, context.tasks_file)

@then('the task should be marked as completed')
def step_impl(context):
    tasks = load_tasks(context.tasks_file)
    assert tasks[0]["completed"] == True

@given('I have the following tasks')
def step_impl(context):
    context.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    context.tasks_file = context.temp_file.name
    context.temp_file.close()
    
    tasks = []
    for row in context.table:
        tasks.append({
            "id": len(tasks) + 1,
            "title": row['title'],
            "description": row['description'],
            "completed": False
        })
    
    save_tasks(tasks, context.tasks_file)
    context.tasks = tasks

@when('I search for "{query}"')
def step_impl(context, query):
    context.search_results = search_tasks(context.tasks, query)

@then('I should see {count:d} task in the results')
def step_impl(context, count):
    assert len(context.search_results) == count

@then('the results should contain a task with title "{title}"')
def step_impl(context, title):
    titles = [task["title"] for task in context.search_results]
    assert title in titles

@when('I add tags "{tags}" to the task')
def step_impl(context, tags):
    tag_list = tags.split(',')
    context.task = context.tasks[0]
    context.updated_task = add_tags_to_task(context.task, tag_list)

@then('the task should have {count:d} tags')
def step_impl(context, count):
    assert len(context.updated_task["tags"]) == count

@then('the task tags should include "{tag}"')
def step_impl(context, tag):
    assert tag in context.updated_task["tags"]

# Clean up after each scenario
def after_scenario(context, scenario):
    if hasattr(context, 'tasks_file') and os.path.exists(context.tasks_file):
        os.unlink(context.tasks_file)