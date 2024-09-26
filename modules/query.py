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
    tables = [
    'stats_23_24', 'stats_22_23', 'stats_21_22', 'stats_20_21', 'stats_19_20',
    'stats_18_19', 'stats_17_18', 'stats_16_17', 'stats_15_16', 'stats_14_15',
    'stats_13_14', 'stats_12_13', 'stats_11_12', 'stats_10_11', 'stats_9_10',
    'stats_8_9', 'stats_7_8', 'stats_6_7', 'stats_5_6', 'stats_4_5', 
    'stats_3_4', 'stats_2_3', 'stats_1_2', 'stats_0_1', 'stats_99_0']

    subqueries = []

    for table in tables:
        subquery = f"""
            SELECT Player, MAX(PTS) AS PTS
            FROM {table}
            WHERE Player LIKE '{name}%'
            GROUP BY Player """

        subqueries.append(subquery)

    union_query = " UNION ".join(subqueries)

    sql_query = f"""
        SELECT Player
        FROM (
            {union_query}
        ) AS SUB
        GROUP BY Player
        ORDER BY CAST(MAX(PTS) AS SIGNED) DESC
        LIMIT 10; """

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