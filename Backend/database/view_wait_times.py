import psycopg2
import pandas as pd
from secret import get_secret  # Adjust the import path if necessary

def view_wait_times():
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="",  # Replace with your database name
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM wait_times;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    connection.close()

def export_wait_times_to_csv(csv_filename="wait_times.csv"):
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="",  # Replace with your database name
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    
    query = "SELECT * FROM wait_times;"
    df = pd.read_sql(query, connection)
    df.to_csv(csv_filename, index=False)
    print(f"Data exported to {csv_filename}")
    connection.close()

if __name__ == '__main__':
    # Uncomment one of the following lines to test:
    # view_wait_times()
    export_wait_times_to_csv()
