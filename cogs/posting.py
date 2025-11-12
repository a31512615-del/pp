import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import asyncio
from config import (
    EMBED_COLOR, AUTO_IMAGE_URL, PANEL_IMAGE_URL, FEEDBACK_CHANNEL_LINK,
     PROFILE_CHANNELS, IMAGE_CHANNELS, BANNER_CHANNELS, PAIR_CHANNELS,
    PUBLISHER_ROLE_ID,
    LOG_PROFILE_CHANNEL_ID, LOG_IMAGE_CHANNEL_ID, LOG_BANNER_CHANNEL_ID, LOG_PAIR_CHANNEL_ID
)

# 💾 زر الحفظ
class SaveButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji="<:directdownload:1434610723065036851>", style=discord.ButtonStyle.gray, custom_id="save_image")
    async def save_image_callback(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.errors.NotFound:
            # Interaction already expired, exit gracefully
            return
        
        try:
            # استرجاع روابط الصور من الرسائل السابقة
            image_urls = []
            # نبدأ البحث من الرسالة التي تحتوي على الزر ونعود للخلف
            # نستخدم limit=20 للبحث في آخر 20 رسالة
            async for message in interaction.channel.history(limit=20, before=interaction.message):
                # نتوقف عند أول رسالة لا تحتوي على Embed أو تحتوي على رسالة اللوحة
                # الرسائل التي تحتوي على الصور هي Embeds بدون محتوى نصي
                if not message.embeds or message.content or message.author.id != interaction.client.user.id:
                    break
                
                # الرسالة التي تحتوي على الصورة التلقائية يجب تجاهلها
                # يجب أن نمرر AUTO_IMAGE_URL إلى الكلاس أو نستخدم طريقة أخرى للوصول إليه
                # الطريقة الأسهل هي الوصول إليه عبر الـ Cog
                posting_cog = interaction.client.get_cog("Posting")
                if posting_cog and message.embeds[0].image and message.embeds[0].image.url == posting_cog.AUTO_IMAGE_URL:
                    continue

                # جمع روابط الصور من الـ Embeds
                if message.embeds[0].image:
                    image_urls.append(message.embeds[0].image.url)
            
            # عكس الترتيب لأننا بدأنا من الأحدث للأقدم
            image_urls.reverse()

            # إرسال الصور
            for url in image_urls:
                await interaction.user.send(url)
            
            # إرسال الصورة التلقائية
            posting_cog = interaction.client.get_cog("Posting")
            if posting_cog:
                await interaction.user.send(posting_cog.AUTO_IMAGE_URL)

            # إرسال رابط التقييم
            try:
                await interaction.user.send(
                    f"<a:rAmi:1431316627089002628> لا تنسى تعطينا رأيك ونصيحتك للسيرفر: {FEEDBACK_CHANNEL_LINK}"
                )
            except discord.Forbidden:
                pass
            
            await interaction.followup.send("<a:SETTINGS:1431316598005698685> تم إرسال الصور إليك بالخاص!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("<:3_:1433501806792806530> لم أتمكن من إرسال الصور، افتح الخاص أولًا!", ephemeral=True)
        except Exception as e:
            print(f"Error in SaveButton: {e}")
            await interaction.followup.send("<:3_:1433501806792806530> حدث خطأ غير متوقع أثناء إرسال الصور.", ephemeral=True)

# ⚙️ قائمة اختيار الروم
class ChannelSelect(Select):
    def __init__(self, channels, callback):
        # إزالة التكرارات من القنوات باستخدام dict للحفاظ على الترتيب
        unique_channels = {ch.id: ch for ch in channels if ch is not None}.values()
        options = [discord.SelectOption(label=ch.name, value=str(ch.id)) for ch in unique_channels]
        super().__init__(placeholder="اختر الروم للنشر...", min_values=1, max_values=1, options=options)
        self.callback_func = callback

    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, int(self.values[0]))

class ChannelSelectView(View):
    def __init__(self, channels, callback):
        super().__init__(timeout=60)
        self.add_item(ChannelSelect(channels, callback))

async def start_posting_process(bot, inter: discord.Interaction, post_type: str, allowed_channels_ids: list):
    allowed_channels = [bot.get_channel(ch_id) for ch_id in allowed_channels_ids]
    allowed_channels = [ch for ch in allowed_channels if ch is not None] # تصفية القنوات غير الموجودة

    if not allowed_channels:
        await inter.user.send("<:1_:1433501793249394870> لا توجد رومات متاحة للنشر لهذا النوع من المحتوى.")
        return

    async def post_to_channel(select_inter: discord.Interaction, ch_id: int):
        await select_inter.response.defer() # تأجيل التفاعل
        ch = bot.get_channel(ch_id)
        
        try:
            image_urls = []
            
            # 1. جمع الصور المطلوبة
            if post_type == "add_profile":
                await inter.user.send("<:7793965375DF4ED2BFA64347F98FDF90:1431316549934780426> أرسل صورة البروفايل أولًا:")
                img_msg = await bot.wait_for("message", check=lambda m: m.author == inter.user and m.attachments, timeout=120)
                await inter.user.send("<:7793965375DF4ED2BFA64347F98FDF90:1431316549934780426>أرسل البنر الآن:")
                banner_msg = await bot.wait_for("message", check=lambda m: m.author == inter.user and m.attachments, timeout=120)
                
                img_url = img_msg.attachments[0].url
                banner_url = banner_msg.attachments[0].url
                image_urls = [img_url, banner_url]
                
            elif post_type == "add_image" or post_type == "add_banner":
                prompt = "<:7793965375DF4ED2BFA64347F98FDF90:1431316549934780426> أرسل الصورة:" if post_type == "add_image" else "<:7793965375DF4ED2BFA64347F98FDF90:1431316549934780426> أرسل البنر:"
                await inter.user.send(prompt)
                msg = await bot.wait_for("message", check=lambda m: m.author == inter.user and m.attachments, timeout=120)
                img_url = msg.attachments[0].url
                image_urls = [img_url]
                
            elif post_type == "add_pair":
                await inter.user.send("<:7793965375DF4ED2BFA64347F98FDF90:1431316549934780426> أرسل الصورة الأولى:")
                img1 = await bot.wait_for("message", check=lambda m: m.author == inter.user and m.attachments, timeout=120)
                await inter.user.send("<:7793965375DF4ED2BFA64347F98FDF90:1431316549934780426> أرسل الصورة الثانية:")
                img2 = await bot.wait_for("message", check=lambda m: m.author == inter.user and m.attachments, timeout=120)
                
                img1_url = img1.attachments[0].url
                img2_url = img2.attachments[0].url
                image_urls = [img1_url, img2_url]

            # 2. إرسال الإيمبدات
            # يتم إرسال كل صورة في رسالة منفصلة
            for url in image_urls:
                embed = discord.Embed()
                embed.set_image(url=url)
                await ch.send(embed=embed)

            # 3. إرسال زر الحفظ والصورة التلقائية
            # يجب إرسال زر الحفظ في رسالة منفصلة لضمان ظهوره بشكل صحيح
            await ch.send(view=SaveButton())
            # إرسال الصورة التلقائية في رسالة منفصلة
            await ch.send(embed=discord.Embed().set_image(url=AUTO_IMAGE_URL))
            
            # 4. تحديث الإحصائيات
            bot.stats[post_type] += 1

            # 5. إرسال رسالة نجاح
            await inter.user.send(f"<a:34:1431316567865561170> تم نشر المنشور بنجاح في الروم: {ch.mention}")
            
            # **تسجيل اللوق في الروم المخصص**
            log_channel_id = None
            log_type_arabic = ""
            
            if post_type == "add_profile":
                log_channel_id = LOG_PROFILE_CHANNEL_ID
                log_type_arabic = "بروفايل كامل"
            elif post_type == "add_image":
                log_channel_id = LOG_IMAGE_CHANNEL_ID
                log_type_arabic = "صورة"
            elif post_type == "add_banner":
                log_channel_id = LOG_BANNER_CHANNEL_ID
                log_type_arabic = "بنر"
            elif post_type == "add_pair":
                log_channel_id = LOG_PAIR_CHANNEL_ID
                log_type_arabic = "تطقيم"
                
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    # بناء رسالة اللوق المفصلة
                    log_embed = discord.Embed(
                        title=f"<a:34:1431316567865561170> تم النشر بنجاح - {log_type_arabic}",
                        description=f"**الناشر:** {inter.user.mention} (`{inter.user.id}`)\n**الروم:** {ch.mention} (`{ch.id}`)",
                        color=EMBED_COLOR if EMBED_COLOR else discord.Color.green()
                    )
                    
                    # إضافة روابط الصور
                    image_links = "\n".join([f"• [رابط الصورة {i+1}]({url})" for i, url in enumerate(image_urls)])
                    log_embed.add_field(name="روابط الصور المنشورة", value=image_links, inline=False)
                    
                    # تعيين أول صورة كصورة مصغرة للإيمبد
                    if image_urls:
                        log_embed.set_thumbnail(url=image_urls[0])
                        
                    log_embed.set_footer(text=f"الوقت: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    try:
                        # إرسال اللوق
                        await log_channel.send(embed=log_embed)
                        # إرسال الصورة التلقائية بعد اللوق
                        await log_channel.send(AUTO_IMAGE_URL)
                    except Exception as e:
                        print(f"Error sending detailed log to channel {log_channel_id}: {e}")
                else:
                    print(f"Log channel with ID {log_channel_id} not found.")
            
            # لا نحتاج لإرجاع أي شيء هنا، فقط نضمن اكتمال العملية
            return inter.user, ch, image_urls

        except asyncio.TimeoutError:
            await inter.user.send("<a:34:1431316579328589845> انتهى الوقت! لم يتم إرسال الصور في الوقت المحدد.")
            return None, None, None
        except Exception as e:
            print(f"Error during posting process: {e}")
            await inter.user.send(f"<a:34:1431316579328589845> حدث خطأ أثناء عملية النشر: {e}")
            return None, None, None
        finally:
            # حذف رسالة اختيار الروم
            try:
                await select_inter.message.delete()
            except:
                pass

    # إرسال قائمة اختيار الروم
    await inter.user.send("<a:__:1431316590141505766> اختر الروم للنشر:", view=ChannelSelectView(allowed_channels, post_to_channel))


# 🔘 لوحة التحكم
class ImagePanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        # الأزرار تم تعريفها كـ @discord.ui.button أدناه، لا حاجة لإضافتها هنا
        # تم حذف الأسطر المكررة التي تسببت في الخطأ

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # التحقق من وجود رتبة "ناشر" باستخدام الـ ID
        if PUBLISHER_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message("<:3_:1433501806792806530> فقط الأعضاء الذين لديهم رتبة 'ناشر' يمكنهم استخدام هذه الأزرار.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        # إزالة الأزرار عند انتهاء المهلة (إذا لم يكن timeout=None)
        pass

    @discord.ui.button(label="إضافة بروفايل كامل", style=discord.ButtonStyle.gray, custom_id="add_profile", row=0)
    async def add_profile_callback(self, interaction: discord.Interaction, button: Button):
        await self.handle_posting_interaction(interaction, "add_profile", PROFILE_CHANNELS)

    @discord.ui.button(label="إضافة صورة", style=discord.ButtonStyle.gray, custom_id="add_image", row=0)
    async def add_image_callback(self, interaction: discord.Interaction, button: Button):
        await self.handle_posting_interaction(interaction, "add_image", IMAGE_CHANNELS)

    @discord.ui.button(label="إضافة بنر", style=discord.ButtonStyle.gray, custom_id="add_banner", row=1)
    async def add_banner_callback(self, interaction: discord.Interaction, button: Button):
        await self.handle_posting_interaction(interaction, "add_banner", BANNER_CHANNELS)

    @discord.ui.button(label="إضافة تطقيم", style=discord.ButtonStyle.gray, custom_id="add_pair", row=1)
    async def add_pair_callback(self, interaction: discord.Interaction, button: Button):
        await self.handle_posting_interaction(interaction, "add_pair", PAIR_CHANNELS)

    async def handle_posting_interaction(self, interaction: discord.Interaction, post_type: str, allowed_channels_ids: list):
        # إرسال رسالة تأكيد للمستخدم في الخاص
        await interaction.response.send_message("<a:SETTINGS:1431316598005698685> جارٍ إكمال عملية النشر في الخاص...", ephemeral=True)
        

        
        # بدء عملية النشر في الخاص مباشرة بدون مودال الوصف
        await start_posting_process(self.bot, interaction, post_type, allowed_channels_ids)


class Posting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.AUTO_IMAGE_URL = AUTO_IMAGE_URL
        # إضافة لوحة التحكم كـ persistent view
        self.bot.add_view(ImagePanel(self.bot))
        self.bot.add_view(SaveButton()) # إضافة زر الحفظ كـ persistent view

    # ===== لوحة التحكم مع صورة الإيمبد (أمر سلاش) =====
    @commands.hybrid_command(name="panel", description="إرسال لوحة التحكم لنشر الصور (للمسؤولين فقط).")
    @commands.has_permissions(administrator=True)
    async def panel(self, ctx: commands.Context):
        # Acknowledge the command ephemerally
        await ctx.send("جاري إرسال اللوحة...", ephemeral=True)

        # 1. Send the top image
        await ctx.channel.send(PANEL_IMAGE_URL)

        # 2. Send the buttons without an embed (using an empty string for content)
        await ctx.channel.send(content="", view=ImagePanel(self.bot))

        # 3. Send the bottom image (line)
        await ctx.channel.send(AUTO_IMAGE_URL)

    @panel.error
    async def panel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("<:1_:1433501793249394870> ليس لديك الصلاحيات الكافية لاستخدام هذا الأمر.", ephemeral=True)
        elif isinstance(error, commands.MissingRole):
            await ctx.send("<:1_:1433501793249394870> ليس لديك الصلاحيات الكافية لاستخدام هذا الأمر.", ephemeral=True)
        else:
            await ctx.send(f"<:1_:1433501793249394870> حدث خطأ: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Posting(bot))
