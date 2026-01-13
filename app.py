import os, asyncio, time
from pyrogram import Client, filters
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import yt_dlp

# --- CONFIGURATION ---
BOT_TOKEN = "7256694280:AAFlMK9szh2mPlucr2YJIkc3vIBKHbkcWgs"
API_ID = 22679198
API_HASH = "f5200cf837447cc1a8e0e60176fefff7"
CHANNEL_ID = -1002065320793

app = Client("bot_final", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_video_link(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Sur Koyeb, Selenium trouvera Chrome tout seul
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(10) # Laisse le temps au site de charger
        iframes = driver.find_elements("tag name", "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and any(x in src for x in ["lulu", "vidoza", "mycloud"]):
                return src
        return None
    finally:
        driver.quit()

@app.on_message(filters.private & filters.text)
async def handle_message(client, message):
    if "http" in message.text:
        msg = await message.reply("📡 **Analyse en cours sur le serveur...**")
        loop = asyncio.get_event_loop()
        link = await loop.run_in_executor(None, get_video_link, message.text)
        
        if link:
            await msg.edit(f"✅ Lecteur trouvé : `{link}`\nEnvoi au canal...")
            try:
                with yt_dlp.YoutubeDL({'outtmpl': 'video.mp4'}) as ydl:
                    ydl.download([link])
                await client.send_video(CHANNEL_ID, "video.mp4")
                os.remove("video.mp4")
            except Exception as e:
                await msg.edit(f"❌ Erreur : {e}")
        else:
            await msg.edit("❌ Impossible de trouver la vidéo.")
    else:
        await message.reply("Envoie-moi un lien d'épisode !")

app.run()
