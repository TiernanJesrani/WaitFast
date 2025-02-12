import psycopg2
from secret import get_secret


def create_table():
    # Connect to the database
    user, password = get_secret()
    try:
        connection = psycopg2.connect(
            dbname = "",
            user = user,
            password = password,
            host = "wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",  # or the IP address of your database server
            port = "5432" 
        )
        cursor = connection.cursor()

        # Define table schema 
        create_locations_table = """
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            placed_id VARCHAR(255) UNIQUE,
            displayName TEXT,
            delivery BOOLEAN,
            latlong point,
            type TEXT,
            photos JSONB,
            websiteURI TEXT
        );
        """

        # Define table schema for opening hours
        # location_id connects to the locations table
        create_opening_hours_table = """
        CREATE TABLE IF NOT EXISTS opening_hours (
            id SERIAL PRIMARY KEY,
            location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
            day TEXT,
            open_time TIME,
            close_time TIME,
            open_day TEXT,
            close_day TEXT
        );
        """

        cursor.execute(create_locations_table)
        cursor.execute(create_opening_hours_table)
        connection.commit()
        print("Tables created successfully")

    except Exception as error:
        print("Error while creating tables:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    create_table()