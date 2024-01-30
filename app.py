import streamlit as st
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error
from datetime import datetime

DATABASE_FILE = "tasks.db"

class TaskModel(BaseModel):
    name: str
    description: str = ""
    is_done: bool = False
    created_at: datetime = datetime.now()
    created_by: str = ""
    category: str = ""

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except Error as e:
        st.error(f"Error: {e}")
    return conn

def create_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        is_done INTEGER DEFAULT 0,
        created_at DATETIME,
        created_by TEXT,
        category TEXT
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
    except Error as e:
        st.error(f"Error: {e}")

def save_task_to_db(conn, task_data):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (name, description, is_done, created_at, created_by, category) VALUES (?, ?, ?, ?, ?, ?)",
            (task_data["name"], task_data["description"], task_data["is_done"], task_data["created_at"],
             task_data["created_by"], task_data["category"]),
        )
        conn.commit()
        st.success("Task saved successfully!")
    except Error as e:
        st.error(f"Error: {e}")

def list_tasks(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        for row in rows:
            st.write(f"Task ID: {row[0]}, Name: {row[1]}, Description: {row[2]}, Is Done: {row[3]}")
    except Error as e:
        st.error(f"Error: {e}")

def update_task_status(conn, task_id, is_done):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET is_done = ? WHERE id = ?", (is_done, task_id))
        conn.commit()
        st.success("Task status updated successfully!")
    except Error as e:
        st.error(f"Error: {e}")

def delete_task(conn, task_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        st.success("Task deleted successfully!")
    except Error as e:
        st.error(f"Error: {e}")

def main():
    st.title("Task Management App")

    conn = create_connection()
    if conn is not None:
        create_table(conn)

    # Create Task Form
    st.header("Create New Task")
    task_name = st.text_input("Task Name", "")
    task_description = st.text_area("Task Description", "")
    is_done = st.checkbox("Is Done?")
    created_by = st.text_input("Created By", "")
    category = st.selectbox("Category", ["", "School", "Work", "Personal"])

    if st.button("Submit Task"):
        task_data = {
            "name": task_name,
            "description": task_description,
            "is_done": is_done,
            "created_by": created_by,
            "category": category
        }
        save_task_to_db(conn, task_data)

    # List Tasks
    st.header("Task List")
    list_tasks(conn)

    # Update Task status
    if st.button("Update Task Status"):
        task_id = st.number_input("Enter Task ID to update status", min_value=1)
        is_done = st.checkbox("Mark as Done")
        update_task_status(conn, task_id, is_done)

    # Bonus: Delete Task
    if st.button("Delete Task"):
        task_id = st.number_input("Enter Task ID to delete", min_value=1)
        delete_task(conn, task_id)

if __name__ == "__main__":
    main()
