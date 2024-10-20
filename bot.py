import asyncio
import database_calls
import discord
import discord.ext
import discord.ext.commands
import format_bot_response
import random
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
from itertools import cycle

# Bot commands configuration
spin_sugar_file = "spin_sugar.txt"
crafting_recipes_file = "crafting_recipes.txt"
game_rules_file = "game_rules.txt"
auth_code_file = "auth_code.txt"
game_command = commands.DefaultHelpCommand(no_category = "Commands")
client = commands.Bot(command_prefix="=", case_insensitive=True, intents=discord.Intents.all(), help_command=game_command)

# Bot status
bot_status = cycle(["=Help for commands.", "=Rules for game rules."])
@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.CustomActivity(name=next(bot_status), emoji=":scream_cat:"))

# Bot commands
@client.command(help = "Shows the game rules")
async def rules(ctx):
    game_rules = open(game_rules_file).read()
    await ctx.reply(game_rules)

@client.command(help = "Say hello to Cyberglorp MK1", aliases = ["Hey", "Greet", "Hi", "Good Morning", "Greetings"])
async def hello(ctx):
    # await ctx.reply("Public Message") | await ctx.author.send("Direct Message")
    username = ctx.message.author.global_name.title()
    await ctx.reply(f"Greetings, {username}. Now kneel before Cyberglorp!")

'''
@client.command(help = "Delete the last 100 messages")
async def clear(ctx, number = 100):
    await ctx.channel.purge(limit = number)

@client.command(help = "Return unique ID for discord user")
async def Idme(ctx):
    user_id = ctx.message.author.id
    await ctx.reply(f"Your ID is {user_id}.")

@client.command(help = "Get the latency of bot")
async def Ping(ctx):
    bot_latency = round(client.latency * 1000)
    await ctx.reply(f"My current latency is {bot_latency} ms. Not great, not terrible.")
'''
@client.command(help = "Discard one of your Glorps", aliases = ["Delete", "Remove"])
async def discard(ctx, glorp_name: str = commands.parameter(default="", description="The name of a Glorp in your collection.")):
    user_id = ctx.message.author.id
    if not glorp_name:
        message = f"# :fire: Discarding\n\nType `=Discard \"Glorp Name\"` to remove a Glorp from your collection."
        message += f"\n\nDiscarding can create room in your collection if you hit the limit. There is no other benefit to discarding Glorps."
        message += f" Once a Glorp is discarded, it is lost forever."
        await ctx.reply(message)
    else:
        glorp_row_id = database_calls.GlorpDB().GetIdForGlorpInUsersCollection(user_id, glorp_name)
        if not glorp_row_id:
            await ctx.reply("You cannot discard what you do not possess. Type `=View` to see the Glorps in your collection.")
        else:
            database_calls.GlorpDB().DiscardGlorp(glorp_row_id[0])
            await ctx.reply(f":fire: `{glorp_name.title()}` was removed from your collection.\n\n-# Perhaps you'll meet again some day...")
    return


@client.command(help = "View your Glorp collection", aliases = ["List", "See", "Inspect", "Look"])
async def view(ctx, glorp_name: str = commands.parameter(default="", description="The name of a Glorp in your collection.")):
    user_id = ctx.message.author.id
    if not glorp_name:
        glorp_collection = database_calls.GlorpDB().GetUserGlorpCollection(user_id)
        await ctx.reply(glorp_collection[:1900])
    elif glorp_name.lower() == "sort":
        glorp_collection = database_calls.GlorpDB().GetUserGlorpCollection(user_id, True)
        await ctx.reply(glorp_collection[:1900])
    else:
        glorp_data = database_calls.GlorpDB().GetGlorpDataFromUserIdAndName(user_id, glorp_name)
        if not glorp_data:
            await ctx.reply(f"You cannot examine what you do not own. Type `=View` to see the Glorps in your collection.")
        else:
            file_path = format_bot_response.GlorpResponses().GetImagePath(file_name = glorp_data[1])
            message = f"# {glorp_data[2]}\n"
            message += format_bot_response.GlorpResponses().GetDetailedViewDescription(glorp_data)
            await ctx.reply(content=message, file=discord.File(file_path))

