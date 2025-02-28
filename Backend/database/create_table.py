import psycopg2
from secret import get_secret

def drop_table_if_exists(connection, table_name):
    try:
        cursor = connection.cursor()
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_table_query)
        connection.commit()
        print(f"Table {table_name} dropped successfully.")
    except Exception as error:
        print(f"Error dropping table {table_name}: {error}")
    finally:
        cursor.close()

# TODO: Delete the two wait_times tables and create them again

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

        drop_table_if_exists(connection, "wait_times")
        drop_table_if_exists(connection, "wait_times_today")
        # Define table schema 
        """
        This is how we will store our operating times
        {
            "Monday": {
                "open_time": 9,
                "close_time": 22
            }
            "Tuesday": {
                "open_time": 9,
                "close_time": 22
            }
        }
        """
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
            websiteURI TEXT,
            operating_time JSONB
        );
        """


        """
        Define the table schema to hold the wait_times by the hour based on historical data
        location_id references a location in the locations table
        wait_times in a JSONB that will store the day of the week and wait time for each hour it's open
        updated_at stores when we made this update
            {
                "Monday": {
                    "9": 15,
                    "10": 20,
                    "11": 25
                },
                "Tuesday": {
                    "9": 10,
                    "10": 10,
                    "11": 25
                }
            }
        """
        create_wait_times_table = """
        CREATE TABLE IF NOT EXISTS wait_times (
            id SERIAL PRIMARY KEY,
            location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
            wait_times_data JSONB NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (location_id)
        );  
        """

        """
        This will keep track of the live wait times for each location
        This will clear at the end of the day everday and then be sent into the create_wait_times_table
        """
        create_wait_times_today_table = """
        CREATE TABLE IF NOT EXISTS wait_times_today (
            id SERIAL PRIMARY KEY,
            location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
            day TEXT NOT NULL CHECK (day IN ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
            hour INTEGER NOT NULL CHECK (hour BETWEEN 0 and 23),
            avg_wait_time_per_hour JSONB,
            live_wait_time INTEGER NOT NULL,
            sample_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location_id, day, hour)
        );
        """

        create_wait_time_submissions_table = """ 
        CREATE TABLE IF NOT EXISTS wait_time_submissions (
            id SERIAL PRIMARY KEY,
            location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
            day TEXT NOT NULL CHECK (day IN ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
            hour INTEGER NOT NULL CHECK (hour BETWEEN 0 and 23),
            wait_time INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_locations_table)
        cursor.execute(create_wait_times_table)
        cursor.execute(create_wait_times_today_table)
        cursor.execute(create_wait_time_submissions_table)
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