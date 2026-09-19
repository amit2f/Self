# SelfSaz - single file Replit version
# فقط همین فایل لازم است. در Replit Secrets این موارد را قرار بده:
# API_ID, API_HASH, OWNER_ID, BOT_TOKEN
#
# اجرای اول:
# python main.py
# Telethon شماره، کد ورود و در صورت فعال بودن 2FA را در Shell می‌گیرد.
# فایل Session کنار همین فایل ساخته می‌شود و در اجراهای بعدی استفاده می‌شود.

import os
import sys
import subprocess
import asyncio
import json
import random
from pathlib import Path

# نصب خودکار Telethon، بنابراین requirements.txt لازم نیست.
try:
    from telethon import TelegramClient, events, Button
    from telethon.tl.functions.account import UpdateProfileRequest
    from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.tl.functions.messages import ReadHistoryRequest
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "telethon>=1.42,<2"])
    from telethon import TelegramClient, events, Button
    from telethon.tl.functions.account import UpdateProfileRequest
    from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.tl.functions.messages import ReadHistoryRequest

BASE = Path(__file__).resolve().parent
CONFIG_FILE = BASE / "selfsaz_config.json"

def get_env(name, default=""):
    value = os.getenv(name)
    return value if value not in (None, "") else default

def load_config():
    default = {
        "diamond": 0,
        "auto_reply": False,
        "auto_seen": False,
        "online": False,
        "auto_reply_text": "سلام 👋 پیام شما دریافت شد.",
        "channels": []
    }
    try:
        if CONFIG_FILE.exists():
            default.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    except Exception:
        pass
    return default

cfg = load_config()

def save_config():
    try:
        CONFIG_FILE.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print("Config save warning:", e)

try:
    API_ID = int(get_env("API_ID"))
    API_HASH = get_env("API_HASH")
    OWNER_ID = int(get_env("OWNER_ID"))
    BOT_TOKEN = get_env("BOT_TOKEN")
except Exception:
    raise SystemExit("Secrets را درست تنظیم کن: API_ID / API_HASH / OWNER_ID / BOT_TOKEN")

if not API_ID or not API_HASH or not OWNER_ID or not BOT_TOKEN:
    raise SystemExit("چهار Secret لازم است: API_ID, API_HASH, OWNER_ID, BOT_TOKEN")

# بدون STRING_SESSION
user = TelegramClient("selfsaz_session", API_ID, API_HASH)
control = TelegramClient("selfsaz_control", API_ID, API_HASH)

def owner(event):
    return event.sender_id == OWNER_ID

def icon(value):
    return "🟢 روشن" if value else "🔴 خاموش"

def menu():
    return [
        [Button.inline("👤 حساب", b"account"), Button.inline("⚙️ مدیریت", b"manage")],
        [Button.inline("💎 الماس", b"diamond"), Button.inline("🎮 بازی", b"game")],
        [Button.inline("📣 کانال‌ها", b"channels"), Button.inline("📊 وضعیت", b"status")],
        [Button.inline("📚 راهنما", b"help")]
    ]

def back():
    return [[Button.inline("🔙 بازگشت", b"home")]]

@control.on(events.NewMessage(pattern=r"^/start$"))
async def start(event):
    if not owner(event): return
    await event.respond("🤖 SelfSaz\n\nپنل شخصی آماده است.", buttons=menu())

@control.on(events.NewMessage(pattern=r"^/ping$"))
async def ping(event):
    if owner(event):
        await event.respond("🏓 Pong")

@control.on(events.NewMessage(pattern=r"^/status$"))
async def status(event):
    if not owner(event): return
    await event.respond(
        f"📊 وضعیت\n\n"
        f"💎 الماس: {cfg['diamond']}\n"
        f"↩️ پاسخ خودکار: {icon(cfg['auto_reply'])}\n"
        f"👁 سین خودکار: {icon(cfg['auto_seen'])}\n"
        f"🟢 آنلاین: {icon(cfg['online'])}"
    )

@control.on(events.NewMessage(pattern=r"^/profile$"))
async def profile(event):
    if not owner(event): return
    me = await user.get_me()
    await event.respond(
        f"👤 حساب\n\nID: {me.id}\n"
        f"Username: @{me.username or 'ندارد'}\n"
        f"Name: {me.first_name or ''} {me.last_name or ''}"
    )

@control.on(events.NewMessage(pattern=r"^/setname\s+(.+)$"))
async def setname(event):
    if not owner(event): return
    await user(UpdateProfileRequest(first_name=event.pattern_match.group(1).strip()))
    await event.respond("✅ نام تغییر کرد.")

