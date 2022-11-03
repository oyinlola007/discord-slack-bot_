import discord, asyncio, time, sys

import cogs.config as config
import cogs.strings as strings
import cogs.db as db
import cogs.utils as utils

client = discord.Client()
default_ts = str(time.time())

db.initialize_db()

@client.event
async def on_ready():
    print(strings.LOGGED_IN.format(client.user))

@client.event
async def on_message(message):
    if message.author.id != config.BOT_ID and message.channel.id == config.DISCORD_CHANNEL_ID:
        text = message.content

        #replaces discord_id with slack_id when available
        try:
            text = utils.replace_discord_id_with_slack_id(text)
        except Exception as _:
            pass

        avatar_url = str(message.author.avatar_url).split("?")[0]

        res = utils.post_message_to_slack(avatar_url, message.author.name, text)
        json_res = res.json()
        db.insert_discord_log(message.id, message.author.id, "text", json_res["ts"], message.content)
        db.limit_table_to_x_rows("DISCORD_MESSAGE_LOG", "100")

        #send all attachements as links, if any
        for attachment in message.attachments:
            utils.post_message_to_slack(avatar_url, message.author.name, attachment.url)

@client.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        try:
            slack_timestamp = db.get_timestamp(reaction.message.id)
            emoji = strings.EMOJI_DICT[reaction.emoji[0]]

            if slack_timestamp != "0":
                utils.add_reaction_to_slack(emoji, slack_timestamp)
                return

            slack_timestamp = db.get_timestamp_from_slack_message_log(reaction.message.id)
            emoji = strings.EMOJI_DICT[reaction.emoji[0]]

            if slack_timestamp != "0":
                utils.add_reaction_to_slack(emoji, slack_timestamp)

        except Exception as _:
            pass

async def user_metrics_background_task1():
    await client.wait_until_ready()
    while True:
        try:
            messages = utils.get_messages_since_timestamp(default_ts)
            messages = list(reversed(messages))

            for message in messages:
                try:
                    text = message["text"]

                    if text != "":
                        user_id = message["user"]
                        try:
                            text = utils.replace_slack_id_with_discord_id(text)
                        except Exception as _:
                            pass

                        user = utils.get_user_details(user_id)
                        name = user["name"]
                        avatar_url = user["profile"]["image_original"]

                        channel = client.get_channel(config.DISCORD_CHANNEL_ID)

                        embed = discord.Embed(description=text, color=0xbd2f00)
                        embed.set_author(name=name, icon_url=avatar_url)
                        msg = await channel.send(embed=embed)
                        db.insert_slack_log(message["ts"], user_id, "text", msg.id, text, "")
                        db.limit_table_to_x_rows("SLACK_MESSAGE_LOG", "20")

                except Exception as _:
                    pass

        except Exception as _:
            pass

        for _ in range(10):
            await asyncio.sleep(1)

async def user_metrics_background_task2():
    await client.wait_until_ready()
    while True:
        try:
            rows = db.get_all_slack_message_ts()

            for row in rows:
                try:
                    ts = row[0]
                    channel_id = config.DISCORD_CHANNEL_ID
                    message_id = row[3]
                    reactions = utils.get_reactions_for_message(ts)
                    old_reactions = db.get_old_reactions_for_message(ts)

                    for reaction in reactions:
                        try:
                            reaction_name = reaction["name"]
                            if reaction_name not in old_reactions:
                                reaction_emoji = utils.get_key_from_value(reaction_name, strings.EMOJI_DICT)
                                channel = client.get_channel(channel_id)
                                msg = await channel.fetch_message(message_id)
                                await msg.add_reaction(reaction_emoji)
                                db.update_old_reactions_for_message(ts, old_reactions + " " + reaction_name)

                        except Exception as _:
                            pass
                except Exception as _:
                    pass
        except Exception as _:
            pass

        for _ in range(30):
            await asyncio.sleep(1)

async def user_metrics_background_task3():
    await client.wait_until_ready()
    while True:
        try:
            rows = db.get_all_slack_message_from_discord()

            for row in rows:
                try:
                    ts = row[3]
                    channel_id = config.DISCORD_CHANNEL_ID
                    message_id = row[0]
                    reactions = utils.get_reactions_for_message(ts)
                    old_reactions = db.get_old_reactions_for_message2(ts)

                    for reaction in reactions:
                        try:
                            reaction_name = reaction["name"]
                            if reaction_name not in old_reactions:
                                reaction_emoji = utils.get_key_from_value(reaction_name, strings.EMOJI_DICT)
                                channel = client.get_channel(channel_id)
                                msg = await channel.fetch_message(message_id)
                                await msg.add_reaction(reaction_emoji)
                                db.update_old_reactions_for_message2(ts, old_reactions + " " + reaction_name)

                        except Exception as _:
                            pass
                except Exception as _:
                    pass
        except Exception as _:
            pass

        for _ in range(30):
            await asyncio.sleep(1)

client.loop.create_task(user_metrics_background_task1())
client.loop.create_task(user_metrics_background_task2())
client.loop.create_task(user_metrics_background_task3())
client.run(config.DISCORD_TOKEN)
