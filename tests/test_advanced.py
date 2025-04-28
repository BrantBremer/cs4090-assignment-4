import pytest
from src.tasks import filter_tasks_by_priority

@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "Task 1", "priority": "High"},
        {"id": 2, "title": "Task 2", "priority": "Medium"},
        {"id": 3, "title": "Task 3", "priority": "Low"},
    ]

@pytest.mark.parametrize("priority,expected_count", [
    ("High", 1),
    ("Medium", 1),
    ("Low", 1),
    ("Critical", 0)  # Non-existent priority
])
def test_filter_by_priority_parameterized(sample_tasks, priority, expected_count):
    """Test filtering tasks by different priority levels"""
    filtered = filter_tasks_by_priority(sample_tasks, priority)
    assert len(filtered) == expected_count

def test_load_tasks_with_mock(mocker):
    """Test loading tasks with a mocked open function"""
    # Create a mock for the open function
    mock_open = mocker.patch('builtins.open', mocker.mock_open(
        read_data='[{"id": 999, "title": "Mocked Task"}]'
    ))
    
    # Call the function that uses open()
    from src.tasks import load_tasks
    tasks = load_tasks('fake_path.json')
    
    # Verify the results
    assert len(tasks) == 1
    assert tasks[0]['id'] == 999
    assert tasks[0]['title'] == "Mocked Task"
    
    # Verify open was called with the right parameters
    mock_open.assert_called_once_with('fake_path.json', 'r')