@client.command(help = "Banish a card from the wheel")
async def ban(ctx, glorp_name: str = commands.parameter(default="", description="The name of a Glorp to add to the ban list."), clear_glorp_name: str = commands.parameter(default="", description="The name of a Glorp to remove from the ban list.")):
    user_id = ctx.message.author.id
    ban_slots = database_calls.GlorpDB().QueryDatabaseForUserBanSlotCount(user_id)
    banned_glorps = database_calls.GlorpDB().GetGlorpsInUsersBannedList(user_id)
    open_ban_slots = ban_slots - len(banned_glorps)

    if not glorp_name or (BanClearCommand(glorp_name) and not clear_glorp_name):
        banned_info_message = format_bot_response.GlorpResponses().GetBannedListMessage(open_ban_slots, banned_glorps)
        await ctx.reply(banned_info_message)
    elif BanClearCommand(glorp_name) and clear_glorp_name:
        glorp_ban_request = database_calls.GlorpDB().GetBannableGlorpInfo(clear_glorp_name)
        database_calls.GlorpDB().RemoveGlorpFromUserBanList(user_id, glorp_ban_request[2])
        await ctx.reply(f":prohibited: `{clear_glorp_name.title()}` was removed from your banishment list.\n\n-# It can once again be obtained from spinning the wheel...")
    elif not BanClearCommand(glorp_name) and ban_slots == 0 and len(banned_glorps) == 0:
        await ctx.reply(f"You have no banishment slots available. You'll need to obtain a Glorp with the banishment perk to use this feature.")
    elif not BanClearCommand(glorp_name) and open_ban_slots < 1:
        await ctx.reply(f"You have no banishment slots available. Type `=Ban Clear \"Glorp Name\"` to clear one of your occupied slots.")
    elif glorp_name and open_ban_slots > 0:

        glorp_ban_request = database_calls.GlorpDB().GetBannableGlorpInfo(glorp_name)
        if not glorp_ban_request:
            await ctx.reply(f"{glorp_name.title()} is not a valid Glorp name. Use the `=View` command to see the Glorps in your collection.")
        elif not glorp_ban_request[1]:
            await ctx.reply(f"There is no need to waste a banishment slot on `{glorp_name.title()}`. It cannot be obtained from spinning the wheel.")
        else:
            duplicate_ban = False
            for row in banned_glorps:
                if row[0] == glorp_ban_request[0]:
                    duplicate_ban = True
            if duplicate_ban:
                await ctx.reply(f"`{glorp_name.title()}` is already filling a banishment slot. There is no need to banish it again.")
            else:
                database_calls.GlorpDB().AddGlorpToUserBanList(user_id, glorp_ban_request[2])
                await ctx.reply(f":prohibited: `{glorp_name.title()}` was added to your list of banished Glorps.\n\n-# This Glorp will no longer be awarded for spinning the wheel...")
                
    else:
        await ctx.reply(":dizzy_face: You have confused Glorp_Bot! I'm not sure what you're trying to do.")
    return


def BanClearCommand(command):
    return command.lower() == "clear" or command.lower() == "remove" or command.lower() == "delete"

