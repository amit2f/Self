import os
import asyncio
import json
import random
from pathlib import Path

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ReadHistoryRequest

BASE = Path(__file__).parent
CONFIG_FILE = BASE / "config.json"

DEFAULT_CONFIG = {
    "api_id": 0,
    "api_hash": "",
    "owner_id": 0,
    "bot_token": "",
    "session_name": "selfsaz_session",
    "diamond": 0,
    "settings": {
        "auto_reply": False,
        "auto_seen": False,
        "online": False
    },
    "auto_reply_text": "سلام 👋 پیام شما دریافت شد.",
    "channels": []
}

def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG.copy())
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(data):
    # This file is intentionally simple: no database is required.
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

cfg = load_config()

def env(name, fallback=""):
    value = os.getenv(name)
    return value if value is not None and value != "" else fallback

API_ID = int(env("API_ID", cfg.get("api_id", 0)))
API_HASH = env("API_HASH", cfg.get("api_hash", ""))
OWNER_ID = int(env("OWNER_ID", cfg.get("owner_id", 0)))
BOT_TOKEN = env("BOT_TOKEN", cfg.get("bot_token", ""))
STRING_SESSION = env("STRING_SESSION", "").strip()

if not API_ID or not API_HASH:
    raise RuntimeError("API_ID و API_HASH را در Secrets سرویس قرار بده.")
if not OWNER_ID:
    raise RuntimeError("OWNER_ID را در Secrets سرویس قرار بده.")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN را در Secrets سرویس قرار بده.")

if STRING_SESSION:
    user = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
else:
    user = TelegramClient(cfg.get("session_name", "selfsaz_session"), API_ID, API_HASH)

control = TelegramClient("control_bot", API_ID, API_HASH)

def is_owner(event):
    return event.sender_id == OWNER_ID

def main_menu():
    return [
        [Button.inline("⚙️ مدیریت سلف", b"manage"), Button.inline("👤 حساب", b"account")],
        [Button.inline("💎 الماس", b"diamond"), Button.inline("🎮 بازی", b"game")],
        [Button.inline("🔗 زیرمجموعه", b"ref"), Button.inline("🛟 پشتیبانی", b"support")],
        [Button.inline("📣 کانال‌ها", b"channels"), Button.inline("📊 وضعیت", b"status")],
        [Button.inline("📚 راهنما", b"help")]
    ]

def back():
    return [[Button.inline("🔙 بازگشت", b"home")]]

def bool_icon(v):
    return "🟢 روشن" if v else "🔴 خاموش"

@control.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    if not is_owner(event):
        return
    await event.respond("🤖 پنل SelfSaz\n\nدسترسی کامل برای مالک فعال است.", buttons=main_menu())

@control.on(events.NewMessage(pattern=r"^/help$"))
async def help_cmd(event):
    if not is_owner(event):
        return
    await event.respond(
        "📚 دستورات\n\n"
        "/start — پنل اصلی\n"
        "/diamond add N — افزایش الماس\n"
        "/diamond sub N — کاهش الماس\n"
        "/setname NAME — تغییر نام\n"
        "/setbio TEXT — تغییر بیو\n"
        "/setusername USERNAME — تغییر یوزرنیم\n"
        "/block — ریپلای به پیام و بلاک\n"
        "/unblock — ریپلای و آنبلاک\n"
        "/join CHANNEL — عضویت در کانال عمومی\n"
        "/channels — نمایش کانال‌های تنظیم‌شده\n"
        "/addchannel CHANNEL — افزودن کانال به لیست\n"
        "/delchannel CHANNEL — حذف کانال از لیست\n"
        "/reply TEXT — متن پاسخ خودکار\n"
        "/game — بازی ساده\n"
        "/status — وضعیت سلف\n"
        "/profile — اطلاعات حساب\n"
        "/ping — تست اتصال"
    )

