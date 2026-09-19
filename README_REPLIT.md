# SelfSaz — Replit (without STRING_SESSION)

## Secrets
Add these Replit Secrets:
- API_ID
- API_HASH
- OWNER_ID
- BOT_TOKEN

`STRING_SESSION` is NOT required.

## First run
Run:
```bash
python main.py
```

Telethon will ask in the Shell for:
1. Telegram phone number
2. Login code sent by Telegram
3. Two-factor password, if enabled

After successful login, a local `selfsaz_session.session` file is created and reused on later runs.

Do not publish the `.session` file to GitHub. It is already excluded by `.gitignore`.

## Important
If the Replit project/storage is reset and the `.session` file is lost, you will need to log in again.
