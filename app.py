from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import date, timedelta
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

@app.route('/')
def index():
    y_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    return redirect(url_for('home', date=y_date))

@app.route('/home/<date>')
def home(date):
    conn = query.connect_to_database()
    sql_query = f"""SELECT Team, MIN(Opp) AS Opponent, MIN(Result) AS Result,
                    MIN(q1_teamScoring) AS Q1, MIN(q2_teamScoring) AS Q2, MIN(q3_teamScoring) AS Q3, 
                    MIN(q4_teamScoring) AS Q4, MIN(OT_teamScoring) AS OT, MIN(2OT_teamScoring) AS 2OT
                    FROM `last_5_games`
                    WHERE Date = "{date}"
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
            results.remove(matching_result)

    new_results = process_data(merged_results)
    return render_template('home.html', results = new_results, count = len(new_results), date = date)


@app.route('/search', methods=['POST'])
def search():
    query_string = request.json.get('query', '')
    results = query.name_search(query_string)
    return jsonify(results=results)


@app.route('/playerInfo/<name>')
def playerInfo(name):
    tables = ['stats_23_24', 'stats_22_23', 'stats_21_22', 'stats_20_21', 'stats_19_20', 'stats_18_19', 
              'stats_17_18', 'stats_16_17', 'stats_15_16', 'stats_14_15', 'stats_13_14', 'stats_12_13', 
              'stats_11_12', 'stats_10_11', 'stats_9_10', 'stats_8_9', 'stats_7_8', 'stats_6_7', 
              'stats_5_6', 'stats_4_5', 'stats_3_4', 'stats_2_3','stats_1_2', 'stats_0_1', 'stats_99_0']
    all_results = {}
    conn = query.connect_to_database()
    for table in tables:
        sql_query = f"""SELECT Pos, Tm, G, MP, FG, FGA,
                        `FG%`, 3P, 3PA, `3P%`, FT, FTA, `FT%`, 
                        TRB, AST, STL, BLK, TOV, PTS FROM {table}
                        WHERE player = "{name}" AND Tm != 'Tot' """ # instead of tot, its 2Tm or 3Tm ect for new tables
                  
        results = query.execute_query(conn, sql_query)
        all_results[table] = results

    image_sql_query = f"""SELECT image_url FROM stats_23_24 
                        WHERE player = '{name}' """
    image_url = None
    image_url = query.execute_query(conn, image_sql_query)

    last_games_sql_query = f"""SELECT Date, Team, `@`, OPP, Result, MP, FG, FGA,
                                `FG%`, 3P, 3PA, `3P%`, FT, FTA, `FT%`, 
                                ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, `+/-` FROM `last_5_games` 
                                WHERE player = "{name}" """
    
    five_games = query.execute_query(conn, last_games_sql_query)

    full_image_url = None
    if(image_url): full_image_url = "http://cdn.ssref.net/scripts/image_resize.cgi?min=200&url=" + image_url[0][0]
    else: full_image_url = "https://cdn-icons-png.flaticon.com/512/10701/10701484.png"

    season_sums = [0] * 17
    last5_sums = [0] * 20
    k = 1
    games = 0

    for key, value in all_results.items(): # check if this properly calculates average
        for item in value:
            games += int(item[2])
            for val in item[3:]:
                if(k == 4 or k == 7 or k == 10): 
                    k+=1
                    continue

                else :season_sums[k] += float(float(val) * int(item[2]) or 0) 
                k+=1
            k = 1

    for i in range(len(season_sums)):
        if i in [4, 7, 10]: season_sums[i] = round(season_sums[i-2] / season_sums[i-1], 2)
        else : season_sums[i] = round(season_sums[i] / games, 2)

    season_sums[0] = games
    k = 0
    if(five_games):
        for value in five_games: 
            for val in value[5:]:
                if(k == 3 or k == 6 or k == 9): 
                    k+=1
                    continue
                # If the value is a time string (e.g., "35:40")
                if ':' in val:
                    minutes, seconds = map(int, val.split(':'))
                    # Round up the minutes if seconds >= 30
                    if seconds >= 30:
                        minutes += 1
                    last5_sums[k] += minutes
                else:
                    last5_sums[k] += float(val)
                k += 1
            k = 0

        for j in range(len(last5_sums)):
            if( j == 3 or j == 6 or j == 9): 
                if(last5_sums[j-1] != 0):
                    last5_sums[j] = round(last5_sums[j-2] / last5_sums[j-1], 3)
                else : last5_sums[j] = 'NA'
            else: last5_sums[j] = round(last5_sums[j] / len(five_games), 3)
    
    return render_template('playerInfo.html', total_stats = all_results, image = full_image_url, name = name,
                           five_games = five_games, season_sums = season_sums, last5_sums = last5_sums)


@app.route('/gameInfo/<team>vs<opp>/<date>')
def gameInfo(team, opp, date):
    conn = query.connect_to_database()
    sql_query = f"""SELECT * FROM `last_5_games`
                    WHERE Date = "{date}"
                    AND (Team = "{team}" OR Team = "{opp}")
                    ORDER BY Team """
    teams = query.execute_query(conn, sql_query)
    team1_info = []
    team2_info = []
    for t in teams: 
        if(t[2] != team):
            team2_info.append(t)
        else: team1_info.append(t)

    team1_sums = [0] * 20
    team2_sums = [0] * 20

    for row in team1_info:
        for i in range(20):
            if i == 0: continue
            if i == 3 or i == 6 or i == 9 or i == 19: team1_sums[i] += float(row[i + 7] or 0) 
            else: team1_sums[i] += int(row[i + 7] or 0)  

    team1_sums[0] = 240
    team1_sums[3] = round(team1_sums[1] / team1_sums[2], 3)
    team1_sums[6] = round(team1_sums[4] / team1_sums[5], 3)
    team1_sums[9] = round(team1_sums[7] / team1_sums[8], 3)

    for row in team2_info:
        for i in range(20):
            if i == 0: continue;
            if i == 3 or i == 6 or i == 9 or i == 19: team2_sums[i] += float(row[i + 7] or 0) 
            else: team2_sums[i] += int(row[i + 7] or 0)  

    team2_sums[0] = 240
    team2_sums[3] = round(team2_sums[1] / team2_sums[2], 3)
    team2_sums[6] = round(team2_sums[4] / team2_sums[5], 3)
    team2_sums[9] = round(team2_sums[7] / team2_sums[8], 3)

    return render_template('gameInfo.html', team1_info = team1_info, team2_info = team2_info, team = team, 
                           team2 = opp, team1_sums = team1_sums, team2_sums = team2_sums)


if __name__ == '__main__':
    app.run(debug=True)
