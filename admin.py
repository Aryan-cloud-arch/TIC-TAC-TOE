"""
ADMIN PANEL - Admin only commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import config
import database as db
from functools import wraps

# Admin decorator
def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in config.ADMIN_IDS:
            await update.message.reply_text("⛔ Admin only command!")
            return
        return await func(update, context)
    return wrapper

@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    text = """━━━━━━━━━━━━━━━━━━━━━━
    ADMIN PANEL
━━━━━━━━━━━━━━━━━━━━━━

Commands:
/setforcesub - Set forcesub channel
/removeforcesub - Remove forcesub
/broadcast - Send message to all
/stats - Bot statistics
/users - Total users count

━━━━━━━━━━━━━━━━━━━━━━"""
    
    await update.message.reply_text(text)

@admin_only
async def set_forcesub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set forcesub channel"""
    if not context.args:
        await update.message.reply_text("Usage: /setforcesub @channelname")
        return
    
    channel = context.args[0]
    
    # Update database
    db.update_settings('forcesub_channel', channel)
    db.update_settings('forcesub_enabled', True)
    
    # Update config
    config.FORCESUB_CHANNEL = channel
    config.FORCESUB_ENABLED = True
    
    await update.message.reply_text(f"✅ Forcesub set to {channel}")

@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return
    
    message = ' '.join(context.args)
    users = db.users.find()
    
    count = 0
    for user in users:
        try:
            await context.bot.send_message(user['user_id'], message)
            count += 1
        except:
            pass
    
    await update.message.reply_text(f"✅ Broadcast sent to {count} users")
