import discord
from discord.ext import commands
import os
import sys
# إضافة المسار الحالي إلى sys.path للسماح باستيراد config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import TOKEN, EMBED_COLOR

class CustomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.dm_messages = True
        intents.message_content = True
        
        # تغيير command_prefix إلى None والاعتماد على أوامر التطبيق (Slash Commands)
        # يمكن إضافة بادئة أخرى إذا لزم الأمر
        super().__init__(command_prefix="!", intents=intents)
        self.embed_color = EMBED_COLOR
        # إحصائيات استخدام أزرار النشر
        self.stats = {
            "add_profile": 0,
            "add_image": 0,
            "add_banner": 0,
            "add_pair": 0,
        }

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        
        # تعيين حالة البوت إلى Streaming
        streaming_url = "https://www.twitch.tv/discord" # يمكن تغيير الرابط إلى رابط حقيقي إذا لزم الأمر
        activity = discord.Streaming(name="استقبال طلبات النشر", url=streaming_url)
        await self.change_presence(activity=activity)
        
        await self.load_extensions()
        # مزامنة أوامر التطبيق (Slash Commands)
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def load_extensions(self):
        # تحميل cogs
        # يجب أن يكون المسار relative to the current working directory
        cogs_path = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_path):
            if filename.endswith(".py"):
                try:
                    # اسم الوحدة هو cogs.اسم_الملف_بدون_امتداد
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
    # يجب أن يكون المسار relative to the current working directory
    # لتشغيل البوت، يجب أن يكون الكود في مجلد discord_bot
    # سيتم تشغيل البوت من المسار /home/ubuntu/discord_bot
    # لذا يجب أن يكون المسار صحيحاً
    bot.run(TOKEN)

if __name__ == "__main__":
    # لتشغيل الملف بشكل صحيح من أي مكان، يجب تغيير المسار الحالي إلى مجلد البوت
    # ولكن بما أننا في بيئة الساندبوكس، سنفترض أن الملف سيتم تشغيله من /home/ubuntu/discord_bot
    # أو سنقوم بتعديل طريقة تحميل الـ cogs
    run_bot()
