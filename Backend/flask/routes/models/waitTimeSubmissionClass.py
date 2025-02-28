from flaskClass import FlaskClass
from datetime import datetime, timedelta
from Backend.database.secret import get_secret
import psycopg2
import json

def get_db_connection():
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="your_db_name",
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    return connection

class WaitTimeSubmissionClass(FlaskClass):


    """
    Submits a wait time for a given location and updates the live wait time average.
    
    The live wait time is the average of all wait times submitted within the past 10 minutes
    for the current day and hour.
    """
    def submit_wait_time(self, location_id, wait_time):

        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            now = datetime.now()
            current_day = now.strftime("%A")
            current_hour = now.hour


            # 1) Insert the new submission
            insert_submission_query = """
                INSERT INTO wait_time_submissions (location_id, day, hour, wait_time, submitted_at)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_submission_query, (location_id, current_day, current_hour, wait_time, now))
            connection.commit()
            
            # 2. Query for all submissions within the last 10 minutes.
            ten_minutes_ago = now - timedelta(minutes=10)
            query_avg = """
                SELECT AVG(wait_time)::numeric, COUNT(*)
                FROM wait_time_submissions
                WHERE location_id = %s
                AND day = %s
                AND hour = %s
                AND submitted_at >= %s;
            """
            cursor.execute(query_avg, (location_id, current_day, current_hour, ten_minutes_ago))
            avg_result = cursor.fetchone()
            avg_wait_time, sample_count = avg_result

            if avg_wait_time is None:
                avg_wait_time = wait_time
                sample_count = 1
            else:
                avg_wait_time = int(round(float(avg_wait_time)))

            print(f"Location {location_id} ({current_day} at hour {current_hour}):")
            print(f"Average wait time (last 10 minutes): {avg_wait_time} minutes, based on {sample_count} submissions.")

            # 3. Query for the entire hour average.
            start_of_hour = now.replace(minute=0, second=0, microsecond=0)
            end_of_hour = start_of_hour + timedelta(hours=1)
            query_hour_avg = """
                SELECT AVG(wait_time)::numeric
                FROM wait_time_submissions
                WHERE location_id = %s
                AND day = %s
                AND hour = %s
                AND submitted_at >= %s AND submitted_at < %s;
            """
            cursor.execute(query_hour_avg, (location_id, current_day, current_hour, start_of_hour, end_of_hour))
            hour_avg_result = cursor.fetchone()
            if hour_avg_result and hour_avg_result[0] is not None:
                avg_wait_hour = int(round(float(hour_avg_result[0])))
            else:
                avg_wait_hour = avg_wait_time        

            # 4. Upsert the computed average into wait_times_today.
            avg_wait_json = json.dumps({ str(current_hour): avg_wait_hour })
            upsert_query = """
                INSERT INTO wait_times_today (location_id, day, hour, avg_wait_time_per_hour, live_wait_time, sample_count, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (location_id, day, hour)
                DO UPDATE SET 
                    avg_wait_time_per_hour = EXCLUDED.avg_wait_time_per_hour,
                    live_wait_time = EXCLUDED.live_wait_time,
                    sample_count = EXCLUDED.sample_count,
                    updated_at = EXCLUDED.updated_at;
            """
            cursor.execute(upsert_query, (location_id, current_day, current_hour, avg_wait_json, avg_wait_time, sample_count, now))
            connection.commit()

            print("Live wait time record updated in wait_times_today.")
        
        except Exception as e:
            connection.rollback()
            print("Error submitting wait time:", e)
        finally:
            cursor.close()
            connection.close()

    """
    At X TIME, for every location in the database, this function:
      1. Retrieves the live wait time averages stored in the avg_wait_time_per_hour JSONB 
         from the wait_times_today table.
      2. Merges those live values with any existing historical data in the wait_times table,
         by taking the simple average between the historical value and the live value for each hour.
      3. Upserts the merged data into the wait_times table.
      4. Finally, clears the live data tables (wait_times_today and wait_time_submissions).
    
    This version explicitly loops through every location_id from the locations table.
    """

    def daily_archive_all_locations():
        connection = get_db_connection()
        try:
            cursor = connection.cursor()

            # 1) Get all locations IDs from the locations table
            cursor.execute("SELECT id from locations;")
            all_locations = [row[0] for row in cursor.fetchall()]

            # 2) For each location, retrieve live data from wait_times_today
            for location_id in all_locations:
                # Retrieve live data for this location
                cursor.execute("""
                    SELECT day, hour, avg_wait_time_per_hor
                    FROM wait_times_today
                               WHERE location_id = %s
                    """, (location_id,))
                rows = cursor.fetchall()
                if not rows:
                    # If there is no live data for this location, skip it
                    continue
                
                # Build a nested dictionary of the data from todya { day: {"hour": value,..,},}
                wait_data_today = {}
                for day, hour, avg_wait_json in rows:
                    if isinstance(avg_wait_json, str):
                        hour_data = json.loads(avg_wait_json)
