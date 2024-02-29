from flask import Flask, render_template, request, jsonify
import modules.query as query 

app = Flask(__name__)

# Define your routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    query_string = request.json.get('query', '')
    # Call the Python function to execute the query
    results = query.search(query_string)
    # Return the results as JSON
    return jsonify(results=results)

@app.route('/playerInfo')
def playerInfo():
   conn = query.connect_to_database()
   sql_query = f"""SELECT * FROM stats_23_24
                  WHERE player = 'Lebron James' """
                  
   results = query.execute_query(conn, sql_query)

   return render_template('playerInfo.html', results = results)

if __name__ == '__main__':
    app.run(debug=True)