@control.on(events.NewMessage(pattern=r"^/setbio\s+(.+)$"))
async def setbio(event):
    if not owner(event): return
    await user(UpdateProfileRequest(about=event.pattern_match.group(1).strip()))
    await event.respond("✅ بیو تغییر کرد.")

@control.on(events.NewMessage(pattern=r"^/setusername\s+([A-Za-z0-9_]{5,32})$"))
async def setusername(event):
    if not owner(event): return
    try:
        username = event.pattern_match.group(1)
        await user(UpdateProfileRequest(username=username))
        await event.respond("✅ یوزرنیم تغییر کرد.")
    except Exception as e:
        await event.respond("❌ تغییر یوزرنیم انجام نشد: " + type(e).__name__)

@control.on(events.NewMessage(pattern=r"^/diamond\s+(add|sub)\s+(\d+)$"))
async def diamond(event):
    if not owner(event): return
    action, amount = event.pattern_match.groups()
    amount = int(amount)
    if action == "add":
        cfg["diamond"] += amount
    else:
        cfg["diamond"] = max(0, cfg["diamond"] - amount)
    save_config()
    await event.respond(f"💎 موجودی: {cfg['diamond']}")

@control.on(events.NewMessage(pattern=r"^/game$"))
async def game(event):
    if not owner(event): return
    prize = random.randint(1, 5)
    cfg["diamond"] += prize
    save_config()
    await event.respond(f"🎮 برنده شدی! +{prize} 💎\nموجودی: {cfg['diamond']}")

@control.on(events.NewMessage(pattern=r"^/reply\s+(.+)$"))
async def reply_cmd(event):
    if not owner(event): return
    cfg["auto_reply_text"] = event.pattern_match.group(1).strip()
    cfg["auto_reply"] = True
    save_config()
    await event.respond("✅ پاسخ خودکار فعال شد.")

@control.on(events.NewMessage(pattern=r"^/toggle\s+(reply|seen|online)$"))
async def toggle(event):
    if not owner(event): return
    key = {"reply":"auto_reply", "seen":"auto_seen", "online":"online"}[
        event.pattern_match.group(1)
    ]
    cfg[key] = not cfg[key]
    save_config()
    await event.respond(f"✅ {key}: {icon(cfg[key])}")

@control.on(events.NewMessage(pattern=r"^/join\s+(.+)$"))
async def join(event):
    if not owner(event): return
    try:
        await user(JoinChannelRequest(event.pattern_match.group(1).strip()))
        await event.respond("✅ عضویت انجام شد.")
    except Exception as e:
        await event.respond("❌ انجام نشد: " + type(e).__name__)

@control.on(events.NewMessage(pattern=r"^/addchannel\s+(.+)$"))
async def addchannel(event):
    if not owner(event): return
    ch = event.pattern_match.group(1).strip()
    if ch not in cfg["channels"]:
        cfg["channels"].append(ch)
        save_config()
    await event.respond("✅ اضافه شد.")

@control.on(events.NewMessage(pattern=r"^/delchannel\s+(.+)$"))
async def delchannel(event):
    if not owner(event): return
    ch = event.pattern_match.group(1).strip()
    if ch in cfg["channels"]:
        cfg["channels"].remove(ch)
        save_config()
        await event.respond("✅ حذف شد.")
    else:
        await event.respond("❌ در لیست نیست.")

@control.on(events.NewMessage(pattern=r"^/channels$"))
async def channels(event):
    if not owner(event): return
    await event.respond("📣 کانال‌ها\n\n" + ("\n".join(cfg["channels"]) if cfg["channels"] else "خالی است."))

@control.on(events.NewMessage(pattern=r"^/block$"))
async def block(event):
    if not owner(event): return
    if not event.is_reply:
        await event.respond("روی پیام شخص ریپلای کن و /block بفرست.")
        return
    msg = await event.get_reply_message()
    if msg.sender_id:
        await user(BlockRequest(id=msg.sender_id))
        await event.respond("✅ بلاک شد.")

@control.on(events.NewMessage(pattern=r"^/unblock$"))
async def unblock(event):
    if not owner(event): return
    if not event.is_reply:
        await event.respond("روی پیام شخص ریپلای کن و /unblock بفرست.")
        return
    msg = await event.get_reply_message()
    if msg.sender_id:
        await user(UnblockRequest(id=msg.sender_id))
        await event.respond("✅ آنبلاک شد.")

