from flask import Flask
from discord.ext import commands
import discord, asyncio, os, requests
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.context import MenuContext, SlashContext
from discord_slash.model import ContextMenuType
import time
from discord_slash.utils.manage_components import create_actionrow, create_button, create_select, create_select_option, wait_for_component, ComponentContext
from discord_slash.model import ButtonStyle
from threading import Thread
import datetime


app = Flask("sus")

@app.route("/")
def sussibaak():
  return "SO SUS"

client = commands.Bot("__", status=discord.Status.offline)
client.remove_command("help")
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_message(message):
  if message.author.bot:
    return
  if message.content == "didi mod":
    async with message.channel.typing():
      await asyncio.sleep(0.4)
    return await message.channel.send("哞！我在這裡！")

@slash.context_menu(target=ContextMenuType.USER, name="回報使用者", guild_ids=[858984157929144321])
async def _letsgo_report(ctx):
  await ctx.defer(hidden=True)
  await asyncio.sleep(0.5)
  if ctx.target_author.id == 990911689929138206:
    return await ctx.send(f"我做錯了甚麼...", hidden=True)
  embed = discord.Embed(
    title=f"你將回報的使用者是 {ctx.target_author.name}",
    description="請選擇使用者違規的類別，若要取消請按 `取消` 按鈕",
    color=0x0995ec
  )
  embed.set_footer(text="舉報使用者 • #牛牛的草原")
  msg = await ctx.send(embed=embed, components=[
    create_actionrow(
      create_select(
        options=[
          create_select_option(
            label="違反規定",
            value="against_rules",
            emoji="📖",
            description="違反在 #📙規定 頻道中的條項"
          ),
          create_select_option(
            label="洗版",
            value="washboard",
            emoji="🧽",
            description="多次傳送訊息來覆蓋頻道版面"
          ),
          create_select_option(
            label="炸群",
            value="nuke",
            emoji="💥",
            description="管理員或機器人破壞伺服器安寧 (如：隨意刪除頻道)"
          ),
          create_select_option(
            label="其他",
            value="other",
            emoji="🤔",
            description="其他違規事項"
          )
        ],
        custom_id="select_REPORT:USER"
      )
    ),
    create_actionrow(
      create_button(
        style=ButtonStyle.red,
        label="取消",
        custom_id="cancel"
      )
    )
  ], hidden=True)
  #print(msg)
  res = await wait_for_component(client, messages=int(msg['id']))
  if res.data['custom_id'] == "cancel":
    return await res.edit_origin(content="已取消", components=[], embeds=[])
  #print(res.data)
  json = {
    "nuke": "炸群",
    "against_rules": "違反規定",
    "washboard": "洗版",
    "other": "其他違規事項"
  }
  channel = client.get_channel(858985876200751115)
  embed = discord.Embed(
    title=f"{ctx.target_author} 被回報",
    description=f"原因：{json[''.join(res.data['values'])]}",
    color=0x0995ec
  )
  embed.set_footer(text=f"舉發人：{ctx.author.name} • {ctx.author.id}", icon_url=str(ctx.author.avatar_url))
  await channel.send(embed=embed, components=[
    create_actionrow(
      create_select(
        options=[
          create_select_option(
            label="禁言使用者",
            value="timeout",
            emoji="🚫",
            description="使用者將無法發言、使用指令或新增反應"
          ),
          create_select_option(
            label="踢除使用者",
            value='kick',
            emoji="👢",
            description="直接跟他說再見"
          ),
          create_select_option(
            label="飛機票",
            value="ban",
            emoji="✈️",
            description="🔨 停權使用者"
          ),
          create_select_option(
            label="警告使用者",
            value="warn",
            emoji="⚠️",
            description="在 #聊天 頻道警告使用者"
          ),
          create_select_option(
            label="去面壁思過",
            value="role",
            emoji="😩",
            description="最傳統的面壁思過方法"
          )
        ],
        custom_id=f"action:{ctx.target_author.id}",
        placeholder="🛡️ 選擇操作"
      )
    )
  ])
  await res.edit_origin(content="回報成功！", components=[], embeds=[])
  

