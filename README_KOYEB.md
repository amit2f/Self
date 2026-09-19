# SelfSaz — GitHub → Koyeb

## 1) GitHub
محتویات این پوشه را مستقیماً در ریشه Repository آپلود کن؛ یعنی `main.py` باید در صفحه اصلی Repository دیده شود.

## 2) Koyeb Secrets
این موارد را به عنوان Environment Variables/Secrets اضافه کن:
- API_ID
- API_HASH
- OWNER_ID
- BOT_TOKEN
- STRING_SESSION

مقدار واقعی API_HASH و STRING_SESSION را داخل GitHub قرار نده.

## 3) Deploy
Repository را به Koyeb وصل کن و سرویس را به صورت Worker اجرا کن.
Dockerfile موجود است؛ Koyeb می‌تواند آن را برای Build استفاده کند.

## 4) نکته ذخیره‌سازی
این نسخه دیتابیس ندارد. تنظیمات ساده در `config.json` ذخیره می‌شوند. روی سرویس‌های ابری بدون دیسک پایدار، تغییرات فایل ممکن است بعد از Redeploy/تعویض ماشین باقی نمانند.

## امکانات
پنل مالک، مدیریت تنظیمات پاسخ خودکار/سین، پروفایل، تغییر نام/بیو/یوزرنیم، بلاک/آنبلاک، عضویت در کانال، مدیریت لیست کانال‌ها، الماس، بازی ساده، وضعیت و راهنما.
