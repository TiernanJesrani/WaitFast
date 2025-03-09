from flaskClass import FlaskClass
from datetime import datetime, timedelta
from Backend.database.secret import get_secret
import psycopg2
import json

def get_db_connection():
    user, password = get_secret()
    connection = psycopg2.connect(
        dbname="",
        user=user,
        password=password,
        host="wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    return connection

class WaitTimeSubmissionClass(FlaskClass):

    def __init__(self):
        return
    

    def get_date(self):
        return "hello"
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

    def daily_archive_all_locations(self):
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
                    SELECT day, hour, avg_wait_time_per_hour
                    FROM wait_times_today
                               WHERE location_id = %s
                    """, (location_id,))
                rows = cursor.fetchall()
                if not rows:
                    # If there is no live data for this location, skip it
                    continue
                
                # Build a nested dictionary of the data from today{ day: {"hour": value,..,},}
                wait_data_today = {}
                # These are the rows in the wait_times_today table
                for day, hour, avg_wait_json in rows:
                    if not isinstance(avg_wait_json, dict):
                        hour_data = json.loads(avg_wait_json)
                    else:
                        hour_data = avg_wait_json
                    # Ensure we use the hour as a string
                    hour_key = str(hour)
                    if hour_key not in hour_data:
                        continue
                    avg_hour_value = hour_data[hour_key]

                    if day not in wait_data_today:
                        wait_data_today[day] = {}
                    wait_data_today[day][hour_key] = avg_hour_value
            # 3) Retrieve existing historical data from wait_times for this location
            cursor.execute(""" 
                    SELECT wait_times_data FROM wait_times WHERE location_id = %s;
                    """, (location_id, ))
            result = cursor.fetchone()

            if result is None:
                # No historical record exists; use the live data as the new historical data
                new_hist_data = wait_data_today
                cursor.execute("""
                    INSERT INTO wait_times (location_id, wait_times_data, updated_at)
                    VALUES (%s, %s, NOW());
                """, (location_id, json.dumps(new_hist_data)))
            else:
                hist_wait_data = result[0]
                if not isinstance(hist_wait_data, dict):
                    hist_wait_data = json.loads(hist_wait_data)
                # 4 Merge live data into the historical data
                for day, live_hours in wait_data_today.items():
                    # If the day doesn't exist, just add it to the historical data
                    # When you take the average then you will just be adding it to itself and dividing by 2
                    if day not in hist_wait_data:
                        hist_wait_data[day] = live_hours
                    else:
                        # If the day already exists then for each hour in the live data for that day
                        for hour, live_value in live_hours.items():
                            if hour in hist_wait_data[day]:
                                old_value = hist_wait_data[day][hour]
                                merged_value = int(round((old_value + live_value) / 2))
                                hist_wait_data[day][hour] = merged_value
                            else:
                                hist_wait_data[day][hour] = live_value
                
                new_hist_data = hist_wait_data
                # 5) Update the historical record
                cursor.execute("""
                        UPDATE wait_times
                        SET wait_times_data = %s, updated_at = NOW()
                        WHERE location_id = %s;
                    """, (json.dumps(new_hist_data), location_id))
            connection.commit()
            print("Historical wait_times updated for all locations")

            # 6) Clear the live data tables
            cursor.execute("TRUNCATE TABLE wait_times_today;")
            cursor.execute("TRUNCATE TABLE wait_time_submissions;")
            connection.commit()
            print("wait_times_today and wait_time_submissions cleared")
        except Exception as e:
            connection.rollback()
            print("Error during daily archive:", e)
        finally:
            cursor.close()
            connection.close()



                    
