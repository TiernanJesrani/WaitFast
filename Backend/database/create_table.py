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
            place_id VARCHAR(255) UNIQUE,
            displayName TEXT,
            delivery BOOLEAN,
            address TEXT,
            latlong point,
            type TEXT[],
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
            close_time TIME
        );
        """

        # Define table schema for wait times by the hour
        # This table will store a wait time (in minutes) for each hour that a location is open
        # The day field is stored as TEXT for readability (e.g. 'Monday', 'Tuesday', ...),
        # and hour is an integer representing the hour of the day (0-23).
        # A uniqueness constraint ensures that each location, day, and hour combination appears only once.
        create_wait_times_table = """
        CREATE TABLE IF NOT EXISTS wait_times (
            id SERIAL PRIMARY KEY,
            location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
            day TEXT NOT NULL CHECK (day IN ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
            hour INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),
            wait_time INTEGER NOT NULL,
            sample_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (location_id, day, hour)
        );  
        """


        
        create_wait_times_submissions_table = """
        CREATE TABLE IF NOT EXISTS wait_times_submissions_table (
            id SERIAL PRIMARY KEY,
            location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
            user_id INTEGER, -- optional if we want to assocaite table with users
            submitted_wait_time INTEGER NOT NULL,
            submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """


        cursor.execute(create_locations_table)
        cursor.execute(create_opening_hours_table)
        cursor.execute(create_wait_times_table)
        cursor.execute(create_wait_times_submissions_table)
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