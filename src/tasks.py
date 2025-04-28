import json
import os
from datetime import datetime, timedelta

# File path for task storage
DEFAULT_TASKS_FILE = "tasks.json"

def load_tasks(file_path=DEFAULT_TASKS_FILE):
    """
    Load tasks from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file containing tasks
        
    Returns:
        list: List of task dictionaries, empty list if file doesn't exist
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # Handle corrupted JSON file
        print(f"Warning: {file_path} contains invalid JSON. Creating new tasks list.")
        return []

def save_tasks(tasks, file_path=DEFAULT_TASKS_FILE):
    """
    Save tasks to a JSON file.
    
    Args:
        tasks (list): List of task dictionaries
        file_path (str): Path to save the JSON file
    """
    with open(file_path, "w") as f:
        json.dump(tasks, f, indent=2)

def generate_unique_id(tasks):
    """
    Generate a unique ID for a new task.
    
    Args:
        tasks (list): List of existing task dictionaries
        
    Returns:
        int: A unique ID for a new task
    """
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def filter_tasks_by_priority(tasks, priority):
    """
    Filter tasks by priority level.
    
    Args:
        tasks (list): List of task dictionaries
        priority (str): Priority level to filter by (High, Medium, Low)
        
    Returns:
        list: Filtered list of tasks matching the priority
    """
    return [task for task in tasks if task.get("priority") == priority]

def filter_tasks_by_category(tasks, category):
    """
    Filter tasks by category.
    
    Args:
        tasks (list): List of task dictionaries
        category (str): Category to filter by
        
    Returns:
        list: Filtered list of tasks matching the category
    """
    return [task for task in tasks if task.get("category") == category]

def filter_tasks_by_completion(tasks, completed=True):
    """
    Filter tasks by completion status.
    
    Args:
        tasks (list): List of task dictionaries
        completed (bool): Completion status to filter by
        
    Returns:
        list: Filtered list of tasks matching the completion status
    """
    return [task for task in tasks if task.get("completed") == completed]

def search_tasks(tasks, query):
    """
    Search tasks by a text query in title and description.
    
    Args:
        tasks (list): List of task dictionaries
        query (str): Search query
        
    Returns:
        list: Filtered list of tasks matching the search query
    """
    query = query.lower()
    return [
        task for task in tasks 
        if query in task.get("title", "").lower() or 
           query in task.get("description", "").lower()
    ]

def get_overdue_tasks(tasks_list):
    """
    Get tasks that are past their due date and not completed.
    
    Args:
        tasks (list): List of task dictionaries
        
    Returns:
        list: List of overdue tasks
    """
    today = datetime.now().date()
    overdue_tasks = []
    
    for task in tasks_list:
        # Skip completed tasks
        if task.get("completed", False):
            continue
            
        # Skip tasks with no due date
        if "due_date" not in task:
            continue
            
        try:
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            if due_date < today:
                overdue_tasks.append(task)
        except (ValueError, TypeError):
            # Skip tasks with invalid due date format
            continue
            
    return overdue_tasks

def add_tags_to_task(task, tags):
    """Add tags to a task
    
    Args:
        task (dict): The task to update
        tags (list): List of string tags to add
        
    Returns:
        dict: The updated task with tags
    """
    if "tags" not in task:
        task["tags"] = []
    
    # Add new tags that don't already exist
    for tag in tags:
        if tag not in task["tags"]:
            task["tags"].append(tag)
    
    return task

def get_tasks_by_tag(tasks, tag):
    """Filter tasks by a specific tag
    
    Args:
        tasks (list): List of task dictionaries
        tag (str): Tag to filter by
        
    Returns:
        list: Tasks that have the specified tag
    """
    return [task for task in tasks if "tags" in task and tag in task["tags"]]

def add_subtask(task, subtask_data):
    """Add a subtask to a task
    
    Args:
        task (dict): The parent task
        subtask_data (dict): The subtask information
        
    Returns:
        dict: Updated task with the subtask added
    """
    if "subtasks" not in task:
        task["subtasks"] = []
    
    # Generate ID for subtask
    next_id = 1
    if task["subtasks"]:
        next_id = max(st.get("id", 0) for st in task["subtasks"]) + 1
    
    # Create complete subtask with ID
    subtask = {
        "id": next_id,
        "title": subtask_data.get("title", ""),
        "completed": subtask_data.get("completed", False)
    }
    
    task["subtasks"].append(subtask)
    return task

def complete_subtask(task, subtask_id):
    """Mark a subtask as complete
    
    Args:
        task (dict): The parent task
        subtask_id (int): ID of the subtask to complete
        
    Returns:
        dict: Updated task with the subtask completed
    """
    if "subtasks" not in task:
        return task
    
    for subtask in task["subtasks"]:
        if subtask.get("id") == subtask_id:
            subtask["completed"] = True
            break
    
    return task

def set_task_recurrence(task, recurrence_pattern):
    """Set recurrence pattern for a task
    
    Args:
        task (dict): The task to update
        recurrence_pattern (str): Pattern like 'daily', 'weekly', 'monthly'
        
    Returns:
        dict: The updated task with recurrence
    """
    valid_patterns = ["daily", "weekly", "monthly", "yearly"]
    if recurrence_pattern in valid_patterns:
        task["recurrence"] = recurrence_pattern
    return task

def get_next_occurrence_date(task):
    """Calculate the next occurrence date for a recurring task
    
    Args:
        task (dict): The recurring task
        
    Returns:
        str: The next occurrence date in YYYY-MM-DD format
    """
    if "recurrence" not in task or "due_date" not in task:
        return None
    
    try:
        current_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        
        if task["recurrence"] == "daily":
            next_date = current_date + timedelta(days=1)
        elif task["recurrence"] == "weekly":
            next_date = current_date + timedelta(days=7)
        elif task["recurrence"] == "monthly":
            # Move to the same day next month
            month = current_date.month % 12 + 1
            year = current_date.year + (1 if current_date.month == 12 else 0)
            day = min(current_date.day, 28)  # Avoid issues with month lengths
            next_date = current_date.replace(year=year, month=month, day=day)
        elif task["recurrence"] == "yearly":
            next_date = current_date.replace(year=current_date.year + 1)
        else:
            return None
            
        return next_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def generate_next_occurrence(task):
    """Generate the next occurrence of a recurring task
    
    Args:
        task (dict): The completed recurring task
        
    Returns:
        dict: A new task representing the next occurrence
    """
    if "recurrence" not in task or "due_date" not in task:
        return None
    
    next_date = get_next_occurrence_date(task)
    if not next_date:
        return None
    
    # Create a new task with a new ID but same details
    next_task = task.copy()
    next_task["id"] = generate_unique_id([task])  # You'll need your existing ID generator
    next_task["due_date"] = next_date
    next_task["completed"] = False
    
    # If there were subtasks, reset their completion status
    if "subtasks" in next_task:
        for subtask in next_task["subtasks"]:
            subtask["completed"] = False
    
    return next_task