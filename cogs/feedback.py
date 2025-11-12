import discord
from discord.ext import commands
from datetime import timezone
from config import FEEDBACK_CHANNEL_ID, AUTO_IMAGE_URL, EMBED_COLOR
import asyncio

# تم إزالة خاصية الرد على التقييم بناءً على طلب المستخدم

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل رسائل البوتات
        if message.author.bot:
            return
        
        # التأكد من أن الرسالة في روم التقييم
        if message.channel.id == FEEDBACK_CHANNEL_ID:
            try:
                # تنسيق الوقت النسبي
                timestamp = int(message.created_at.timestamp())
                
                embed = discord.Embed(
                    title=f"<a:glitter_sparkles:1431316545208062013> تقييم جديد من {message.author.display_name}",
                    description=f"> **{message.content}**"
                )
                
                # تعيين الصورة المصغرة
                avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                embed.set_thumbnail(url=avatar_url)
                
                # استخدام تنسيق الوقت النسبي في التذييل
                embed.set_footer(text=f"تم التقييم في: ")
                embed.timestamp = message.created_at
                
                # إرسال منشن العضو مع الإيمبد
                sent_msg = await message.channel.send(
                    content=f"{message.author.mention} | <t:{timestamp}:R>", # إضافة الوقت النسبي في المحتوى
                    embed=embed
                )
                
                # إضافة رد فعل قلب تلقائيًا مع معالجة الأخطاء
                try:
                    await sent_msg.add_reaction("<a:Stars:1431316500270289007>")
                except discord.HTTPException as e:
                    print(f"Failed to add reaction: {e}")
                
                # تأخير صغير لتجنب التحديد من معدل الطلبات
                await asyncio.sleep(0.5)
                
                # إرسال الصورة التلقائية
                await message.channel.send(embed=discord.Embed().set_image(url=AUTO_IMAGE_URL))
                
                # حذف الرسالة الأصلية مع معالجة حالة الرسالة المحذوفة مسبقًا
                try:
                    await message.delete()
                except discord.NotFound:
                    # الرسالة محذوفة بالفعل، لا مشكلة
                    pass
                except discord.HTTPException as e:
                    print(f"Failed to delete message: {e}")
                
            except Exception as e:
                print(f"Error processing feedback message: {e}")
                # محاولة إرسال رسالة خطأ للعضو إذا أمكن
                try:
                    await message.channel.send(f"❌ {message.author.mention} حدث خطأ أثناء معالجة تقييمك. يرجى المحاولة مرة أخرى.", delete_after=10)
                except:
                    pass

async def setup(bot):
    await bot.add_cog(Feedback(bot))
