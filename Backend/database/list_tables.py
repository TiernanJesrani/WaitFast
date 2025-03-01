import psycopg2
from secret import get_secret


def list_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(table[0])
    except Exception as error:
        print("Error fetching tables:", error)
    finally:
        cursor.close()


if __name__ == "__main__":

    user, password = get_secret()
    connection = psycopg2.connect(
            dbname = "",
            user = user,
            password = password,
            host = "wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",  # or the IP address of your database server
            port = "5432" 
        )
    list_tables(connection)
    connection.close()