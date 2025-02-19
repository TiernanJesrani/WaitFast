import psycopg2
from secret import get_secret

def view_locations():
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="your_db_name",  # Replace with your database name
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM locations;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    connection.close()

if __name__ == '__main__':
    view_locations()