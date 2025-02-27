from flaskClass import FlaskClass
from datetime import datetime
from Backend.database.secret import get_secret
import psycopg2

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

    def submit_wait_time(location_id, wait_time):

        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            now = datetime.now()
            current_day = now.strftime("%A")
            current_hour = now.hour
