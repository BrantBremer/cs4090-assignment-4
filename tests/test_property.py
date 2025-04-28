# tests/test_property.py
import sys
import os
import json
from datetime import datetime, timedelta
import tempfile
import pytest
from hypothesis import given, strategies as st

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tasks import (
    filter_tasks_by_priority, filter_tasks_by_category, 
    search_tasks, add_tags_to_task, generate_unique_id,
    get_overdue_tasks
)

# Define strategies for task generation
task_priorities = st.sampled_from(["Low", "Medium", "High"])
task_categories = st.sampled_from(["Work", "Personal", "School", "Other"])
task_titles = st.text(min_size=1, max_size=100)
task_descriptions = st.text(max_size=200)
task_ids = st.integers(min_value=1, max_value=10000)
task_completed = st.booleans()

# Strategy for generating a single task
task_strategy = st.builds(
    lambda id, title, desc, priority, category, completed: {
        "id": id,
        "title": title,
        "description": desc,
        "priority": priority,
        "category": category,
        "completed": completed
    },
    id=task_ids,
    title=task_titles,
    desc=task_descriptions,
    priority=task_priorities,
    category=task_categories,
    completed=task_completed
)

# Strategy for generating a list of tasks
tasks_strategy = st.lists(task_strategy, min_size=0, max_size=20)

@given(tasks=tasks_strategy, priority=task_priorities)
def test_property_filter_by_priority(tasks, priority):
    """Test that filtered tasks by priority only contain tasks with that priority"""
    filtered = filter_tasks_by_priority(tasks, priority)
    
    # All filtered tasks should have the specified priority
    for task in filtered:
        assert task["priority"] == priority
    
    # All tasks with the specified priority should be in the filtered list
    for task in tasks:
        if task.get("priority") == priority:
            assert task in filtered

@given(tasks=tasks_strategy, category=task_categories)
def test_property_filter_by_category(tasks, category):
    """Test that filtered tasks by category only contain tasks with that category"""
    filtered = filter_tasks_by_category(tasks, category)
    
    # All filtered tasks should have the specified category
    for task in filtered:
        assert task["category"] == category
    
    # All tasks with the specified category should be in the filtered list
    for task in tasks:
        if task.get("category") == category:
            assert task in filtered

@given(tasks=tasks_strategy)
def test_property_unique_id_is_greater_than_all_existing(tasks):
    """Test that generated unique ID is greater than all existing IDs"""
    if not tasks:
        # Edge case: empty list
        assert generate_unique_id(tasks) == 1
    else:
        unique_id = generate_unique_id(tasks)
        assert unique_id > max(task["id"] for task in tasks)

@given(tasks=tasks_strategy, completed=task_completed)
def test_property_filter_by_completion(tasks, completed):
    """Test that filtered tasks by completion match the completion criteria"""
    from src.tasks import filter_tasks_by_completion
    
    filtered = filter_tasks_by_completion(tasks, completed)
    
    # All filtered tasks should have the specified completion status
    for task in filtered:
        assert task["completed"] == completed
    
    # All tasks with the specified completion status should be in the filtered list
    for task in tasks:
        if task.get("completed") == completed:
            assert task in filtered

@given(task=task_strategy, tags=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5))
def test_property_add_tags(task, tags):
    """Test that adding tags works correctly with various inputs"""
    # Make a copy to avoid modifying the original
    task_copy = task.copy()
    
    # Add tags
    result = add_tags_to_task(task_copy, tags)
    
    # Ensure all tags are added
    for tag in tags:
        assert tag in result["tags"]
    
    # Ensure no duplicates
    assert len(result["tags"]) == len(set(result["tags"]))