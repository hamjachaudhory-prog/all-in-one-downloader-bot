
import os
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp

# GitHub Secrets বা Environment থেকে কনফিগারেশন নেওয়া
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client("AllInOneDownloaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(
        "👋 স্বাগতম!\n\n"
        "যেকোনো YouTube (Single/Playlist), Facebook, Instagram বা TikTok-এর লিংক দিন, আমি ভিডিও ডাউনলোড করে পাঠিয়ে দেবো। 📥"
    )

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_media(client, message: Message):
    url = message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.reply_text("❌ দয়া করে একটি সঠিক ভিডিও লিংক পাঠান।")
        return

    status_msg = await message.reply_text("⏳ মিডিয়া প্রসেস হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': False,
        'max_downloads': 10,
    }

    try:
        os.makedirs("downloads", exist_ok=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await status_msg.edit_text("🔍 লিংকের তথ্য সংগ্রহ করা হচ্ছে...")
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:
                await status_msg.edit_text(f"📥 প্লেলিস্ট শনাক্ত হয়েছে! মোট ভিডিও: {len(info['entries'])}টি। আপলোড শুরু হচ্ছে...")
                for entry in info['entries']:
                    if entry:
                        file_path = ydl.prepare_filename(entry)
                        if os.path.exists(file_path):
                            await client.send_video(message.chat.id, video=file_path, caption=entry.get('title', 'Video'))
                            os.remove(file_path)
                await status_msg.delete()
            else:
        # একক ভিডিও হলে
                file_path = ydl.prepare_filename(info)
                await status_msg.edit_text("📤 টেলিগ্রামে আপলোড করা হচ্ছে...")
                if os.path.exists(file_path):
                    await client.send_video(message.chat.id, video=file_path, caption=info.get('title', 'Video'))
                    os.remove(file_path)
                    await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ ডাউনলোড করতে সমস্যা হয়েছে:\n`{str(e)}`")

if __name__ == "__main__":
    print("🤖 বট চালু হচ্ছে...")
    app.run()
