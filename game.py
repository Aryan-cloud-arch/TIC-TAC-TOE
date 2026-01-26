"""
GAME LOGIC - Board, moves, win detection, AI
"""

import random

# Board positions
#  0 | 1 | 2
# -----------
#  3 | 4 | 5
# -----------
#  6 | 7 | 8

WIN_COMBINATIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical
    [0, 4, 8], [2, 4, 6]              # Diagonal
]

def create_game(game_id, player_id, difficulty='easy'):
    """Create new game session"""
    return {
        'game_id': game_id,
        'type': 'bot',
        'player1': player_id,
        'player2': 'bot',
        'board': [0] * 9,  # 0=empty, 1=X, 2=O
        'turn': player_id,
        'difficulty': difficulty,
        'moves_count': 0,
        'status': 'ongoing'
    }

def make_move(game_session, position, player_id):
    """Make a move on the board"""
    # Check if position is valid
    if game_session['board'][position] != 0:
        return {'valid': False, 'message': 'Position occupied!'}
    
    # Make move
    symbol = 1 if player_id == game_session['player1'] else 2
    game_session['board'][position] = symbol
    game_session['moves_count'] += 1
    
    # Switch turn
    if game_session['turn'] == game_session['player1']:
        game_session['turn'] = game_session['player2']
    else:
        game_session['turn'] = game_session['player1']
    
    # Check game status
    result = check_game_status(game_session)
    
    return {'valid': True, 'status': result['status'], 'winner': result.get('winner')}

def check_game_status(game_session):
    """Check if game is won, draw or ongoing"""
    board = game_session['board']
    
    # Check win
    for combo in WIN_COMBINATIONS:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != 0:
            winner = game_session['player1'] if board[combo[0]] == 1 else game_session['player2']
            return {'status': 'finished', 'winner': winner, 'combo': combo}
    
    # Check draw
    if game_session['moves_count'] == 9:
        return {'status': 'finished', 'winner': 'draw'}
    
    return {'status': 'ongoing'}

def get_bot_move(game_session):
    """Get bot's move based on difficulty"""
    difficulty = game_session.get('difficulty', 'easy')
    board = game_session['board']
    
    if difficulty == 'easy':
        # Random move
        empty_cells = [i for i in range(9) if board[i] == 0]
        return random.choice(empty_cells)
    
    elif difficulty == 'medium':
        # Try to block player wins, else random
        move = find_blocking_move(board)
        if move is not None:
            return move
        empty_cells = [i for i in range(9) if board[i] == 0]
        return random.choice(empty_cells)
    
    elif difficulty == 'hard':
        # Try to win, then block, then random
        move = find_winning_move(board, 2)  # Bot is O (2)
        if move is not None:
            return move
        move = find_blocking_move(board)
        if move is not None:
            return move
        empty_cells = [i for i in range(9) if board[i] == 0]
        return random.choice(empty_cells)
    
    else:  # impossible
        # Use minimax algorithm
        return minimax_move(board)

def find_winning_move(board, symbol):
    """Find move that wins the game"""
    for combo in WIN_COMBINATIONS:
        values = [board[i] for i in combo]
        if values.count(symbol) == 2 and values.count(0) == 1:
            return combo[values.index(0)]
    return None

def find_blocking_move(board):
    """Find move that blocks opponent win"""
    return find_winning_move(board, 1)  # Player is X (1)

def minimax_move(board):
    """Minimax algorithm for impossible difficulty"""
    # Simplified version - always plays optimal
    best_score = -float('inf')
    best_move = None
    
    for i in range(9):
        if board[i] == 0:
            board[i] = 2  # Bot plays
            score = minimax(board, False)
            board[i] = 0  # Undo
            
            if score > best_score:
                best_score = score
                best_move = i
    
    return best_move

def minimax(board, is_maximizing):
    """Minimax recursive function"""
    # Check terminal states
    result = check_board_winner(board)
    if result == 2:  # Bot wins
        return 1
    elif result == 1:  # Player wins
        return -1
    elif 0 not in board:  # Draw
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == 0:
                board[i] = 2
                score = minimax(board, False)
                board[i] = 0
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == 0:
                board[i] = 1
                score = minimax(board, True)
                board[i] = 0
                best_score = min(score, best_score)
        return best_score

def check_board_winner(board):
    """Quick check for winner (for minimax)"""
    for combo in WIN_COMBINATIONS:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != 0:
            return board[combo[0]]
    return 0