@client.event
async def on_component(ctx):
  if ctx.data['custom_id'].startswith("timeout:"):
    m = ctx.data['custom_id'].replace("timeout:", "")
    duration = int(m.split(";")[0])
    user = m.split(";")[1]
    if duration == 60:
      t = datetime.datetime.now() + datetime.timedelta(seconds=60)
      t = t.isoformat()
    elif duration == 600:
      t = datetime.datetime.now() + datetime.timedelta(minutes=10)
      t = t.isoformat()
      
    elif duration == 86400:
      t = datetime.datetime.now() + datetime.timedelta(days=1)
      t = t.isoformat()
      
    elif duration == 0:
      t = None
    url = f"https://discord.com/api/v9/guilds/858984157929144321/members/{user}"
    r = requests.patch(url, json={
        "communication_disabled_until": t
      }, headers={
        "Authorization": f"Bot {os.environ['token']}"
      })
    print("response: " + r.text)
    if duration != 0:
      await ctx.edit_origin(content=":white_check_mark: 使用者已被禁言", components=[], embeds=[])
      await ctx.channel.send(f"使用者 <@{user}> 已被禁言", components=[
        create_actionrow(
          create_button(
            style=ButtonStyle.red,
            label="取消禁言",
            custom_id=f"timeout:0;{user}"
          )
        )
      ])
    else:
      await ctx.edit_origin(content=":white_check_mark: 使用者已被取消禁言", components=[], embeds=[])
      await ctx.channel.send(f"使用者 <@{user}> 已被取消禁言")

    

  if ctx.data['custom_id'].startswith("action:"):
    user = ctx.data['custom_id'].replace("action:", "")
    #print(ctx.data)

    if ctx.data['values'] == ['warn']:
      ch = client.get_channel(858984158620286998)
      await ch.send(f"<@{user}>", embed=discord.Embed(
        title=":warning: | 警告 1 支",
        description="請注意你的言行舉止！",
        color=0xFF0000
      ))
      await ctx.send(":white_check_mark: 已傳送警告", hidden=True)
      
    
    if ctx.data['values'] == ['role']:
      url = f"https://discord.com/api/v9/guilds/858984157929144321/members/{user}"
      r = requests.get(url, headers={
        "Authorization": f"Bot {os.environ['token']}"
      })
      roles = r.json()['roles']
      for R in roles:
        print(R)
        url = f"https://discord.com/api/v9/guilds/858984157929144321/members/{user}/roles/{R}"
        requests.delete(url, headers={
          "Authorization": f"Bot {os.environ['token']}"
        })
      url = f"https://discord.com/api/v9/guilds/858984157929144321/members/{user}/roles/876720343887257630"
      requests.put(url, headers={
          "Authorization": f"Bot {os.environ['token']}"
        })
      await ctx.defer(ignore=True)
      await ctx.channel.send(f"現在 <@{user}> 必須到 <#876721506766450730> 面壁思過")
    if ctx.data['values'] == ['ban']:
      url = f"https://discord.com/api/v9/guilds/858984157929144321/bans/{user}"
      requests.put(url, headers={
        "Authorization": f"Bot {os.environ['token']}"
      })
      await ctx.send(":hammer: 使用者搭飛機閃人了", hidden=True)
      await ctx.channel.send(f"使用者 <@{user}> 被停權了")
      
    if ctx.data['values'] == ['kick']:
      url = f"https://discord.com/api/v9/guilds/858984157929144321/members/{user}"
      requests.delete(url, headers={
        "Authorization": f"Bot {os.environ['token']}"
      })
      await ctx.send(":white_check_mark: 使用者被踢出了", hidden=True)
      await ctx.channel.send(f"使用者 <@{user}> 已被踢出")
      
    if ctx.data['values'] == ['timeout']:
      await ctx.send("要禁言多久？", components=[
        create_actionrow(
          create_button(
            style=ButtonStyle.blurple,
            label="1 分鐘",
            custom_id=f"timeout:60;{user}"
          ),
          create_button(
            style=ButtonStyle.gray,
            label="10 分鐘",
            custom_id=f"timeout:600;{user}"
          ),
          create_button(
            style=ButtonStyle.red,
            label="1 天",
            custom_id=f"timeout:86400;{user}"
          )
        )
      ], hidden=True)

      

      
  
@client.event
async def on_ready():
  print("i am finally ready!1111!")

def runner():
  app.run(host="0.0.0.0", port=123)


Thread(target=runner).start()
client.run(os.environ['token'])
