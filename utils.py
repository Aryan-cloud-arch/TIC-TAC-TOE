"""
UTILITIES - Messages, keyboards, helpers
"""

import random
import string
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import config

# ============ MESSAGES ============
WELCOME_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━
 TIC TAC TOE • ARENA
━━━━━━━━━━━━━━━━━━━━━━

Welcome {name}!

Select an option:
"""

DIFFICULTY_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━
 SELECT DIFFICULTY
━━━━━━━━━━━━━━━━━━━━━━

Choose your opponent:
"""

FORCESUB_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━
 TIC TAC TOE • ARENA
━━━━━━━━━━━━━━━━━━━━━━

⚠️ Join Our Channel

To use this bot, you must
join our channel first!

After joining, click /start
"""

HELP_MESSAGE = """
━━━━━━━━━━━━━━━━━━━━━━
 HOW TO PLAY
━━━━━━━━━━━━━━━━━━━━━━

🎮 Commands:
/play - Start new game
/challenge - Challenge players
/stats - Your statistics
/leaderboard - Top players

📋 Rules:
Get 3 in a row to win!
Horizontal, Vertical or Diagonal

💰 Points:
Win: +25 points
Draw: +10 points
Loss: +5 points

Good luck! 🎯
"""

# ============ KEYBOARDS ============
def get_main_menu_keyboard():
    """Main menu buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Play vs Bot", callback_data="play_bot")],
        [InlineKeyboardButton("⚔️ Challenge Friend", callback_data="challenge")],
        [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

def get_difficulty_keyboard():
    """Difficulty selection buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Easy", callback_data="difficulty_easy")],
        [InlineKeyboardButton("🟡 Medium", callback_data="difficulty_medium")],
        [InlineKeyboardButton("🔴 Hard", callback_data="difficulty_hard")],
        [InlineKeyboardButton("💀 Impossible", callback_data="difficulty_impossible")],
        [InlineKeyboardButton("◀️ Back", callback_data="menu")]
    ])

def get_game_keyboard(game_session):
    """Generate game board keyboard"""
    board = game_session['board']
    game_id = game_session['game_id']
    
    keyboard = []
    for row in range(3):
        row_buttons = []
        for col in range(3):
            pos = row * 3 + col
            if board[pos] == 0:
                btn_text = "⬜"
                callback = f"move_{game_id}_{pos}"
            elif board[pos] == 1:
                btn_text = "❌"
                callback = "occupied"
            else:
                btn_text = "⭕"
                callback = "occupied"
            
            row_buttons.append(InlineKeyboardButton(btn_text, callback_data=callback))
        keyboard.append(row_buttons)
    
    # Add forfeit button
    keyboard.append([InlineKeyboardButton("🏳️ Surrender", callback_data=f"forfeit_{game_id}")])
    
    return InlineKeyboardMarkup(keyboard)

def get_game_over_keyboard():
    """Game over buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Play Again", callback_data="play_again")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")]
    ])

def get_forcesub_keyboard():
    """Forcesub buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=config.FORCESUB_CHANNEL)]
    ])

def get_challenge_keyboard(challenge_id):
    """Challenge accept/decline buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Accept", callback_data=f"accept_{challenge_id}")],
        [InlineKeyboardButton("❌ Decline", callback_data=f"decline_{challenge_id}")]
    ])

def get_back_keyboard():
    """Back to menu button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="menu")]
    ])

# ============ HELPERS ============
def generate_game_id():
    """Generate unique game ID"""
    timestamp = str(int(datetime.now().timestamp()))
    random_str = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"{timestamp}_{random_str}"

def render_board(game_session):
    """Render game board as text"""
    board = game_session['board']
    symbols = {0: '⬜', 1: '❌', 2: '⭕'}
    
    text = f"""━━━━━━━━━━━━━━━━━━━━━━
 TIC TAC TOE • ARENA
━━━━━━━━━━━━━━━━━━━━━━
You ❌  •  ⭕ Bot

    {symbols[board[0]]}  {symbols[board[1]]}  {symbols[board[2]]}
    {symbols[board[3]]}  {symbols[board[4]]}  {symbols[board[5]]}
    {symbols[board[6]]}  {symbols[board[7]]}  {symbols[board[8]]}

Your turn
━━━━━━━━━━━━━━━━━━━━━━"""
    
    return text

def format_stats(stats):
    """Format user statistics"""
    if not stats:
        return "No stats available yet!"
    
    total_games = stats['wins'] + stats['losses'] + stats['draws']
    win_rate = (stats['wins'] / total_games * 100) if total_games > 0 else 0
    
    return f"""━━━━━━━━━━━━━━━━━━━━━━
 YOUR STATS
━━━━━━━━━━━━━━━━━━━━━━

@{stats.get('username', 'Player')}

Games: {total_games}
Wins: {stats['wins']}
Losses: {stats['losses']}
Draws: {stats['draws']}

Win Rate: {win_rate:.1f}%
Points: {stats['points']}
Best Streak: {stats['best_streak']} 🔥

━━━━━━━━━━━━━━━━━━━━━━"""

def format_leaderboard(players):
    """Format leaderboard"""
    text = """━━━━━━━━━━━━━━━━━━━━━━
 LEADERBOARD
━━━━━━━━━━━━━━━━━━━━━━

"""
    
    medals = ["🥇", "🥈", "🥉"]
    
    for i, player in enumerate(players):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} @{player['username']} - {player['points']}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━"
    
    return text

def get_challenge_message(challenger_name):
    """Format challenge message"""
    return f"""━━━━━━━━━━━━━━━━━━━━━━
 TIC TAC TOE • ARENA
━━━━━━━━━━━━━━━━━━━━━━

⚔️ CHALLENGE!

{challenger_name} wants to play!

Who dares to accept?

⏰ Expires in 60 seconds
━━━━━━━━━━━━━━━━━━━━━━"""

async def check_membership(bot, user_id):
    """Check if user is member of forcesub channel"""
    if not config.FORCESUB_CHANNEL:
        return True
    
    try:
        member = await bot.get_chat_member(config.FORCESUB_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def log_game_result(bot, game_data):
    """Log game result to Telegram group"""
    if not config.LOG_GROUP_ID:
        return
    
    message = f"""━━━━━━━━━━━━━━━━━━━━━━
🎮 GAME COMPLETED
━━━━━━━━━━━━━━━━━━━━━━

Game ID: {game_data.get('game_id')}

Winner: {game_data.get('winner')}
Moves: {game_data.get('moves_count')}

⏰ {datetime.now().strftime('%d %b %Y, %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━"""
    
    try:
        await bot.send_message(config.LOG_GROUP_ID, message)
    except:
        pass

def get_welcome_message(name):
    """Get welcome message with name"""
    return WELCOME_MESSAGE.format(name=name)
