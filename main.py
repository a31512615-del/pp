import discord
from discord.ext import commands
import os
import sys
from threading import Thread
from flask import Flask

# ==============================
# 🔹 إعداد Flask لإرضاء Render 🔹
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Discord bot is running on Render!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==============================
# 🔹 كود البوت الأصلي 🔹
# ==============================
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import TOKEN, EMBED_COLOR


class CustomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.dm_messages = True
        intents.message_content = True
        
        super().__init__(command_prefix="!", intents=intents)
        self.embed_color = EMBED_COLOR
        self.stats = {
            "add_profile": 0,
            "add_image": 0,
            "add_banner": 0,
            "add_pair": 0,
        }

    async def on_ready(self):
        print(f'✅ Logged in as {self.user} (ID: {self.user.id})')
        streaming_url = "https://www.twitch.tv/discord"
        activity = discord.Streaming(name="استقبال طلبات النشر", url=streaming_url)
        await self.change_presence(activity=activity)
        
        await self.load_extensions()
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

    async def load_extensions(self):
        cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_path):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"Loaded extension: {filename[:-3]}")
                except Exception as e:
                    print(f"Failed to load extension {filename[:-3]}: {e}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("<:1_:1433501793249394870> ليس لديك الصلاحيات الكافية لاستخدام هذا الأمر.")
        else:
            print(f"Ignoring exception in command {ctx.command}: {error}")
            await ctx.send(f"<:1_:1433501793249394870> حدث خطأ غير متوقع: {error}")


def run_bot():
    if TOKEN is None:
        print("Error: TOKEN environment variable is not set.")
        return
    bot = CustomBot()
    bot.run(TOKEN)


# ==============================
# 🔹 تشغيل Flask + البوت معًا 🔹
# ==============================
if __name__ == "__main__":
    # نشغّل خادم Flask في Thread منفصل
    Thread(target=run_web_server).start()
    # بعدها نشغل البوت
    run_bot()