@control.on(events.NewMessage(pattern=r"^/ping$"))
async def ping(event):
    if is_owner(event):
        await event.respond("🏓 Pong — اتصال پنل برقرار است.")

@control.on(events.NewMessage(pattern=r"^/status$"))
async def status_cmd(event):
    if not is_owner(event):
        return
    await event.respond(
        "📊 وضعیت\n\n"
        f"Auto Reply: {bool_icon(cfg['settings']['auto_reply'])}\n"
        f"Auto Seen: {bool_icon(cfg['settings']['auto_seen'])}\n"
        f"Online Mode: {bool_icon(cfg['settings']['online'])}\n"
        f"💎 Diamonds: {cfg.get('diamond', 0)}"
    )

@control.on(events.NewMessage(pattern=r"^/profile$"))
async def profile(event):
    if not is_owner(event):
        return
    me = await user.get_me()
    await event.respond(
        f"👤 پروفایل\n\n"
        f"ID: {me.id}\n"
        f"Username: @{me.username or 'ندارد'}\n"
        f"Name: {me.first_name or ''} {me.last_name or ''}\n"
        f"Phone: {me.phone or 'مخفی'}"
    )

@control.on(events.NewMessage(pattern=r"^/setname\s+(.+)$"))
async def setname(event):
    if not is_owner(event):
        return
    name = event.pattern_match.group(1).strip()
    await user(UpdateProfileRequest(first_name=name))
    await event.respond("✅ نام تغییر کرد.")

@control.on(events.NewMessage(pattern=r"^/setbio\s+(.+)$"))
async def setbio(event):
    if not is_owner(event):
        return
    bio = event.pattern_match.group(1).strip()
    await user(UpdateProfileRequest(about=bio))
    await event.respond("✅ بیو تغییر کرد.")

@control.on(events.NewMessage(pattern=r"^/setusername\s+([A-Za-z0-9_]{5,32})$"))
async def setusername(event):
    if not is_owner(event):
        return
    username = event.pattern_match.group(1)
    try:
        await user(UpdateProfileRequest(username=username))
        await event.respond(f"✅ یوزرنیم به @{username} تغییر کرد.")
    except Exception as e:
        await event.respond(f"❌ تغییر یوزرنیم انجام نشد:\n{type(e).__name__}")

@control.on(events.NewMessage(pattern=r"^/block$"))
async def block(event):
    if not is_owner(event):
        return
    if not event.is_reply:
        await event.respond("روی پیام شخص ریپلای کن و /block بفرست.")
        return
    msg = await event.get_reply_message()
    if msg.sender_id:
        await user(BlockRequest(id=msg.sender_id))
        await event.respond("✅ کاربر بلاک شد.")

@control.on(events.NewMessage(pattern=r"^/unblock$"))
async def unblock(event):
    if not is_owner(event):
        return
    if not event.is_reply:
        await event.respond("روی پیام شخص ریپلای کن و /unblock بفرست.")
        return
    msg = await event.get_reply_message()
    if msg.sender_id:
        await user(UnblockRequest(id=msg.sender_id))
        await event.respond("✅ کاربر آنبلاک شد.")

@control.on(events.NewMessage(pattern=r"^/join\s+(.+)$"))
async def join(event):
    if not is_owner(event):
        return
    channel = event.pattern_match.group(1).strip()
    try:
        await user(JoinChannelRequest(channel))
        await event.respond("✅ عضویت انجام شد.")
    except Exception as e:
        await event.respond(f"❌ عضویت انجام نشد:\n{type(e).__name__}")

@control.on(events.NewMessage(pattern=r"^/addchannel\s+(.+)$"))
async def addchannel(event):
    if not is_owner(event):
        return
    channel = event.pattern_match.group(1).strip()
    channels = cfg.setdefault("channels", [])
    if channel not in channels:
        channels.append(channel)
        save_config(cfg)
    await event.respond("✅ کانال به لیست اضافه شد.")

