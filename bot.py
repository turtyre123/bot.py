import discord
from discord.ext import commands
from datetime import datetime
import os
from dotenv import load_dotenv
import random

# ======================
# 🔐 TOKEN
# ======================
load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("❌ TOKEN이 .env에 없습니다!")

# ======================
# ⚙️ BOT
# ======================
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1510902073787416596
guild = discord.Object(id=GUILD_ID)

# ======================
# 📦 DATA
# ======================
stock = {"상품1": 10, "상품2": 5}

STOCK_LOG_CHANNEL_ID = 1510949980469465208
SALES_LOG_CHANNEL_ID = 1510989617329999892

BUY_ROLE = "𝐀𝐝𝐦𝐢𝐧"
ALERT_ROLE_ID = 1511693398250360872

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ======================
# 📦 입고
# ======================
@bot.tree.command(name="입고로그", description="상품 입고", guild=guild)
async def 입고(interaction: discord.Interaction, 상품명: str, 수량: int, 설명: str):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ 관리자만 가능", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    stock[상품명] = stock.get(상품명, 0) + 수량

    embed = discord.Embed(title="📦 HOJI SHOP 입고", color=discord.Color.green())
    embed.add_field(name="상품", value=상품명, inline=True)
    embed.add_field(name="수량", value=str(수량), inline=True)
    embed.add_field(name="설명", value=설명, inline=False)
    embed.add_field(name="입고자", value=interaction.user.mention, inline=False)
    embed.add_field(name="시간", value=now(), inline=False)
    embed.set_footer(text="HOJI SHOP SYSTEM")

    channel = bot.get_channel(STOCK_LOG_CHANNEL_ID)

    if channel:
        role = interaction.guild.get_role(ALERT_ROLE_ID)
        if role:
            await channel.send(f"{role.mention} 📦 새 상품이 입고되었습니다!")

        await channel.send(embed=embed)

    await interaction.followup.send("✅ 입고 완료")

# ======================
# 🛒 구매 + 영수증
# ======================
@bot.tree.command(name="구매로그", description="상품 구매", guild=guild)
async def 구매(interaction: discord.Interaction, 상품명: str, 수량: int):

    await interaction.response.defer(ephemeral=True)

    roles = [r.name for r in interaction.user.roles]

    if BUY_ROLE not in roles:
        await interaction.followup.send("❌ 구매 권한 없음")
        return

    if 상품명 not in stock:
        await interaction.followup.send("❌ 상품 없음")
        return

    if stock[상품명] < 수량:
        await interaction.followup.send("❌ 재고 부족")
        return

    stock[상품명] -= 수량

    receipt_id = random.randint(100000, 999999)

    embed = discord.Embed(title="🧾 HOJI SHOP 영수증", color=discord.Color.blue())
    embed.add_field(name="영수증 ID", value=str(receipt_id), inline=False)
    embed.add_field(name="구매자", value=interaction.user.mention, inline=False)
    embed.add_field(name="상품", value=상품명, inline=True)
    embed.add_field(name="수량", value=str(수량), inline=True)
    embed.add_field(name="남은 재고", value=str(stock[상품명]), inline=False)
    embed.add_field(name="시간", value=now(), inline=False)
    embed.set_footer(text="HOJI SHOP 💙 Thank you")

    channel = bot.get_channel(SALES_LOG_CHANNEL_ID)

    if channel:
        await channel.send(embed=embed)

    await interaction.followup.send(f"✅ 구매 완료! | 영수증 ID: {receipt_id}")

# ======================
# 🚀 READY
# ======================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Slash Sync 완료: {len(synced)}개")
        print(f"🤖 로그인 완료: {bot.user}")
    except Exception as e:
        print(f"❌ Sync 오류: {e}")

# ======================
# 🚀 RUN
# ======================
bot.run("TOKEN")