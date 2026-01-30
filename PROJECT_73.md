
# PROJECT ID: 73
# TELEGRAM DM BACKUP SYSTEM

## OBJECTIVE
Build a real-time Telegram conversation backup system that mirrors all messages between two users to a private backup group. Two bots represent each person for clear sender attribution.

## ARCHITECTURE
```
User A ◄──── DM Chat ────► User B
                │
                ▼
         MONITOR SERVICE
         (User A's Account)
                │
        ┌───────┴───────┐
        ▼               ▼
   @UserA_Bot      @UserB_Bot
        │               │
        └───────┬───────┘
                ▼
          BACKUP GROUP
                │
                ▼
            MongoDB
```

## REQUIRED FEATURES
1. Text Messages
2. Photos
3. Videos
4. Voice Messages
5. Stickers
6. Documents/Files
7. View-Once Media Capture
8. Edit Detection
9. Delete Detection
10. Reply Chains
11. Offline Recovery
12. MongoDB Storage
13. Heroku Deployment

## TECH STACK
- Python 3.11+
- Telethon
- MongoDB Atlas
- Heroku
- Pydantic

## CONFIGURATION REQUIRED
```
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
BOT_A_TOKEN=
BOT_A_NAME=
BOT_B_TOKEN=
BOT_B_NAME=
MONITOR_PHONE=
USER_A_NAME=
USER_B_ID=
USER_B_NAME=
BACKUP_GROUP_ID=
MONGODB_URI=
```

## MESSAGE FLOW

### User A sends message:
User A sends "Hello" → Monitor detects → @UserA_Bot posts in backup group

### User B sends message:
User B sends "Hi" → Monitor detects → @UserB_Bot posts in backup group

### View-Once:
View-once sent → Captured → Saved as permanent media

### Edit:
Message edited → "✏️ Edited" notification posted as reply to original

### Delete:
Message deleted → "🗑️ Deleted" notification posted (original still visible)

## DATABASE SCHEMA
```
{
  original_msg_id: Number,
  group_msg_id: Number,
  sender: String,
  content: String,
  has_media: Boolean,
  media_type: String,
  is_view_once: Boolean,
  is_edited: Boolean,
  is_deleted: Boolean,
  reply_to_original: Number,
  reply_to_group: Number,
  timestamp: Date
}
```

## TIMELINE
8-12 days

## DELIVERABLES
1. Complete source code
2. Setup wizard
3. Documentation
4. Heroku deployment
5. Working demo
```

---