@control.on(events.NewMessage(pattern=r"^/delchannel\s+(.+)$"))
async def delchannel(event):
    if not is_owner(event):
        return
    channel = event.pattern_match.group(1).strip()
    channels = cfg.setdefault("channels", [])
    if channel in channels:
        channels.remove(channel)
        save_config(cfg)
        await event.respond("✅ حذف شد.")
    else:
        await event.respond("این کانال در لیست نیست.")

@control.on(events.NewMessage(pattern=r"^/channels$"))
async def channels_cmd(event):
    if not is_owner(event):
        return
    channels = cfg.get("channels", [])
    text = "📣 کانال‌ها\n\n" + ("\n".join(channels) if channels else "لیست خالی است.")
    await event.respond(text)

@control.on(events.NewMessage(pattern=r"^/reply\s+(.+)$"))
async def reply_text(event):
    if not is_owner(event):
        return
    cfg["auto_reply_text"] = event.pattern_match.group(1).strip()
    cfg["settings"]["auto_reply"] = True
    save_config(cfg)
    await event.respond("✅ پاسخ خودکار فعال و متن ذخیره شد.")

@control.on(events.NewMessage(pattern=r"^/game$"))
async def game(event):
    if not is_owner(event):
        return
    prize = random.randint(1, 5)
    cfg["diamond"] = cfg.get("diamond", 0) + prize
    save_config(cfg)
    await event.respond(f"🎮 نتیجه بازی: 🎉\nشما {prize} 💎 بردید!\nموجودی: {cfg['diamond']} 💎")

@control.on(events.NewMessage(pattern=r"^/diamond\s+(add|sub)\s+(\d+)$"))
async def diamond(event):
    if not is_owner(event):
        return
    action, raw = event.pattern_match.groups()
    amount = int(raw)
    if action == "add":
        cfg["diamond"] = cfg.get("diamond", 0) + amount
    else:
        cfg["diamond"] = max(0, cfg.get("diamond", 0) - amount)
    save_config(cfg)
    await event.respond(f"💎 موجودی: {cfg['diamond']}")

@control.on(events.NewMessage(pattern=r"^/toggle\s+(reply|seen|online)$"))
async def toggle(event):
    if not is_owner(event):
        return
    key = {"reply": "auto_reply", "seen": "auto_seen", "online": "online"}[event.pattern_match.group(1)]
    cfg["settings"][key] = not cfg["settings"][key]
    save_config(cfg)
    await event.respond(f"✅ {key}: {bool_icon(cfg['settings'][key])}")

