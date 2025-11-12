import os

# إعدادات البوت
TOKEN = os.environ.get("TOKEN")

# الروابط والصور
AUTO_IMAGE_URL = "https://media.discordapp.net/attachments/1420819533941444608/1431324782863057017/line.png?ex=69063b14&is=6904e994&hm=cf47fbbeb5e94717e8375717a5cc780164bbeb6340611ab4d036112d0f954264&format=png&quality=lossless&width=1673&height=108&"
PANEL_IMAGE_URL = "https://media.discordapp.net/attachments/1243692264434438266/1437551644832174280/banner.png?ex=6914508c&is=6912ff0c&hm=84d1eefd6c88538655d9bb7ebd7d06b5c1b95a376cd851b9645b28d7cc86cd30&=&format=webp&quality=lossless&width=1240&height=686"
FEEDBACK_CHANNEL_LINK = "https://canary.discord.com/channels/1420808537784979488/1437552135188381717"

# الألوان
EMBED_COLOR = None  # لا يوجد لون محدد للإيمبدات

# معرف رتبة "ناشر"
PUBLISHER_ROLE_ID = 1437552543843745852

# رومات اللوقات (يجب استبدال هذه الأرقام بأرقام ID حقيقية للرومات)
# تم استخدام أرقام وهمية لغرض التطوير
LOG_PROFILE_CHANNEL_ID = 1437829430809460827
LOG_IMAGE_CHANNEL_ID = 1437829496727273522 # لوق الصورة
LOG_BANNER_CHANNEL_ID = 1437829681817849917 # لوق البنر
LOG_PAIR_CHANNEL_ID = 1437829796750168152 # لوق التطقيم

# رومات النشر (يجب استبدال هذه الأرقام بأرقام ID حقيقية للرومات)
# تم استخدام أرقام وهمية لغرض التطوير
PROFILE_CHANNELS = [1434594361483591761, 1434594397441232927]
IMAGE_CHANNELS = [1431315412104118435, 1434594300171128943, 1431315425894862928, 1434593901733482648]
BANNER_CHANNELS = [1437556064332808223, 1437556122037911582]
PAIR_CHANNELS = [1431315847166824491, 1437534765866680534, 1437535008829997116]

# قائمة بجميع قنوات النشر
ALL_POSTING_CHANNELS = PROFILE_CHANNELS + IMAGE_CHANNELS + BANNER_CHANNELS + PAIR_CHANNELS

# معرف روم التقييم (يجب استخراجه من الرابط المرفق في الكود الأصلي)
# ملاحظة: الرابط في الكود الأصلي هو "https://discord.com/channels/1433920441357045772/1433939000422301766"
# المعرف هو آخر جزء في الرابط
try:
    FEEDBACK_CHANNEL_ID = int(FEEDBACK_CHANNEL_LINK.split('/')[-1])
except ValueError:
    FEEDBACK_CHANNEL_ID = None # يجب على المستخدم تعيينه يدوياً إذا كان الرابط غير صحيح
