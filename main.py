from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Running Successfully!"

def run_flask():
    # Render সাধারণত ১০০০০ পোর্ট ব্যবহার করে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# এটি বট চালু হওয়ার পাশাপাশি আলাদাভাবে চলবে
threading.Thread(target=run_flask).start()

# --- এখান থেকে আপনার আগের কোড শুরু ---
import telebot
from telebot import types
import json
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# --- CONFIGURATION (DON'T CHANGE IDs) ---
API_TOKEN = '8757325787:AAEg-KJWtB-qSSBHlmqPzIB_o_3YEmDm0W4'
ADMIN_ID = 7596820363  
LOG_GROUP_ID = -1003876835738  

# --- FIREBASE SETUP ---
try:
    service_account_env = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    
    if service_account_env:
        service_account_info = json.loads(service_account_env)
        cred = credentials.Certificate(service_account_info)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tiktok-94a9a-default-rtdb.firebaseio.com'
    })
    ref_users = db.reference('users')
    ref_config = db.reference('config')
except Exception as e:
    print(f"Firebase Error: {e}")

# --- DATABASE SYNC FUNCTIONS ---
def load_data():
    data = ref_users.get()
    return data if data else {}

def save_user_to_db(user_id, user_data):
    ref_users.child(str(user_id)).set(user_data)

def load_config():
    default_config = {
        "welcome_bonus": 1.0,
        "referral_bonus": 1.0,
        "view_price": 2.0,
        "view_count": "500",
        "channel_username": "@shuvo_bhai11"
    }
    data = ref_config.get()
    if not data:
        ref_config.set(default_config)
        return default_config
    return data

def save_config(config):
    ref_config.set(config)

bot_config = load_config()
bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")

# --- HELPER FUNCTIONS ---
def get_user_data(user_id):
    user_id = str(user_id)
    all_users = load_data()
    if user_id not in all_users:
        new_user = {
            'coins': bot_config['welcome_bonus'],
            'referred_by': None,
            'referred_count': 0,
            'orders': 0,
            'pending_order': False,
            'joined_at': datetime.now().strftime("%d %b, %Y")
        }
        save_user_to_db(user_id, new_user)
        return new_user
    return all_users[user_id]

def is_user_joined(user_id):
    try:
        # এখানে আপনার ২ টি চ্যানেলের আইডি
        ch1 = "@TikTokAutoViews15"
        ch2 = "@shuvo_bhai11"
        
        member1 = bot.get_chat_member(ch1, user_id)
        member2 = bot.get_chat_member(ch2, user_id)
        
        status_list = ['member', 'administrator', 'creator']
        
        if member1.status in status_list and member2.status in status_list:
            return True
        else:
            return False
    except Exception:
        return False
    
# --- USER COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    if not is_user_joined(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📢 𝙅𝙤𝙞𝙣 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 1", url="https://t.me/TikTokAutoViews15")
        btn2 = types.InlineKeyboardButton("📢 𝙅𝙤𝙞𝙣 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 2", url="https://t.me/shuvo_bhai11")
        check_btn = types.InlineKeyboardButton("🔄 𝙑𝙚𝙧𝙞𝙛𝙮 𝙈𝙚𝙢𝙗𝙚𝙧𝙨𝙝𝙞𝙥", callback_data="check_join")
        
        markup.add(btn1, btn2)
        markup.add(check_btn)
        
        welcome_join_text = (
            f"👋 *আসসালামু আলাইকুম, {first_name}!*\n\n"
            "✨ *TikTok Boost Premium* এ আপনাকে স্বাগতম।\n"
            "আমাদের সার্ভিসগুলো ব্যবহার করতে আপনাকে অবশ্যই নিচের দুটি চ্যানেলে জয়েন থাকতে হবে।\n\n"
            "⚠️ *বিঃদ্রঃ জয়েন না থাকলে অর্ডার সাবমিট হবে না!*"
        )
        bot.send_message(message.chat.id, welcome_join_text, reply_markup=markup)
        return

    user_id_str = str(user_id)
    all_users = load_data()
    is_new = user_id_str not in all_users
    args = message.text.split()
    
    user_data = get_user_data(user_id_str)
    
    if is_new:
        bot.send_message(message.chat.id, f"🎊 *𝖢𝗈𝗇𝗀𝗋𝖺𝗍𝗎𝗅𝖺𝗍𝗂𝗈𝗇𝗌!*\n\nআপনি স্বাগতম বোনাস হিসেবে `{bot_config['welcome_bonus']}` 𝖢𝗈𝗂𝗇 পেয়েছেন।")
        if len(args) > 1:
            referrer_id = args[1]
            if referrer_id != user_id_str and referrer_id in all_users:
                ref_data = all_users[referrer_id]
                ref_data['coins'] += bot_config['referral_bonus']
                ref_data['referred_count'] += 1
                save_user_to_db(referrer_id, ref_data)
                
                user_data['referred_by'] = referrer_id
                save_user_to_db(user_id_str, user_data)
                
                try:
                    bot.send_message(referrer_id, f"🥳 *𝙉𝙚𝙬 𝙍𝙚𝙛𝙚𝙧𝙧𝙖𝙡 𝙎𝙪𝙘𝙘𝙚𝙨𝙨!* \n\nআপনার লিঙ্কে ক্লিক করে {first_name} জয়েন করেছে। আপনি পেয়েছেন +{bot_config['referral_bonus']} 𝖢𝗈𝗂𝗇!")
                except:
                    pass

    main_menu(message.chat.id, first_name)