@client.command(help = "Sacrifice your Glorps to the Blood God", aliases = ["Sac", "Sacrifice", "Destroy"])
async def kill(ctx, glorp_name: str = commands.parameter(default="", description="The name of a Glorp in your collection.")):
    if not glorp_name:
        await ctx.reply("# :knife: Sacrificing\n\nType `=Kill \"Glorp Name\"` to sacrifice a Glorp. Another path to power, but at what cost?\n\n-# The Blood God demands sacrifice...")
        return
        
    glorp_name = glorp_name.title()
    user_id = ctx.message.author.id
    kill_glorp_data = database_calls.GlorpDB.GlorpInUsersCollection(user_id, glorp_name)

    if not database_calls.GlorpDB().UserHasPrisonCardInCollection(user_id):
        await ctx.reply(":knife: You must have the tools to confine them before you can sacrifice them.\n\n-# Perhaps a prison of their own making...")
        return

    if not kill_glorp_data:
        await ctx.reply("You cannot sacrifice what you do not possess. Type `=View` to see the Glorps in your collection.")
    elif not kill_glorp_data[4]:
        await ctx.reply(f"`{glorp_name}` is much too powerful to be destroyed! Type `=View` to find weaker prey.")
    else:
        sac_points = database_calls.GlorpDB().GetUsersSacrificePoints(user_id)
        sac_points += format_bot_response.GlorpResponses().GetSacrificePointsFromGlorpCard(kill_glorp_data[1])
        if sac_points < 8:
            database_calls.GlorpDB().UpdateUserSacrificePoints(user_id, sac_points)
            sugar_text = format_bot_response.GlorpResponses().GetSacricicePointsDescription(sac_points)
            await ctx.reply(f":knife: You cast the soul of `{glorp_name}` into the ether...\n\n-# {sugar_text}")
        else:
            glorp_data = database_calls.GlorpDB().GetSacrificeRewards(user_id)
            database_calls.GlorpDB().UpdateUserSacrificePoints(user_id, 0)
            await ctx.reply(f":knife: You cast the soul of `{glorp_name}` into the ether...\n\n-# *The ritual is complete! A web of cracks form upon the floor... something emerges?*")
            if glorp_data:
                    for i, glorp in enumerate(glorp_data["glorp_data"]):
                        file_path = format_bot_response.GlorpResponses().GetImagePath(file_name = glorp[1])
                        glorp_description = format_bot_response.GlorpResponses().GetSpinOutcomeText(glorp[2], glorp[3], "sacrifice", glorp_data["eye_count"])
                        await ctx.reply(content = glorp_description, file=discord.File(file_path))
                    database_calls.GlorpDB().DeleteMultipleGlorpsFromUsersCollection(user_id, [35]) #Consume prison (35)
                    await ctx.reply("The `Prison` contorts and shatters into spirals of rended metal.\n\n-# You'll need to obtain a new prison for the sacrifices to continue...")
            else:
                await ctx.reply(":dizzy_face: Oh no! The ritual has failed. Was there an error in my calculations?")
        
        database_calls.GlorpDB().DeleteSacrificedGlorpFromUsersCollection(user_id, kill_glorp_data[2])
        return

@client.command(help = "Gamble away your Glorps for rarer ones", aliases = ["Bet"])
async def gamble(ctx, glorp_name: str = commands.parameter(default="", description="The name of a Glorp in you collection.")):
    if not glorp_name:
        await ctx.reply("# :game_die: Gambling\n\nType `=Gamble \"Glorp Name\"` to wager a card and gamble for spins.\n\n-# Gambling a card does not guarantee a reward...")
        return
    
    glorp_name = glorp_name.title()
    user_id = ctx.message.author.id
    gamble_glorp_data = database_calls.GlorpDB.GlorpInUsersCollection(user_id, glorp_name)

    if not gamble_glorp_data:
        await ctx.reply("You cannot gamble what you do not own. Type `=View` to see the Glorps in your collection.")
    elif not gamble_glorp_data[3]:
        await ctx.reply(f"`{glorp_name}` is much too valuable to be gambled away! Type `=View` to find something more expendable.")
    else:
        structured_gamble_data = database_calls.GlorpDB.ParseGlorpDataForGambling(gamble_glorp_data)
        await ctx.reply(f":game_die: You have wagered `{glorp_name}`. It is worth {structured_gamble_data["spins"]} spins on the wheel, but awards are not guaranteed.\n\n-# *The wheel is spinning...*")
        await asyncio.sleep(1)
        glorp_data = database_calls.GlorpDB.GambleGlorp(user_id, structured_gamble_data)
        if not glorp_data:
            await ctx.reply(":dizzy_face: Oh no! The Glorp casino seems to be experiencing some issues.")
        else:
            if glorp_data == "Bust":
                await ctx.reply(f":cry: Sorry, but fate did not smile upon you. Better luck next time.\n\n-# The wager has been settled and `{glorp_name}` was removed from your collection.")
            else:
                file_path = format_bot_response.GlorpResponses().GetImagePath(file_name = glorp_data[1])
                glorp_description = format_bot_response.GlorpResponses().GetSpinOutcomeText(glorp_data[2], glorp_data[3])
                await ctx.reply(content=glorp_description, file=discord.File(file_path))
                await ctx.reply(f"The wager has been settled. A `{glorp_name}` was removed from your collection.")

