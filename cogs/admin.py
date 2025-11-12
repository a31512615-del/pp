import discord
from discord.ext import commands
from config import EMBED_COLOR

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="stats", description="عرض إحصائيات استخدام البوت (للمسؤولين فقط).")
    @commands.has_permissions(administrator=True)
    async def stats(self, ctx: commands.Context):
        stats_data = self.bot.stats
        
        # تحويل المفاتيح إلى أسماء عربية واضحة
        names_map = {
            "add_profile": "إضافة بروفايل كامل",
            "add_image": "إضافة صورة",
            "add_banner": "إضافة بنر",
            "add_pair": "إضافة تطقيم",
        }
        
        description = "📊 **إحصائيات استخدام أزرار النشر**\n\n"
        
        total_uses = sum(stats_data.values())
        
        if total_uses == 0:
            description += "لم يتم استخدام أي من أزرار النشر بعد."
        else:
            for key, count in stats_data.items():
                name = names_map.get(key, key)
                percentage = (count / total_uses) * 100 if total_uses > 0 else 0
                description += f"**{name}:** {count} مرة ({percentage:.1f}%)\n"
        
        embed = discord.Embed(
            title="📈 إحصائيات البوت",
            description=description
        )
        embed.set_footer(text=f"إجمالي الاستخدام: {total_uses}")
        
        await ctx.send(embed=embed)

    @stats.error
    async def stats_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ ليس لديك الصلاحيات الكافية لاستخدام هذا الأمر.", ephemeral=True)
        else:
            await ctx.send(f"❌ حدث خطأ: {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
