import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import os
import sys
from tasks import (load_tasks, save_tasks, filter_tasks_by_priority, 
                   filter_tasks_by_category, generate_unique_id, 
                   add_tags_to_task, get_tasks_by_tag,
                   add_subtask, complete_subtask,
                   set_task_recurrence, get_next_occurrence_date,
                   generate_next_occurrence, get_overdue_tasks)

def main():
    st.title("To-Do Application")
    
    # Load existing tasks
    tasks = load_tasks()
    
    # Sidebar for adding new tasks
    st.sidebar.header("Add New Task")
    
    # Task creation form with new features
    with st.sidebar.form("new_task_form"):
        task_title = st.text_input("Task Title")
        task_description = st.text_area("Description")
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
        task_due_date = st.date_input("Due Date")
        
        # Add tags input
        task_tags = st.text_input("Tags (comma separated)")
        
        # Add recurrence option
        enable_recurrence = st.checkbox("Enable Recurrence")
        recurrence_pattern = None
        if enable_recurrence:
            recurrence_pattern = st.selectbox(
                "Recurrence Pattern", 
                ["daily", "weekly", "monthly", "yearly"]
            )
        
        submit_button = st.form_submit_button("Add Task")
        
        if submit_button and task_title:
            new_task = {
                "id": generate_unique_id(tasks),
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add tags if provided
            if task_tags:
                tags_list = [tag.strip() for tag in task_tags.split(",") if tag.strip()]
                if tags_list:
                    new_task = add_tags_to_task(new_task, tags_list)
            
            # Add recurrence if enabled
            if enable_recurrence and recurrence_pattern:
                new_task = set_task_recurrence(new_task, recurrence_pattern)
                
            tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")
    
    # Main area to display tasks
    st.header("Your Tasks")
    
    # Filter options with new tag filter
    col1, col2, col3 = st.columns(3)
    with col1:
        # Get unique categories from tasks
        categories = ["All"]
        if tasks:
            categories += list(set([task["category"] for task in tasks if "category" in task]))
        filter_category = st.selectbox("Filter by Category", categories)
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    with col3:
        # Get unique tags
        all_tags = []
        for task in tasks:
            if "tags" in task:
                all_tags.extend(task["tags"])
        unique_tags = ["All"] + list(set(all_tags))
        filter_tag = st.selectbox("Filter by Tag", unique_tags)
    
    show_completed = st.checkbox("Show Completed Tasks")
    show_overdue = st.checkbox("Show Only Overdue Tasks")
    
    # Apply filters
    filtered_tasks = tasks.copy()
    
    # Category filter
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    
    # Priority filter
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    
    # Tag filter
    if filter_tag != "All":
        filtered_tasks = get_tasks_by_tag(filtered_tasks, filter_tag)
    
    # Completed filter
    if not show_completed:
        filtered_tasks = [task for task in filtered_tasks if not task.get("completed", False)]
    
    # Overdue filter
    if show_overdue:
        filtered_tasks = get_overdue_tasks(filtered_tasks)
    
    # Display tasks
    if not filtered_tasks:
        st.info("No tasks found. Add a task to get started!")
    
    for task in filtered_tasks:
        # Create an expander for each task to show details
        with st.expander(f"{'✅ ' if task.get('completed', False) else '📝 '}{task['title']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if task.get("completed", False):
                    st.markdown(f"~~**{task['title']}**~~")
                else:
                    st.markdown(f"**{task['title']}**")
                st.write(task.get("description", ""))
                st.caption(f"Due: {task.get('due_date', 'None')} | Priority: {task.get('priority', 'None')} | Category: {task.get('category', 'None')}")
                
                # Display recurrence info if present
                if "recurrence" in task:
                    st.caption(f"Recurrence: {task['recurrence']}")
                
                # Display tags if present
                if "tags" in task and task["tags"]:
                    st.write("Tags: " + ", ".join(task["tags"]))
            
            with col2:
                # Task action buttons
                if st.button("Complete" if not task.get("completed", False) else "Undo", key=f"complete_{task['id']}"):
                    for t in tasks:
                        if t["id"] == task["id"]:
                            was_completed = t.get("completed", False)
                            t["completed"] = not was_completed
                            
                            # If task is completed and has recurrence, create next occurrence
                            if not was_completed and "recurrence" in t:
                                next_task = generate_next_occurrence(t)
                                if next_task:
                                    tasks.append(next_task)
                            
                            save_tasks(tasks)
                            st.rerun()
                
                if st.button("Delete", key=f"delete_{task['id']}"):
                    tasks = [t for t in tasks if t["id"] != task["id"]]
                    save_tasks(tasks)
                    st.rerun()
                
                # Add tag option
                if st.button("Add Tag", key=f"add_tag_{task['id']}"):
                    st.session_state[f"show_tag_input_{task['id']}"] = True
                
                # Edit tags if shown
                if st.session_state.get(f"show_tag_input_{task['id']}", False):
                    new_tag = st.text_input("New Tag", key=f"tag_input_{task['id']}")
                    if st.button("Save Tag", key=f"save_tag_{task['id']}"):
                        for t in tasks:
                            if t["id"] == task["id"]:
                                t = add_tags_to_task(t, [new_tag])
                                save_tasks(tasks)
                                st.session_state[f"show_tag_input_{task['id']}"] = False
                                st.rerun()
            
            # Subtasks section
            st.write("---")
            st.subheader("Subtasks")
            
            # Display existing subtasks
            if "subtasks" in task and task["subtasks"]:
                for subtask in task["subtasks"]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if subtask.get("completed", False):
                            st.markdown(f"~~{subtask['title']}~~")
                        else:
                            st.write(subtask['title'])
                    with col2:
                        if not subtask.get("completed", False):
                            if st.button("Complete", key=f"complete_subtask_{task['id']}_{subtask['id']}"):
                                for t in tasks:
                                    if t["id"] == task["id"]:
                                        t = complete_subtask(t, subtask["id"])
                                        save_tasks(tasks)
                                        st.rerun()
            else:
                st.write("No subtasks yet")
            
            # Add subtask option
            if st.button("Add Subtask", key=f"add_subtask_{task['id']}"):
                st.session_state[f"show_subtask_input_{task['id']}"] = True
            
            # Show subtask input if requested
            if st.session_state.get(f"show_subtask_input_{task['id']}", False):
                with st.form(key=f"subtask_form_{task['id']}"):
                    subtask_title = st.text_input("Subtask Title", key=f"subtask_title_{task['id']}")
                    submit_subtask = st.form_submit_button("Add")
                    
                    if submit_subtask and subtask_title:
                        for t in tasks:
                            if t["id"] == task["id"]:
                                t = add_subtask(t, {"title": subtask_title})
                                save_tasks(tasks)
                                st.session_state[f"show_subtask_input_{task['id']}"] = False
                                st.rerun()
    
    # Add a separator before testing section
    st.markdown("---")
    
    # ... [rest of the code with testing sections remains unchanged]
    
    # Testing Suite section - Adding directly to main page instead of in a tab
    st.header("Testing Suite")
    
    # Unit Testing Section
    st.subheader("Unit Testing")
    st.markdown("""
    Unit tests verify the core functionality of the application components in isolation.
    Click the button below to run the basic unit tests.
    """)
    
    if st.button("Run Unit Tests"):
        run_unit_tests()
    
    # Coverage Testing Section
    st.subheader("Coverage Testing")
    st.markdown("""
    Coverage testing measures how much of the codebase is being tested.
    Click the button below to run coverage analysis.
    """)

    if st.button("Run Coverage Tests"):
        stdout, return_code = run_coverage_tests()
        if return_code == 0:
            st.success("Coverage tests completed successfully!")
        else:
            st.error("Coverage tests encountered issues.")
        st.code(stdout, language="text")

    # Parameterized Testing Section
    st.subheader("Parameterized Testing")
    st.markdown("""
    Parameterized testing runs the same test with multiple different inputs.
    Click the button below to run parameterized tests.
    """)

    if st.button("Run Parameterized Tests"):
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_advanced.py::test_filter_by_priority_parameterized", "-v"],
            capture_output=True,
            text=True
        )
        st.code(result.stdout, language="text")

    # Mock Testing Section
    st.subheader("Mock Testing")
    st.markdown("""
    Mock testing replaces real components with simulated ones for isolated testing.
    Click the button below to run mock tests.
    """)

    if st.button("Run Mock Tests"):
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_advanced.py::test_load_tasks_with_mock", "-v"],
            capture_output=True,
            text=True
        )
        st.code(result.stdout, language="text")

    # HTML Report Section
    st.subheader("HTML Test Report")
    st.markdown("""
    Generate a comprehensive HTML report of all test results.
    Click the button below to create an HTML report.
    """)

    if st.button("Generate HTML Report"):
        stdout, report_path, return_code = run_html_report()
        if return_code == 0:
            st.success(f"HTML report generated successfully!")
            st.markdown(f"Report saved to: `{report_path}`")
        else:
            st.error("Error generating HTML report.")
        st.code(stdout, language="text")

    # TTD Testing Section
    st.subheader("Test-Driven Development (TDD)")
    st.markdown("""
    TDD tests demonstrate the process of developing features by writing tests first.
    Click the button below to run TDD tests.
    """)

    if st.button("Run TDD Tests"):
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_tdd.py", "-v"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            st.success("✅ All TDD tests passed!")
        else:
            st.error("❌ Some TDD tests failed")

        st.code(result.stdout, language="text")
    
    # BDD Testing Section
    st.subheader("Behavior-Driven Development (BDD)")
    st.markdown("""
    BDD tests focus on the behavior of the application from the user's perspective.
    These tests are written in a natural language format that stakeholders can understand.
    Click the button below to run BDD tests.
    """)

    if st.button("Run BDD Tests"):
        with st.spinner("Running BDD tests..."):
            result = subprocess.run(
                ["behave", "tests/features/"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.success("✅ All BDD tests passed!")
            else:
                st.error("❌ Some BDD tests failed")
    
            st.code(result.stdout, language="text")

    # Property-Based Testing Section
    st.subheader("Property-Based Testing")
    st.markdown("""
    Property-based tests verify that certain properties of the code hold true for a wide range of inputs.
    They generate random test data to find edge cases automatically.
    Click the button below to run property-based tests using Hypothesis.
    """)

    if st.button("Run Property-Based Tests"):
        with st.spinner("Running property-based tests..."):
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/test_property.py", "-v"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.success("✅ All property-based tests passed!")
            else:
                st.error("❌ Some property-based tests failed")
    
            st.code(result.stdout, language="text")

def run_unit_tests():
    """Run unit tests and display results in the Streamlit UI"""
    with st.spinner("Running unit tests..."):
        # Create results directory if it doesn't exist
        os.makedirs("test_results", exist_ok=True)
        
        # Generate timestamp for unique report name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Determine the root directory (where src/ and tests/ are located)
        current_dir = os.path.dirname(os.path.abspath(__file__))  # This is src/
        root_dir = os.path.dirname(current_dir)  # Go up one level to the project root

        # Run the tests with pytest
        result = subprocess.run(
            [
                "python3", "-m", "pytest", 
                os.path.join(root_dir, "tests", "test_basic.py"),  # Full path to test file
                "-v", 
                "--cov=src.tasks",
                f"--cov-report=html:test_results/coverage_{timestamp}",
                "--no-header"
            ], 
            capture_output=True, 
            text=True,
            cwd=root_dir
        )
        
        # Display results based on return code
        if result.returncode == 0:
            st.success("✅ All unit tests passed!")
        else:
            st.error("❌ Some tests failed")
        
        # Parse and display test results
        test_results = parse_test_output(result.stdout)
        if test_results:
            display_test_results(test_results)
        
        # Display coverage information
        display_coverage_info(result.stdout, timestamp)
        
        # Show full output in expandable section
        with st.expander("View Full Test Output"):
            st.code(result.stdout, language="text")
            
            if result.stderr:
                st.subheader("Errors")
                st.code(result.stderr, language="text")

def run_coverage_tests():
    """Run tests with coverage reporting and display results"""
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "--cov=src.tasks", "--cov-report=term"],
        capture_output=True,
        text=True
    )
    return result.stdout, result.returncode

