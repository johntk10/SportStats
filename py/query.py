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




# Example usage
if __name__ == "__main__":
    # Connect to the database
    conn = connect_to_database()

    if conn:
        print("Connected to database.")
        query = "SELECT * FROM stats_23_24 LIMIT 10"
        result = execute_query(conn, query)
        
        # Print the results
        if result:
            for row in result:
                print(row)
        else:
            print("No results found.")

        # Close the database connection
        conn.close()
    else:
        print("Failed to connect to the database.")
