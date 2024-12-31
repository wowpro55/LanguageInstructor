import sqlite3
import csv
from datetime import datetime

# Database file path
db_path = "db.sqlite3"

# Output file name
output_file = "error_log.csv"

# Connect to the SQLite database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to fetch all error logs
    query = """
    SELECT error_id, error_message, error_location, created_at, user_id 
    FROM core_errorlog
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Column headers
    headers = ["Error ID", "Error Message", "Error Location", "Created At", "User ID"]

    # Write to CSV file
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write headers
        writer.writerows(rows)    # Write data

    print(f"Error logs have been successfully exported to {output_file}")

except sqlite3.Error as e:
    print(f"SQLite error occurred: {e}")

finally:
    # Close the database connection
    if conn:
        conn.close()
