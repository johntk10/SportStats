from flask import Flask, render_template, request, jsonify
import modules.query as query 

app = Flask(__name__)


def process_data(raw_data):
    processed_data = []
    for game in raw_data:
        team1, team2, result, *quarter_scores = game = game
        result_parts = result.split()
        outcome = result_parts[0]  # Win or Loss
        scores = result_parts[1].split('-')  # Split scores
        processed_data.append({
            'team1': team1,
            'team1_score': scores[0],
            'team2': team2,
            'team2_score': scores[1],
            'outcome': 'W',
            'team1_q1_scoring': quarter_scores[0],
            'team1_q2_scoring': quarter_scores[1],
            'team1_q3_scoring': quarter_scores[2],
            'team1_q4_scoring': quarter_scores[3],
            'team1_ot1_scoring': quarter_scores[4] if len(quarter_scores) > 4 else None,
            'team1_ot2_scoring': quarter_scores[5] if len(quarter_scores) > 5 else None,
            'team2_q1_scoring': quarter_scores[6],
            'team2_q2_scoring': quarter_scores[7],
            'team2_q3_scoring': quarter_scores[8],
            'team2_q4_scoring': quarter_scores[9],
            'team2_ot1_scoring': quarter_scores[10] if len(quarter_scores) > 10 else None,
            'team2_ot2_scoring': quarter_scores[11] if len(quarter_scores) > 11 else None,
        })
    return processed_data

# Define your routes
@app.route('/')
def home():
    conn = query.connect_to_database()
    sql_query = f"""SELECT Team, MIN(Opp) AS Opponent, MIN(Result) AS Result,
                    MIN(q1_teamScoring) AS Q1, MIN(q2_teamScoring) AS Q2, MIN(q3_teamScoring) AS Q3, 
                    MIN(q4_teamScoring) AS Q4, MIN(OT_teamScoring) AS OT, MIN(2OT_teamScoring) AS 2OT
                    FROM `last_5_games`
                    WHERE Date = "2024-03-20"
                    GROUP BY Team
                    ORDER BY Result DESC """
    results = query.execute_query(conn, sql_query)
    merged_results = []

# Iterate over each result
    for result in results:
        matching_result = next((r for r in results if r[0] == result[1]), None)
        if matching_result:
            new_game = result + matching_result[3:]
            merged_results.append(new_game)
            
            # results.remove(result)
            results.remove(matching_result)
    # print(merged_results)

    new_results = process_data(merged_results)
    return render_template('home.html', results = new_results, count = len(new_results))



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
                        WHERE player = "{name}" AND Tm != 'Tot' """
                  
        results = query.execute_query(conn, sql_query)
        all_results[table] = results

    image_sql_query = f"""SELECT image_url FROM stats_23_24 
                        WHERE player = '{name}' """
    image_url = query.execute_query(conn, image_sql_query)
    # need to add date, opp team, result, ORB, DRB, PF, GMS(maybe), +/- 
        #I think these should give more info, may even take some info out of the past 10 years stats
    last_games_sql_query = f"""SELECT Date, Team, `@`, OPP, Result, MP, FG, FGA,
                                `FG%`, 3P, 3PA, `3P%`, FT, FTA, `FT%`, 
                                ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, GmSc, `+/-` FROM `last_5_games` 
                                WHERE player = "{name}" """
    
    five_games = query.execute_query(conn, last_games_sql_query)
    # print(five_games)
    full_image_url = "http://cdn.ssref.net/scripts/image_resize.cgi?min=200&url=" + image_url[0][0]

    return render_template('playerInfo.html', total_stats = all_results, image = full_image_url, name = name, five_games = five_games)

@app.route('/gameInfo/<team>/vs/<opp>')
def gameInfo(team, opp):
    conn = query.connect_to_database()
    sql_query = f"""SELECT * FROM `last_5_games`
                    WHERE Date = "2024-03-20" 
                    AND (Team = "{team}" OR Team = "{opp}")
                    ORDER BY Team """
    teams = query.execute_query(conn, sql_query)
    team1_info = []
    team2_info = []
    for t in teams: 
        if(t[2] != team):
            team2_info.append(t)
        else: team1_info.append(t)
    print(team1_info)
    print(team2_info)
    return render_template('gameInfo.html', team1_info = team1_info, team2 = team2_info, team = team, team2 = opp)

if __name__ == '__main__':
    app.run(debug=True)
