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
    results = query.name_search(query_string)
    # Return the results as JSON
    return jsonify(results=results)

@app.route('/playerInfo/<name>')
def playerInfo(name):
    tables = ['stats_23_24', 'stats_22_23', 'stats_21_22', 
             'stats_20_21', 'stats_19_20', 'stats_18_19', 
             'stats_17_18', 'stats_16_17', 'stats_15_16', 'stats_14_15']
    all_results = {}
    conn = query.connect_to_database()
    for table in tables:
        sql_query = f"""SELECT Pos, Tm, G, MP, FG, FGA,
                        `FG%`, 3P, 3PA, `3P%`, FT, FTA, `FT%`, 
                        TRB, AST, STL, BLK, TOV, PTS FROM {table}
                        WHERE player = '{name}' AND Tm != 'Tot' """
                  
        results = query.execute_query(conn, sql_query)
        all_results[table] = results

    image_sql_query = f"""SELECT image_url FROM stats_23_24 
                        WHERE player = '{name}' """
    image_url = query.execute_query(conn, image_sql_query)
    # need to add date, opp team, result, ORB, DRB, PF, GMS(maybe), +/- 
        #I think these should give more info, may even take some info out of the past 10 years stats
    # last_games_sql_query = f"""SELECT Pos, Tm, G, MP, FG, FGA,
    #                             `FG%`, 3P, 3PA, `3P%`, FT, FTA, `FT%`, 
    #                             TRB, AST, STL, BLK, TOV, PTS FROM 'last_5_games' 
    #                             WHERE player = '{name}' """
    
    # five_games = query.execute_query(conn, last_games_sql_query)
    full_image_url = "http://cdn.ssref.net/scripts/image_resize.cgi?min=200&url=" + image_url[0][0]
    return render_template('playerInfo.html', total_stats = all_results, image = full_image_url)

if __name__ == '__main__':
    app.run(debug=True)
