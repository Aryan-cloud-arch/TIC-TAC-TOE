"""
MAIN BOT FILE - Everything starts here
Handles: /start, /play, /challenge, /stats, /help, callbacks
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

import config
import game
import database as db
import utils
import admin

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ START COMMAND ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start - Check forcesub + Show menu"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Add user to database if new
    db.add_user(user.id, user.username, user.first_name)
    
    # Check forcesub
    if config.FORCESUB_ENABLED:
        is_member = await utils.check_membership(context.bot, user.id)
        
        if not is_member:
            # Show forcesub message
            await update.message.reply_text(
                text=utils.FORCESUB_MESSAGE,
                reply_markup=utils.get_forcesub_keyboard()
            )
            return
        
        # Auto-delete forcesub message if exists
        try:
            await context.bot.delete_message(chat_id, update.message.message_id - 1)
        except:
            pass
    
    # Show main menu
    await update.message.reply_text(
        text=utils.get_welcome_message(user.first_name),
        reply_markup=utils.get_main_menu_keyboard()
    )

# ============ PLAY COMMAND ============
async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start new game vs bot"""
    # Show difficulty selection
    await update.message.reply_text(
        text=utils.DIFFICULTY_MESSAGE,
        reply_markup=utils.get_difficulty_keyboard()
    )

# ============ CHALLENGE COMMAND ============
async def challenge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Challenge other players in group"""
    if update.effective_chat.type == 'private':
        await update.message.reply_text("Use /challenge in a group!")
        return
    
    # Create challenge
    challenger = update.effective_user
    challenge_id = utils.generate_game_id()
    
    # Store challenge
    db.create_challenge(challenge_id, challenger.id, update.effective_chat.id)
    
    # Show challenge message
    await update.message.reply_text(
        text=utils.get_challenge_message(challenger.first_name),
        reply_markup=utils.get_challenge_keyboard(challenge_id)
    )

# ============ STATS COMMAND ============
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)
    
    await update.message.reply_text(
        text=utils.format_stats(stats),
        reply_markup=utils.get_back_keyboard()
    )

# ============ LEADERBOARD COMMAND ============
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top players"""
    top_players = db.get_leaderboard(limit=10)
    
    await update.message.reply_text(
        text=utils.format_leaderboard(top_players),
        reply_markup=utils.get_back_keyboard()
    )

# ============ HELP COMMAND ============
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    await update.message.reply_text(
        text=utils.HELP_MESSAGE,
        reply_markup=utils.get_back_keyboard()
    )

# ============ CALLBACK HANDLER ============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    
    # Main Menu Callbacks
    if data == "play_bot":
        await query.edit_message_text(
            text=utils.DIFFICULTY_MESSAGE,
            reply_markup=utils.get_difficulty_keyboard()
        )
    
    # Difficulty Selection
    elif data.startswith("difficulty_"):
        difficulty = data.split("_")[1]
        game_id = utils.generate_game_id()
        
        # Create game session
        game_session = game.create_game(game_id, user.id, difficulty)
        db.save_active_game(game_session)
        
        # Show game board
        board_text = utils.render_board(game_session)
        keyboard = utils.get_game_keyboard(game_session)
        
        await query.edit_message_text(
            text=board_text,
            reply_markup=keyboard
        )
    
    # Game Move
    elif data.startswith("move_"):
        parts = data.split("_")
        game_id = parts[1]
        position = int(parts[2])
        
        # Get game session
        game_session = db.get_active_game(game_id)
        
        if not game_session:
            await query.answer("Game not found!", show_alert=True)
            return
        
        # Check if it's player's turn
        if game_session['turn'] != user.id:
            await query.answer("Not your turn!", show_alert=True)
            return
        
        # Make move
        result = game.make_move(game_session, position, user.id)
        
        if not result['valid']:
            await query.answer(result['message'], show_alert=True)
            return
        
        # Check game status
        if result['status'] == 'ongoing':
            # Bot makes move
            if game_session['type'] == 'bot':
                bot_move = game.get_bot_move(game_session)
                game.make_move(game_session, bot_move, 'bot')
                
                # Check again after bot move
                result = game.check_game_status(game_session)
        
        # Update board display
        board_text = utils.render_board(game_session)
        
        if result['status'] != 'ongoing':
            # Game ended
            db.delete_active_game(game_id)
            
            # Update stats
            if result['winner'] == user.id:
                db.update_user_stats(user.id, 'win')
                board_text += "\n\n✨ VICTORY! +25 Points"
            elif result['winner'] == 'draw':
                db.update_user_stats(user.id, 'draw')
                board_text += "\n\n🤝 DRAW! +10 Points"
            else:
                db.update_user_stats(user.id, 'loss')
                board_text += "\n\n😢 DEFEAT! +5 Points"
            
            # Log to group
            utils.log_game_result(context.bot, result)
            
            keyboard = utils.get_game_over_keyboard()
        else:
            keyboard = utils.get_game_keyboard(game_session)
        
        await query.edit_message_text(
            text=board_text,
            reply_markup=keyboard
        )
    
    # Challenge Accept
    elif data.startswith("accept_"):
        challenge_id = data.split("_")[1]
        # Handle challenge acceptance...
    
    # Play Again
    elif data == "play_again":
        await play_command(update, context)
    
    # Back to Menu
    elif data == "menu":
        await start_command(update, context)

# ============ MAIN FUNCTION ============
def main():
    """Start the bot"""
    # Create application
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("challenge", challenge_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Admin commands
    app.add_handler(CommandHandler("admin", admin.admin_panel))
    app.add_handler(CommandHandler("setforcesub", admin.set_forcesub))
    app.add_handler(CommandHandler("broadcast", admin.broadcast))
    
    # Start bot
    if config.WEBHOOK_URL:
        # Production (Heroku)
        app.run_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}"
        )
    else:
        # Development
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
