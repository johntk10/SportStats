import mysql.connector

# Connect to your MySQL database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="96.38.123.26",
            user="john",
            password="poopturdssX123",
            database="basketballstats"
        )
        return conn
    except mysql.connector.Error as err:
        print("Error connecting to MySQL:", err)

# Execute SQL query and return results
def execute_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except mysql.connector.Error as err:
        print("Error executing query:", err)

def name_search(name):
    sql_query = f"""
        SELECT Player
            FROM (
                SELECT DISTINCT Player, MAX(PTS) AS PTS
                FROM stats_23_24
                WHERE Player LIKE '{name}%'
                GROUP BY Player
            ) AS SUB
        ORDER BY PTS DESC;
    """
    

    conn = connect_to_database()

    results = []
    if conn:
        results = execute_query(conn, sql_query)
        conn.close()
    return results

def stat_search(name):
    sql_query = f"""
        SELECT * FROM stats_23_24
        WHERE Player LIKE '{name}%'
        ORDER BY CAST(PTS AS SIGNED) DESC
        LIMIT 10
    """

    conn = connect_to_database()

    results = []
    if conn:
        results = execute_query(conn, sql_query)
        conn.close()
    return results