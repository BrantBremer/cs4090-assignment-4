Feature: Task Management
  As a user of the To-Do application
  I want to manage my tasks effectively
  So that I can stay organized and productive

  Scenario: Add a new task
    Given the task list is empty
    When I add a task with title "Buy groceries" and priority "High"
    Then the task list should contain 1 task
    And the task should have title "Buy groceries"
    And the task should have priority "High"
    And the task should not be marked as completed

  Scenario: Filter tasks by priority
    Given I have tasks with different priorities
      | title       | priority |
      | High task   | High     |
      | Medium task | Medium   |
      | Low task    | Low      |
    When I filter tasks by priority "High"
    Then I should see 1 task in the filtered list
    And the filtered list should contain a task with title "High task"

  Scenario: Mark task as completed
    Given I have a task with title "Complete assignment"
    When I mark the task as completed
    Then the task should be marked as completed

  Scenario: Search for tasks
    Given I have the following tasks
      | title          | description       |
      | Buy milk       | From the store    |
      | Pay bills      | Electric and gas  |
      | Call mom       | For her birthday  |
    When I search for "milk"
    Then I should see 1 task in the results
    And the results should contain a task with title "Buy milk"

  Scenario: Add tags to a task
    Given I have a task with title "Project planning"
    When I add tags "work,urgent,meeting" to the task
    Then the task should have 3 tags
    And the task tags should include "urgent"

