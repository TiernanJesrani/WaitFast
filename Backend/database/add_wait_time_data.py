from .secret import get_secret
import psycopg2

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



def get_mi_places_from_db():
    
    connection = get_db_connection()

    mi_place_query = """
    SELECT displayname
    FROM locations
    WHERE address ILIKE '%Ann Arbor%';
    """

    try:
        cursor = connection.cursor()

        cursor = connection.cursor()
        cursor.execute(mi_place_query)

        result = cursor.fetchall()
        print(result)

    
    except Exception as e:
        connection.rollback()
        print("Error grabbing places: ", e)

if __name__ == "__main__":
    get_mi_places_from_db()