import psycopg2
import pandas as pd
from .secret import get_secret

def view_locations():
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="",  # Replace with your database name
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM locations;")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

def export_locations_to_csv(csv_filename="locations.csv"):
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="",  # Replace with your database name
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    
    query = "SELECT * FROM locations;"
    df = pd.read_sql(query, connection)
    
    # Export DataFrame to a CSV file.
    df.to_csv(csv_filename, index=False)
    
    print(f"Data exported to {csv_filename}")
    
    connection.close()  

if __name__ == '__main__':
    view_locations()