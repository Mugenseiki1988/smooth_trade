import subprocess
import os
import time
import pyodbc

def run_command(command, description=""):
    try:
        print(f"\n[INFO] {description}")
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed.")
        print(e.stderr)
        return None

def check_container_health(container_name):
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{json .State.Health.Status}}", container_name],
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout.strip().replace('"', '')
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to check health status for container '{container_name}'.")
        print(e.stderr)
        return None

def restart_container(container_name):
    print(f"[INFO] Restarting container: {container_name}")
    run_command(["docker", "restart", container_name], f"Restarting container {container_name}")

def check_logs_for_errors(container_name, error_keywords):
    print(f"[INFO] Checking logs for container: {container_name}")
    logs = run_command(["docker", "logs", container_name], f"Retrieving logs for {container_name}")
    if logs:
        for keyword in error_keywords:
            if keyword in logs:
                print(f"[ERROR] Found '{keyword}' in logs of {container_name}.")
                return True
    print(f"[INFO] No critical errors found in logs of {container_name}.")
    return False

def configure_sql_server_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=master;"
        "UID=sa;"
        "PWD=Mugenseiki1988#;"
    )
    try:
        print("[INFO] Attempting to configure SQL Server...")
        connection = pyodbc.connect(conn_str)
        print("[INFO] Connected to SQL Server successfully!")

        cursor = connection.cursor()

        database_name = "airflow_db"
        user_name = "airflow_user"
        user_password = "AirflowUserPassword#123"

        cursor.execute(f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database_name}') CREATE DATABASE {database_name};
        IF NOT EXISTS (SELECT name FROM sys.sql_logins WHERE name = '{user_name}')
        BEGIN
            CREATE LOGIN {user_name} WITH PASSWORD = '{user_password}';
        END;
        USE {database_name};
        IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = '{user_name}')
        BEGIN
            CREATE USER {user_name} FOR LOGIN {user_name};
        END;
        ALTER ROLE db_owner ADD MEMBER {user_name};
        """)

        print(f"[INFO] Database '{database_name}' and user '{user_name}' configured successfully.")

        connection.commit()
        connection.close()
    except pyodbc.Error as e:
        print(f"[ERROR] SQL Server configuration failed: {e}")

def fix_mssql_container():
    container_name = "airflow_tutorial-mssql-1"

    # Step 1: Check if container is running
    print(f"[INFO] Checking if container {container_name} is running...")
    running_containers = run_command(["docker", "ps", "--format", "{{.Names}}"], "Listing running containers")

    if container_name not in running_containers:
        print(f"[ERROR] Container {container_name} is not running. Starting it now...")
        run_command(["docker-compose", "up", "-d", container_name], f"Starting container {container_name}")
        time.sleep(5)  # Allow the container time to start

    # Step 2: Check container health
    print(f"[INFO] Checking health status of {container_name}...")
    health_status = check_container_health(container_name)
    print(f"[INFO] Health status: {health_status}")

    if health_status == "healthy":
        print(f"[INFO] Container {container_name} is healthy.")
        return

    if health_status == "unhealthy":
        print(f"[WARNING] Container {container_name} is unhealthy. Attempting to diagnose...")

    # Step 3: Check logs for common errors
    error_keywords = ["Failed to load LSA", "Permission denied", "fatal error", "AppLoader"]
    has_errors = check_logs_for_errors(container_name, error_keywords)

    if has_errors:
        print(f"[INFO] Attempting to resolve issues in container {container_name}...")

        # Step 4: Restart the container
        restart_container(container_name)
        time.sleep(5)  # Allow the container to restart

        # Step 5: Check health again
        health_status = check_container_health(container_name)
        print(f"[INFO] Health status after restart: {health_status}")

        if health_status == "healthy":
            print(f"[SUCCESS] Container {container_name} is now healthy.")
            return

    # Step 6: Configure SQL Server if necessary
    print("[INFO] Attempting SQL Server configuration...")
    configure_sql_server_connection()

    # Final health check
    health_status = check_container_health(container_name)
    if health_status == "healthy":
        print(f"[SUCCESS] Container {container_name} is now healthy.")
    else:
        print(f"[ERROR] Container {container_name} is still unhealthy. Further manual intervention is required.")

if __name__ == "__main__":
    fix_mssql_container()