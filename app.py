from flask import Flask, render_template
import mysql.connector
import py.query as query 
app = Flask(__name__)

# mysql_config = {
#    'host': '96.38.123.26',
#    'user': 'ghanshyam',
#    'password': 'poopturdssX123',
#    'database': 'basketballstats'
# }

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/playerInfo')
def playerInfo():
   conn = query.connect_to_database()
   sql_query = f"""SELECT * FROM stats_23_24
                  WHERE player = 'Lebron James' """
                  
   results = query.execute_query(conn, sql_query)

   return render_template('playerInfo.html', results = results)




if __name__ == '__main__':
    app.run(debug=True)