def main_menu(chat_id, first_name):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👤 𝖬𝗒 𝖯𝗋𝗈𝖿𝗂𝗅𝖾", "🔗 𝖱𝖾𝖿𝖾𝗋 & 𝖤𝖺𝗋𝗇")
    markup.add("🚀 𝖮𝗋𝖽𝖾𝗋 𝖵𝗂𝖾𝗐𝗌", "📊 𝖡𝗈𝗍 𝖲𝗍𝖺𝗍𝗌")
    markup.add("🛠 𝖧𝖾𝗅𝗉 & 𝖲𝗎𝗉𝗉𝗈𝗋𝗍")
    
    welcome_text = (
        f"👑 *𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖣𝖺𝗌𝗁𝖻𝗈𝖺𝗋𝖽*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 হ্যালো *{first_name}*, আপনার কি সার্ভিস প্রয়োজন?\n"
        "নিচের মেনু থেকে আপনার কাঙ্ক্ষিত অপশনটি বেছে নিন।\n\n"
        f"💰 *𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖡𝖺𝗅𝖺𝗇𝖼𝖾:* `{get_user_data(chat_id)['coins']}` 𝖢𝗈𝗂𝗇𝗌\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    if is_user_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ ভেরিফিকেশন সফল হয়েছে!", show_alert=False)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "⚠️ আপনি এখনো জয়েন করেননি!", show_alert=True)