@control.on(events.NewMessage(pattern=r"^/help$"))
async def help_cmd(event):
    if not owner(event): return
    await event.respond(
        "📚 دستورات:\n\n"
        "/start\n/ping\n/status\n/profile\n"
        "/diamond add N\n/diamond sub N\n"
        "/game\n/setname NAME\n/setbio TEXT\n"
        "/setusername USERNAME\n/reply TEXT\n"
        "/toggle reply|seen|online\n"
        "/join CHANNEL\n/addchannel CHANNEL\n/delchannel CHANNEL\n"
        "/channels\n/block (روی ریپلای)\n/unblock (روی ریپلای)"
    )

@control.on(events.CallbackQuery)
async def buttons(event):
    if not owner(event):
        await event.answer("دسترسی ندارید.", alert=True)
        return

    d = event.data
    if d == b"home":
        await event.edit("🤖 SelfSaz\n\nپنل شخصی آماده است.", buttons=menu())

    elif d == b"account":
        me = await user.get_me()
        await event.edit(
            f"👤 حساب\n\nID: {me.id}\n"
            f"Username: @{me.username or 'ندارد'}\n"
            f"Name: {me.first_name or ''}",
            buttons=back()
        )

    elif d == b"manage":
        await event.edit(
            f"⚙️ مدیریت\n\n"
            f"↩️ پاسخ: {icon(cfg['auto_reply'])}\n"
            f"👁 سین: {icon(cfg['auto_seen'])}\n"
            f"🟢 آنلاین: {icon(cfg['online'])}",
            buttons=[
                [Button.inline("↩️ پاسخ", b"reply_toggle"),
                 Button.inline("👁 سین", b"seen_toggle")],
                [Button.inline("🟢 آنلاین", b"online_toggle")],
                [Button.inline("🔙 بازگشت", b"home")]
            ]
        )

    elif d == b"diamond":
        await event.edit(f"💎 موجودی: {cfg['diamond']}", buttons=back())

    elif d == b"game":
        prize = random.randint(1, 5)
        cfg["diamond"] += prize
        save_config()
        await event.edit(f"🎮 +{prize} 💎\nموجودی: {cfg['diamond']}", buttons=back())

    elif d == b"channels":
        text = "\n".join(cfg["channels"]) if cfg["channels"] else "لیست خالی است."
        await event.edit("📣 کانال‌ها\n\n" + text, buttons=back())

    elif d == b"status":
        await event.edit(
            f"📊 وضعیت\n\n💎 {cfg['diamond']}\n"
            f"↩️ {icon(cfg['auto_reply'])}\n"
            f"👁 {icon(cfg['auto_seen'])}\n"
            f"🟢 {icon(cfg['online'])}",
            buttons=back()
        )

    elif d == b"help":
        await event.edit("📚 برای لیست کامل دستورات /help را بفرست.", buttons=back())

    elif d in (b"reply_toggle", b"seen_toggle", b"online_toggle"):
        key = {
            b"reply_toggle": "auto_reply",
            b"seen_toggle": "auto_seen",
            b"online_toggle": "online"
        }[d]
        cfg[key] = not cfg[key]
        save_config()
        await event.answer(icon(cfg[key]))
        await event.edit(
            f"⚙️ مدیریت\n\n"
            f"↩️ پاسخ: {icon(cfg['auto_reply'])}\n"
            f"👁 سین: {icon(cfg['auto_seen'])}\n"
            f"🟢 آنلاین: {icon(cfg['online'])}",
            buttons=[
                [Button.inline("↩️ پاسخ", b"reply_toggle"),
                 Button.inline("👁 سین", b"seen_toggle")],
                [Button.inline("🟢 آنلاین", b"online_toggle")],
                [Button.inline("🔙 بازگشت", b"home")]
            ]
        )

@user.on(events.NewMessage(incoming=True))
async def user_messages(event):
    if event.sender_id == OWNER_ID:
        return

    if cfg["auto_seen"]:
        try:
            await user(ReadHistoryRequest(peer=event.chat_id, max_id=event.id))
        except Exception:
            pass

    if cfg["auto_reply"]:
        try:
            await event.reply(cfg["auto_reply_text"])
        except Exception:
            pass

async def main():
    # First run asks for Telegram login details in Replit Shell.
    # Later runs reuse selfsaz_session.session.
    await user.start()
    print("✅ User account connected.")
    await control.start(bot_token=BOT_TOKEN)
    print("✅ Control bot connected.")
    await asyncio.gather(
        user.run_until_disconnected(),
        control.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
