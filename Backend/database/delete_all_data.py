import psycopg2
from secret import get_secret

def truncate_all_tables(connection):
    try:
        cursor = connection.cursor()
        
        # Disable foreign key checks
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Truncate each table
        tables = ["locations", "wait_times", "wait_times_today"]
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
            print(f"Table {table} truncated successfully.")
        
        # Re-enable foreign key checks
        cursor.execute("SET session_replication_role = 'origin';")
        
        connection.commit()
    except Exception as error:
        print("Error truncating tables:", error)
    finally:
        cursor.close()

def main():
    # Connect to the database
    user, password = get_secret()
    try:
        connection = psycopg2.connect(
            dbname = "",
            user = user,
            password = password,
            host = "wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
            port = "5432"
        )
        truncate_all_tables(connection)
    except Exception as error:
        print("Error connecting to the database:", error)
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    main()