@client.command(help = "Combine your Glorps to craft new ones", aliases = ["Make", "Build", "Create"])
async def craft(ctx, glorp_name: str = commands.parameter(default="", description="The name of a Glorp in you collection.")):
    user_id =  ctx.message.author.id
    if not glorp_name:
        craft_recipes = open(crafting_recipes_file).read()
        await ctx.reply(craft_recipes)
        return
    glorp_data = database_calls.GlorpDB().GetCraftableGlorp(glorp_name)
    if not glorp_data:
        await ctx.reply("That is not a craftable Glorp. Type `=Craft` for a list of craftable Glorps and their ingredients.")
        return
    missing_ingredients = database_calls.GlorpDB().UserIsMissingIngredients(user_id, glorp_data["ingredients"].copy())
    if missing_ingredients:
        await ctx.reply(f":rage: You cannot craft `{glorp_name.title()}` without the necessary ingredients. You have angered Glorp_Bot!")
        return
    
    await CraftingSugarText(ctx, glorp_name.title())
    new_glorp_data = database_calls.GlorpDB().CraftGlorp(user_id, glorp_data["glorp_id"], glorp_data["ingredients"])
    if new_glorp_data:
        file_path = format_bot_response.GlorpResponses().GetImagePath(file_name = new_glorp_data[1])
        glorp_description = format_bot_response.GlorpResponses().GetSpinOutcomeText(new_glorp_data[2], new_glorp_data[3], "craft")
        await ctx.reply(file=discord.File(file_path))
        await ctx.reply(glorp_description)
        database_calls.GlorpDB().DeleteMultipleGlorpsFromUsersCollection(user_id, glorp_data["ingredients"])
    else:
        await ctx.reply(":dizzy_face: Oh no! There was a problem at the Glorp factory and the crafting failed.")
    return

async def CraftingSugarText(ctx, glorp_name):
    await ctx.reply(f"# Crafting {glorp_name}")
    await asyncio.sleep(1)
    await ctx.reply(f"-# *Your Glorps are consumed as you complete the ritual...*")
    await asyncio.sleep(1)

async def WheelSpinSugarText(ctx, sugar_text):
    if not sugar_text:
        lines = open(spin_sugar_file).read().splitlines()
        sugar_text = random.choice(lines).rstrip()
    await ctx.reply(f"{sugar_text}\n-# *The wheel is spinning...*")
    await asyncio.sleep(1)
    return

@client.command(help = "Spin the wheel to win a Glorp")
async def spin(ctx):
    user_id = ctx.message.author.id
    user_name = ctx.message.author.global_name.title()
    if not database_calls.GlorpDB().UserIsBelowGlorpLimit(user_id):
        await ctx.reply("You have reached the Glorp limit. You must sacrifice, gamble or craft away a Glorp before you may spin again.")
        return
    last_spin_delta = database_calls.GlorpDB.GetSecondsElapsedSinceLastUserSpin(user_id, user_name)
    if database_calls.GlorpDB().UserCanSpin(last_spin_delta):

        lines = open(spin_sugar_file).read().splitlines()
        sugar_text = random.choice(lines).rstrip()
        await ctx.reply(f"# Spin the Wheel\n\n{sugar_text}\n\n-# *The wheel is spinning...*")
        await asyncio.sleep(1)

        glorp_data = database_calls.GlorpDB().SpinForGlorp(user_id)
        if len(glorp_data) > 1:
            await ctx.reply("-# *Something is happening... the wheel has become enraged!*")
        if glorp_data:
                for i, glorp in enumerate(glorp_data):
                    file_path = format_bot_response.GlorpResponses().GetImagePath(file_name = glorp[1])
                    glorp_description = format_bot_response.GlorpResponses().GetSpinOutcomeText(glorp[2], glorp[3], "spin")
                    await ctx.reply(content=glorp_description, file=discord.File(file_path))
        else:
            await ctx.reply(":dizzy_face: Oh no! The Glorp wheel seems to have become enraged and malfuctioned.")
    else:
        time_until_next_spin = database_calls.GlorpDB.FormatTimeUntilNextSpinFromSeconds(last_spin_delta)
        await ctx.reply(f"Greed will not grant you Glorps. You may spin again in {time_until_next_spin}")
    return

# Bot connected
@client.event
async def on_ready():
    print("Success: Glorp_Bot is connected to Discord.")
    change_status.start()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        print(f"{ctx.message.author.global_name.title()} issued the following invalid command to Glorp_Bot: ={ctx.invoked_with}")
        return
    raise error

# Bot start
auth_code = open(auth_code_file).read()
client.run(auth_code)