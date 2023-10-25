from flask import Flask, request, session, jsonify
import jwt
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Define the game board as dictionary with keys 1 to 9
game_board = {1: ' ', 2: ' ', 3: ' ', 4: ' ', 5: ' ', 6: ' ', 7: ' ', 8: ' ', 9: ' '}

player_tokens = ['X', 'O']

# List of loggedin players
logged_in_players = []

users = {
    'team1':'password1',
    'team2':'password2',
    'team3':'password3'
}

# 'X' player goes first 
current_player="None"

@app.route('/login', methods=['POST'])
def login():
    global logged_in_players, current_player
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if len(logged_in_players)<2:
        if username in users and users[username] == password and username:
            session_data = {'username': username}
            session_key = jwt.encode(session_data, app.secret_key, algorithm='HS256')
            if username not in logged_in_players:
                logged_in_players.append(username)
                if len(logged_in_players) == 2:
                    current_player = logged_in_players[0]
            print(logged_in_players)
            print(len(logged_in_players))
            return jsonify({'message': 'Login successful', 'session_key': session_key}), 200
        else:
            return jsonify({'error': 'Login failed'}), 401
    else:
        return jsonify({'error': 'Two players already logged in'}), 401


@app.route('/hello', methods=['GET'])
def hello():
    session_key = request.headers.get('X-Session-Key')
    try:
        session_data = jwt.decode(session_key, app.secret_key, algorithms=['HS256'])
        username = session_data.get('username')
        print(username)
        return jsonify({'message': 'Hello, {}!'.format(username)}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Session key has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Unauthorized'}), 401


@app.route('/game_state', methods=['GET'])
def get_game_state():
    global logged_in_players
    session_key = request.headers.get('X-Session-Key')
    try:
        session_data = jwt.decode(session_key, app.secret_key, algorithms=['HS256'])
        if len(logged_in_players) != 2:
            return jsonify({'message': "Waiting for players"})
        else:
            return jsonify({'game_board': game_board, 'current_player': current_player})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Session key has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Unauthorized'}), 401


@app.route('/make_move', methods=['POST'])
def make_move():
    global logged_in_players, current_player, game_board, player_tokens
    session_key = request.headers.get('X-Session-Key')
    try:
        session_data = jwt.decode(session_key, app.secret_key, algorithms=['HS256'])
        username = session_data.get('username')
        if username == current_player:
            position = request.get_json()['position']
            if is_valid_move(position):
                game_board[position] = player_tokens[logged_in_players.index(current_player)]
                if current_player == logged_in_players[0]:
                    current_player = logged_in_players[1]
                else:
                    current_player = logged_in_players[0]
                win = checkWinner()
                if win != None:
                    print("Player "+ logged_in_players[player_tokens.index(win)] + " has won the game")
                
                return jsonify({'message': 'Well played'}), 200
            else: 
                return jsonify({'message': 'Invalid play. Try again!'}), 400
        else:
            return jsonify({'message': 'Not your turn'}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Session key has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Unauthorized'}), 401


def is_valid_move(position):
    return 1 <= position <= 9 and game_board[position] == ' '

@app.route("/")
def home():
    return "Hello from Turbine Kreuzberg"


@app.route('/reset', methods=['GET'])
def reset():
    global logged_in_players, game_board
    logged_in_players = []
    game_board = {1: ' ', 2: ' ', 3: ' ', 4: ' ', 5: ' ', 6: ' ', 7: ' ', 8: ' ', 9: ' '}

    return jsonify({'message': 'Game was reset'}), 200

def checkWinner():
    global game_board

    win_combinations = [
        [1, 2, 3],  # Rows
        [4, 5, 6],
        [7, 8, 9],
        [1, 4, 7],  # Columns
        [2, 5, 8],
        [3, 6, 9],
        [1, 5, 9],  # Diagonals
        [3, 5, 7]
    ]

    for combination in win_combinations:
        a, b, c = combination
        if game_board[a] == game_board[b] == game_board[c]:
            if game_board[a] is not None:
                return game_board[a]

    return None


# if __name__ == "__main__":
#     app.run(debug=True)