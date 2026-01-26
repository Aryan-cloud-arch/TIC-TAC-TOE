"""
DATABASE - MongoDB operations
"""

import os
from datetime import datetime
from pymongo import MongoClient
import config

# MongoDB connection
client = MongoClient(config.MONGO_URL)
db = client['tictactoe_arena']

# Collections
users = db['users']
active_games = db['active_games']
game_history = db['game_history']
settings = db['settings']

# ============ USER OPERATIONS ============
def add_user(user_id, username, first_name):
    """Add new user or update existing"""
    users.update_one(
        {'user_id': user_id},
        {
            '$set': {
                'username': username,
                'first_name': first_name,
                'last_active': datetime.now()
            },
            '$setOnInsert': {
                'points': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'streak': 0,
                'best_streak': 0,
                'joined_at': datetime.now()
            }
        },
        upsert=True
    )

def get_user_stats(user_id):
    """Get user statistics"""
    return users.find_one({'user_id': user_id})

def update_user_stats(user_id, result):
    """Update user stats after game"""
    update_data = {'last_active': datetime.now()}
    
    if result == 'win':
        update_data['wins'] = {'$inc': 1}
        update_data['points'] = {'$inc': 25}
        update_data['streak'] = {'$inc': 1}
    elif result == 'loss':
        update_data['losses'] = {'$inc': 1}
        update_data['points'] = {'$inc': 5}
        update_data['streak'] = 0
    else:  # draw
        update_data['draws'] = {'$inc': 1}
        update_data['points'] = {'$inc': 10}
    
    users.update_one({'user_id': user_id}, update_data)

def get_leaderboard(limit=10):
    """Get top players"""
    return list(users.find().sort('points', -1).limit(limit))

# ============ GAME OPERATIONS ============
def save_active_game(game_session):
    """Save active game to database"""
    active_games.replace_one(
        {'game_id': game_session['game_id']},
        game_session,
        upsert=True
    )

def get_active_game(game_id):
    """Get active game by ID"""
    return active_games.find_one({'game_id': game_id})

def delete_active_game(game_id):
    """Delete active game"""
    active_games.delete_one({'game_id': game_id})

def save_game_history(game_data):
    """Save completed game to history"""
    game_history.insert_one({
        **game_data,
        'timestamp': datetime.now()
    })

# ============ CHALLENGE OPERATIONS ============
def create_challenge(challenge_id, challenger_id, chat_id):
    """Create new challenge"""
    db['challenges'].insert_one({
        'challenge_id': challenge_id,
        'challenger_id': challenger_id,
        'chat_id': chat_id,
        'created_at': datetime.now()
    })

def get_challenge(challenge_id):
    """Get challenge by ID"""
    return db['challenges'].find_one({'challenge_id': challenge_id})

def delete_challenge(challenge_id):
    """Delete challenge"""
    db['challenges'].delete_one({'challenge_id': challenge_id})

# ============ SETTINGS OPERATIONS ============
def get_settings():
    """Get bot settings"""
    return settings.find_one() or {}

def update_settings(key, value):
    """Update settings"""
    settings.update_one(
        {},
        {'$set': {key: value}},
        upsert=True
    )