@bot.message_handler(func=lambda message: not is_user_joined(message.from_user.id))
def force_join_protection(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📢 𝙅𝙤𝙞𝙣 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 1", url="https://t.me/Trader_Shuvo99")
    btn2 = types.InlineKeyboardButton("📢 𝙅𝙤𝙞𝙣 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 2", url="https://t.me/shuvo_bhai11")
    check_btn = types.InlineKeyboardButton("🔄 𝙑𝙚𝙧𝙞𝙛𝙮 𝙈𝙚𝙢𝙗𝙚𝙧𝙨𝙝𝙞𝙥", callback_data="check_join")
    
    markup.add(btn1, btn2)
    markup.add(check_btn)
    bot.send_message(message.chat.id, "🚫 *অ্যাক্সেস ব্লক করা হয়েছে!*\n\nবটটি ব্যবহার করতে চাইলে আমাদের দুটি চ্যানেলেই জয়েন থাকতে হবে।", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👤 𝖬𝗒 𝖯𝗋𝗈𝖿𝗂𝗅𝖾")
def profile(message):
    data = get_user_data(message.from_user.id)
    profile_text = (
        "💎 *𝖴𝖲𝖤𝖱 𝖯𝖱𝖤𝖬𝖨𝖴𝖬 𝖨𝖭𝖥𝖮*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *𝖭𝖺𝗆𝖾:* {message.from_user.first_name}\n"
        f"🆔 *𝖴𝗌𝖾𝗋 𝖨𝖣:* `{message.from_user.id}`\n\n"
        f"💵 *𝖶𝖺𝗅𝗅𝖾𝗍 𝖡𝖺𝗅𝖺𝗇𝖼𝖾:* `{data['coins']}` 𝖢𝗈𝗂𝗇𝗌\n"
        f"👥 *𝖳𝗈𝗍𝖺𝗅 𝖱𝖾𝖿𝖾𝗋𝗋𝖾𝖽:* `{data['referred_count']}` 𝖴𝗌𝖾𝗋𝗌\n"
        f"📦 *𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝖽 𝖮𝗋𝖽𝖾𝗋𝗌:* `{data.get('orders', 0)}` \n"
        f"📅 *𝖱𝖾𝗀𝗂𝗌𝗍𝖾𝗋𝖾𝖽 𝖣𝖺𝗍𝖾:* {data.get('joined_at', 'N/A')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, profile_text)

@bot.message_handler(func=lambda message: message.text == "🔗 𝖱𝖾𝖿𝖾𝗋 & 𝖤𝖺𝗋𝗇")
def referral(message):
    user_id = str(message.from_user.id)
    bot_username = bot.get_me().username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    ref_text = (
        "📢 *𝙍𝙀𝙁𝙀𝙍𝙍𝘼𝙇 𝙋𝙍𝙊𝙂𝙍𝘼𝙈*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "বন্ধুদের ইনভাইট করুন এবং ফ্রিতে কয়েন আয় করুন!\n\n"
        f"🔗 *𝙔𝙤𝙪𝙧 𝙇𝙞𝙣𝙠:* \n`{ref_link}`\n\n"
        f"🎁 *𝖱𝖾𝗐𝖺𝗋𝖽:* প্রতি সফল রেফারে {bot_config['referral_bonus']} কয়েন।\n"
        f"🛒 *𝖤𝗑𝖼𝗁𝖺𝗇𝗀𝖾:* {bot_config['view_price']} 𝖢𝗈𝗂𝗇𝗌 = {bot_config['view_count']} 𝖵𝗂𝖾𝗐𝗌\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, ref_text)

@bot.message_handler(func=lambda message: message.text == "🚀 𝖮𝗋𝖽𝖾𝗋 𝖵𝗂𝖾𝗐𝗌")
def order_view(message):
    user_id = str(message.from_user.id)
    data = get_user_data(user_id)
    
    if data.get('pending_order', False):
        bot.reply_to(message, "⚠️ *দুঃখিত!* আপনার একটি অর্ডার বর্তমানে রিভিউতে আছে।\n\nসেই অর্ডারটি সম্পন্ন (Accept) বা বাতিল (Reject) না হওয়া পর্যন্ত আপনি নতুন অর্ডার করতে পারবেন না।")
        return

    if data['coins'] >= bot_config['view_price']:
        order_text = (
            "🚀 *𝙋𝙡𝙖𝙘𝙚 𝙔𝙤𝙪𝙧 𝙊𝙧𝙙𝙚𝙧*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *𝖢𝗈𝗌𝗍:* {bot_config['view_price']} 𝖢𝗈𝗂𝗇𝗌\n"
            f"📊 *𝖡𝖾𝗇𝖾𝖿𝗂𝗍:* {bot_config['view_count']} 𝖳𝗂𝗄 Tok 𝖵𝗂𝖾𝗐𝗌\n\n"
            "💬 আপনার 𝖳𝗂𝗄tok ভিডিওর লিঙ্কটি নিচে পেস্ট করুন:"
        )
        msg = bot.reply_to(message, order_text)
        bot.register_next_step_handler(msg, process_order)
    else:
        bot.reply_to(message, f"⚠️ *ব্যালেন্স অপর্যাপ্ত!*\n\nঅর্ডার করতে কমপক্ষে *{bot_config['view_price']} 𝖢𝗈𝗂𝗇𝗌* প্রয়োজন।")

def process_order(message):
    user_id = str(message.from_user.id)
    video_link = message.text
    data = get_user_data(user_id)
    
    if "tiktok.com" in video_link.lower():
        data['coins'] -= bot_config['view_price']
        data['orders'] = data.get('orders', 0) + 1
        data['pending_order'] = True
        save_user_to_db(user_id, data)
        
        success_msg = (
            "✨ *𝙊𝙍𝘿𝙀𝙍 𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇𝙇𝙔 𝙋𝙇𝘼𝘾𝙀𝘿!* ✨\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ আপনার ভিউ অর্ডারটি সফলভাবে জমা হয়েছে।\n"
            "⏳ আমাদের অ্যাডমিন আপনার লিঙ্কটি যাচাই করছে।\n\n"
            "🚀 *খুব শীঘ্রই আপনার কাজ শুরু হবে, ধৈর্য ধরুন!*"
        )
        bot.reply_to(message, success_msg)
        
        markup = types.InlineKeyboardMarkup()
        btn_accept = types.InlineKeyboardButton("✅ 𝖠𝖼𝖼𝖾𝗉𝗍", callback_data=f"ord_acc_{user_id}")
        btn_reject = types.InlineKeyboardButton("❌ 𝖱𝖾𝗃𝖾𝖼𝗍", callback_data=f"ord_rej_{user_id}")
        markup.add(btn_accept, btn_reject)

        admin_msg = (
            "🔥 *𝙉𝙀𝙒 𝙊𝙍𝘿𝙀𝙍 𝙍𝙀𝘾𝙀𝙄𝙑𝙀𝘿*\n\n"
            f"👤 *𝖴𝗌𝖾r:* {message.from_user.first_name}\n"
            f"🆔 *𝖨𝖣:* `{user_id}`\n"
            f"🔗 *𝙇𝙞𝙣𝙠:* {video_link}\n"
            f"📦 *𝙎𝙚𝙧𝙫𝙞𝙘𝙚:* {bot_config['view_count']} 𝖵𝗂𝖾𝗐𝗌\n"
        )
        bot.send_message(ADMIN_ID, admin_msg, reply_markup=markup)

        group_msg = (
            "🚀 *𝙉𝙀𝙒 𝙊𝙍𝘿𝙀𝙍 𝙋𝙇𝘼𝘾𝙀𝘿*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 *𝖢𝗎𝗌𝗍𝗈𝗆𝖾r์:* {message.from_user.first_name}\n"
            f"📦 *𝖰𝗎𝖺𝗇𝗍𝗂𝗍𝗒:* {bot_config['view_count']} 𝖵𝗂𝖾𝗐𝗌\n"
            f"⏳ *𝖲𝗍𝖺𝗍𝗎𝗌:* 𝖯𝖾𝗇𝖽𝗂𝗇𝗀 𝖱𝖾𝗏𝗂𝖾𝗐"
        )
        try:
            bot.send_message(LOG_GROUP_ID, group_msg, disable_web_page_preview=True)
        except: pass
    else:
        bot.reply_to(message, "❌ *𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖫𝗂𝗇k!* \n\nদয়া করে সঠিক 𝖳𝗂𝗄 Tok লিঙ্ক দিন।")

@bot.message_handler(func=lambda message: message.text == "🛠 𝖧𝖾𝗅𝗉 & 𝖲𝗎𝗉𝗉𝗈𝗋𝗍")
def help_command(message):
    help_text = (
        "🛠 *𝙎𝙐𝙋𝙋𝙊𝙍𝙏 𝙂𝙐𝙄𝘿𝙀𝙇𝙄𝙉𝙀*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "❓ *কিভাবে কয়েন আয় করব?*\n"
        "আপনার রেফার লিঙ্ক শেয়ার করুন। প্রতি সফল জয়েনে কয়েন পাবেন।\n\n"
        "❓ *ডেলিভারি টাইম কত?*\n"
        "সাধারণত ১-১২ ঘণ্টার মধ্যে অর্ডার সম্পন্ন হয়।\n\n"
        "❓ *লিঙ্ক ভুল দিলে কি হবে?*\n"
        "ভুল লিঙ্ক দিলে অর্ডার রিজেক্ট হবে এবং কয়েন ফেরত দেওয়া হবে।"
    )
    bot.reply_to(message, help_text)

@bot.message_handler(func=lambda message: message.text == "📊 𝖡𝗈𝗍 𝖲𝗍𝖺𝗍𝗌")
def status(message):
    all_users = load_data()
    total_users = len(all_users)
    stat_text = (
        "📊 *𝙎𝙔𝙎𝙏𝙀𝙈 𝙇𝙄𝙑𝙀 𝙎𝙏𝘼𝙏𝙄𝙎𝙏𝙄𝘾𝙎*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *𝖠𝖼𝗍𝗂𝗏𝖾 𝖴𝗌𝖾𝗋𝗌:* {total_users}\n"
        "⚡ *𝖲𝖾𝗋𝗏𝖾r:* 𝖮𝗇𝗅𝗂𝗇𝖾 (𝖧𝗂𝗀𝗁 𝖲𝗉𝖾𝖾𝖽)\n"
        "✅ *𝖲𝖾𝗋𝗏𝗂𝖼𝖾:* 𝖠𝖼𝗍𝗂𝗏𝖾 (𝟤𝟦/𝟩)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    bot.reply_to(message, stat_text)

# ================= ADMIN PANEL LOGIC =================

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💰 ব্যালেন্স যোগ", callback_data="adm_add_bal")
    btn2 = types.InlineKeyboardButton("➖ ব্যালেন্স রিমুভ", callback_data="adm_rem_bal")
    btn3 = types.InlineKeyboardButton("⚙️ সেটিংস পরিবর্তন", callback_data="adm_settings")
    btn4 = types.InlineKeyboardButton("📢 ব্রডকাস্টিং", callback_data="adm_broadcast")
    btn5 = types.InlineKeyboardButton("📊 তথ্য", callback_data="adm_info")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(ADMIN_ID, "🛠 *WELCOME TO ADMIN PANEL*\nনিচের অপশনগুলো ব্যবহার করুন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('adm_'))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    
    action = call.data
    
    if action == "adm_add_bal":
        msg = bot.send_message(ADMIN_ID, "ইউজারের ID এবং কত কয়েন যোগ করবেন তা এভাবে দিন:\n`USER_ID AMOUNT`\n\nউদাহরণ: `7596820363 10`")
        bot.register_next_step_handler(msg, process_add_balance)
        
    elif action == "adm_rem_bal":
        msg = bot.send_message(ADMIN_ID, "ইউজারের ID এবং কত কয়েন কাটবেন তা এভাবে দিন:\n`USER_ID AMOUNT`\n\nউদাহরণ: `7596820363 5`")
        bot.register_next_step_handler(msg, process_rem_balance)
        
    elif action == "adm_broadcast":
        msg = bot.send_message(ADMIN_ID, "আপনার ব্রডকাস্ট মেসেজটি লিখুন:")
        bot.register_next_step_handler(msg, process_broadcast)
        
    elif action == "adm_info":
        all_users = load_data()
        info = (
            "📊 *বট ইনফরমেশন*\n"
            f"মোট ইউজার: {len(all_users)}\n"
            f"ওয়েলকাম বোনাস: {bot_config['welcome_bonus']}\n"
            f"রেফার বোনাস: {bot_config['referral_bonus']}\n"
            f"ভিউ প্রাইজ: {bot_config['view_price']}\n"
            f"ভিউ কাউন্ট: {bot_config['view_count']}\n"
            f"চ্যানেল: {bot_config['channel_username']}"
        )
        bot.send_message(ADMIN_ID, info)
        
    elif action == "adm_settings":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Welcome Bonus", callback_data="set_welcome_bonus"))
        markup.add(types.InlineKeyboardButton("Refer Bonus", callback_data="set_referral_bonus"))
        markup.add(types.InlineKeyboardButton("View Price", callback_data="set_view_price"))
        markup.add(types.InlineKeyboardButton("View Count", callback_data="set_view_count"))
        markup.add(types.InlineKeyboardButton("Channel Username", callback_data="set_channel_username"))
        bot.send_message(ADMIN_ID, "কোনটি পরিবর্তন করতে চান?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_'))
def setting_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    key = call.data.replace('set_', '')
    msg = bot.send_message(ADMIN_ID, f"নতুন ভ্যালু দিন ({key} এর জন্য):")
    bot.register_next_step_handler(msg, lambda m: save_new_setting(m, key))

def save_new_setting(message, key):
    val = message.text
    if key in ['welcome_bonus', 'referral_bonus', 'view_price']:
        try: val = float(val)
        except: return bot.send_message(ADMIN_ID, "ভুল ইনপুট! নাম্বার দিন।")
    
    bot_config[key] = val
    save_config(bot_config)
    bot.send_message(ADMIN_ID, f"✅ {key} সফলভাবে আপডেট হয়েছে!")

def process_add_balance(message):
    try:
        uid, amt = message.text.split()
        user_data = get_user_data(uid)
        if user_data:
            user_data['coins'] += float(amt)
            save_user_to_db(uid, user_data)
            bot.send_message(ADMIN_ID, f"✅ ইউজার `{uid}` এ {amt} কয়েন যোগ করা হয়েছে।")
            bot.send_message(uid, f"🎁 অ্যাডমিন আপনার ওয়ালেটে `{amt}` কয়েন যোগ করেছে!")
        else:
            bot.send_message(ADMIN_ID, "❌ ইউজার খুঁজে পাওয়া যায়নি।")
    except:
        bot.send_message(ADMIN_ID, "❌ ভুল ফরম্যাট।")

def process_rem_balance(message):
    try:
        uid, amt = message.text.split()
        user_data = get_user_data(uid)
        if user_data:
            user_data['coins'] -= float(amt)
            save_user_to_db(uid, user_data)
            bot.send_message(ADMIN_ID, f"✅ ইউজার `{uid}` থেকে {amt} কয়েন কাটা হয়েছে।")
        else:
            bot.send_message(ADMIN_ID, "❌ ইউজার খুঁজে পাওয়া যায়নি।")
    except:
        bot.send_message(ADMIN_ID, "❌ ভুল ফরম্যাট।")

def process_broadcast(message):
    count = 0
    text = message.text
    all_users = load_data()
    for uid in all_users:
        try:
            bot.send_message(uid, text)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"📢 ব্রডকাস্ট শেষ! মোট {count} জন ইউজার মেসেজ পেয়েছে।")

# --- ORDER HANDLING FOR ADMIN ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('ord_'))
def handle_order_decision(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data.split('_')[1]
    target_user_id = call.data.split('_')[2]
    user_data = get_user_data(target_user_id)

    if action == "acc":
        if user_data:
            user_data['pending_order'] = False
            save_user_to_db(target_user_id, user_data)
            
        bot.edit_message_text(f"✅ *Order Accepted!*\nUser: `{target_user_id}`", ADMIN_ID, call.message.message_id)
        
        user_approve_msg = (
            "🎊 *𝘾𝙊𝙉𝙂𝙍𝘼𝙏𝙐𝙇𝘼𝙏𝙄𝙊𝙉𝙎! 𝙊𝙍𝘿𝙀𝙍 𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿* 🎊\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ আপনার অর্ডারটি অ্যাডমিন এপ্রুভ করেছে।\n"
            "📈 কিছুক্ষণের মধ্যেই আপনার ভিডিওতে ভিউ আসা শুরু হবে।\n\n"
            "✨ *আমাদের সাথে থাকার জন্য ধন্যবাদ!*"
        )
        
        premium_log = (
            "✨ *𝙊𝙍𝘿𝙀𝙍 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀𝘿* ✨\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *𝖢𝗎𝗌𝗍𝗈𝗆𝖾𝗋:* `{target_user_id}`\n"
            f"📦 *𝖲𝖾𝗋𝗏𝗂𝖼𝖾:* {bot_config['view_count']} 𝖳𝗂𝗄Tok 𝖵𝗂𝖾𝗐𝗌\n"
            "✅ *𝙎𝙩𝙖𝙩𝙪𝙨:* 𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮 𝘿𝙚𝙡𝙞𝙫𝙚𝙧𝙚𝙙\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        
        try:
            bot.send_message(target_user_id, user_approve_msg)
            bot.send_message(LOG_GROUP_ID, premium_log)
        except: pass
            
    elif action == "rej":
        if user_data:
            user_data['coins'] += bot_config['view_price']
            user_data['pending_order'] = False
            save_user_to_db(target_user_id, user_data)
            
            bot.edit_message_text(f"❌ *Order Rejected*\nUser: `{target_user_id}` (Refunded)", ADMIN_ID, call.message.message_id)
            
            try:
                bot.send_message(target_user_id, "❌ *Order Cancelled:* আপনার লিঙ্কটি সঠিক ছিল না। কয়েন রিফান্ড করা হয়েছে। আপনি এখন পুনরায় নতুন অর্ডার করতে পারেন।")
                bot.send_message(LOG_GROUP_ID, f"❌ *Rejected:* 𝖴𝗌𝖾𝗋 `{target_user_id}` এর অর্ডারটি বাতিল ও কয়েন রিফান্ড করা হয়েছে।")
            except: pass

# --- START BOT ---
print("--- [ TikTok Boost Premium Bot is Live with Firebase ] ---")
bot.infinity_polling()