def run_html_report():
    """Generate HTML report for tests"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = f"test_results/report_{timestamp}.html"
    
    # Ensure directory exists
    os.makedirs("test_results", exist_ok=True)
    
    result = subprocess.run(
        ["python3", "-m", "pytest", "tests/", f"--html={report_path}", "--self-contained-html"],
        capture_output=True,
        text=True
    )
    
    return result.stdout, report_path, result.returncode

def parse_test_output(output):
    """Parse pytest output to extract test results"""
    lines = output.strip().split('\n')
    test_data = []
    
    for line in lines:
        if " PASSED " in line or " FAILED " in line or " SKIPPED " in line or " ERROR " in line:
            parts = line.strip().split(" ")
            test_name = parts[0]
            
            if " PASSED " in line:
                status = "PASSED"
            elif " FAILED " in line:
                status = "FAILED"
            elif " SKIPPED " in line:
                status = "SKIPPED"
            else:
                status = "ERROR"
            
            test_data.append({
                "Test": test_name,
                "Status": status
            })
    
    return test_data

def display_test_results(test_results):
    """Display test results in a formatted table"""
    st.subheader("Test Results")
    
    # Convert to DataFrame for display
    df = pd.DataFrame(test_results)
    
    # Apply styling
    def highlight_status(val):
        color = ""
        if val == "PASSED":
            color = "green"
        elif val == "FAILED":
            color = "red"
        elif val == "SKIPPED":
            color = "orange"
        else:
            color = "red"
        return f'background-color: {color}; color: white'
    
    # Show styled dataframe
    st.dataframe(df.style.applymap(highlight_status, subset=['Status']))
    
    # Summary statistics
    total = len(test_results)
    passed = sum(1 for r in test_results if r["Status"] == "PASSED")
    failed = sum(1 for r in test_results if r["Status"] == "FAILED")
    skipped = sum(1 for r in test_results if r["Status"] == "SKIPPED")
    
    st.write(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

def display_coverage_info(output, timestamp):
    """Extract and display coverage information"""
    if "TOTAL" in output and "%" in output:
        st.subheader("Coverage Summary")
        
        # Extract coverage information
        lines = output.strip().split('\n')
        coverage_lines = [line for line in lines if "%" in line]
        
        if coverage_lines:
            # Create a table for coverage data
            coverage_data = []
            headers = ["Module", "Statements", "Miss", "Cover", "Missing"]
            
            for line in coverage_lines:
                parts = [part.strip() for part in line.split() if part.strip()]
                if len(parts) >= 4:  # At least module, statements, miss, cover
                    coverage_data.append({
                        "Module": parts[0],
                        "Statements": parts[1],
                        "Miss": parts[2],
                        "Cover": parts[3],
                        "Missing": " ".join(parts[4:]) if len(parts) > 4 else ""
                    })
            
            if coverage_data:
                df = pd.DataFrame(coverage_data)
                st.dataframe(df)
        
        # Link to HTML report
        report_path = f"test_results/coverage_{timestamp}"
        if os.path.exists(report_path):
            st.markdown(f"""
            A detailed HTML coverage report has been generated. 
            You can view it by opening: 
            ```
            {report_path}/index.html
            ```
            """)

if __name__ == "__main__":
    main()