@control.on(events.CallbackQuery)
async def callbacks(event):
    if not is_owner(event):
        await event.answer("دسترسی ندارید.", alert=True)
        return
    data = event.data

    if data == b"home":
        await event.edit("🤖 پنل SelfSaz\n\nدسترسی کامل برای مالک فعال است.", buttons=main_menu())
    elif data == b"manage":
        await event.edit(
            "⚙️ مدیریت سلف\n\n"
            f"پاسخ خودکار: {bool_icon(cfg['settings']['auto_reply'])}\n"
            f"سین خودکار: {bool_icon(cfg['settings']['auto_seen'])}\n"
            f"آنلاین: {bool_icon(cfg['settings']['online'])}",
            buttons=[
                [Button.inline("↩️ پاسخ خودکار", b"toggle_reply"), Button.inline("👁 سین", b"toggle_seen")],
                [Button.inline("🟢 آنلاین", b"toggle_online")],
                [Button.inline("🔙 بازگشت", b"home")]
            ]
        )
    elif data == b"account":
        me = await user.get_me()
        await event.edit(
            f"👤 حساب\n\nID: {me.id}\nUsername: @{me.username or 'ندارد'}\nنام: {me.first_name or ''}",
            buttons=back()
        )
    elif data == b"diamond":
        await event.edit(f"💎 موجودی: {cfg.get('diamond', 0)}", buttons=back())
    elif data == b"game":
        prize = random.randint(1, 5)
        cfg["diamond"] = cfg.get("diamond", 0) + prize
        save_config(cfg)
        await event.edit(f"🎮 بردی! +{prize} 💎\nموجودی: {cfg['diamond']}", buttons=back())
    elif data == b"ref":
        await event.edit("🔗 زیرمجموعه\n\nبرای جلوگیری از نیاز به دیتابیس، این نسخه لینک/آمار دائمی زیرمجموعه را ذخیره نمی‌کند.", buttons=back())
    elif data == b"support":
        await event.edit("🛟 پشتیبانی\n\nاین پنل فقط برای مالک فعال است. می‌توانی پیام‌های پشتیبانی را از طریق حساب تلگرام مدیریت کنی.", buttons=back())
    elif data == b"channels":
        channels = cfg.get("channels", [])
        await event.edit("📣 کانال‌ها\n\n" + ("\n".join(channels) if channels else "لیست خالی است."), buttons=back())
    elif data == b"status":
        await event.edit(
            f"📊 وضعیت\n\n"
            f"Reply: {bool_icon(cfg['settings']['auto_reply'])}\n"
            f"Seen: {bool_icon(cfg['settings']['auto_seen'])}\n"
            f"Online: {bool_icon(cfg['settings']['online'])}\n"
            f"Diamonds: {cfg.get('diamond', 0)}",
            buttons=back()
        )
    elif data == b"help":
        await event.edit(
            "📚 راهنما\n\n"
            "/diamond add N\n"
            "/diamond sub N\n"
            "/setname NAME\n"
            "/setbio TEXT\n"
            "/setusername USERNAME\n"
            "/block و /unblock روی ریپلای\n"
            "/join CHANNEL\n"
            "/reply TEXT\n"
            "/game\n"
            "/status\n"
            "/profile",
            buttons=back()
        )
    elif data in (b"toggle_reply", b"toggle_seen", b"toggle_online"):
        key = {
            b"toggle_reply": "auto_reply",
            b"toggle_seen": "auto_seen",
            b"toggle_online": "online"
        }[data]
        cfg["settings"][key] = not cfg["settings"][key]
        save_config(cfg)
        await event.answer(f"{bool_icon(cfg['settings'][key])}")
        await event.edit(
            "⚙️ مدیریت سلف\n\n"
            f"پاسخ خودکار: {bool_icon(cfg['settings']['auto_reply'])}\n"
            f"سین خودکار: {bool_icon(cfg['settings']['auto_seen'])}\n"
            f"آنلاین: {bool_icon(cfg['settings']['online'])}",
            buttons=[
                [Button.inline("↩️ پاسخ خودکار", b"toggle_reply"), Button.inline("👁 سین", b"toggle_seen")],
                [Button.inline("🟢 آنلاین", b"toggle_online")],
                [Button.inline("🔙 بازگشت", b"home")]
            ]
        )

# Personal-account features. These respond only to normal incoming messages
# and never mass-message or spam other users.
@user.on(events.NewMessage(incoming=True))
async def personal_features(event):
    if event.sender_id == OWNER_ID:
        return

    if cfg["settings"].get("auto_seen"):
        try:
            await user(ReadHistoryRequest(peer=event.chat_id, max_id=event.id))
        except Exception:
            pass

    if cfg["settings"].get("auto_reply"):
        try:
            await event.reply(cfg.get("auto_reply_text", "سلام 👋 پیام شما دریافت شد."))
        except Exception:
            pass

async def main():
    if STRING_SESSION:
        await user.connect()
        if not await user.is_user_authorized():
            raise RuntimeError("STRING_SESSION معتبر نیست.")
    else:
        await user.start()

    print("User session connected.")
    await control.start(bot_token=BOT_TOKEN)
    print("Control bot connected.")
    await asyncio.gather(
        user.run_until_disconnected(),
        control.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
