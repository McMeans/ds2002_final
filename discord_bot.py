import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from services.recipe_service import RecipeService
from services.gemini_service import GeminiService

load_dotenv()
recipe_service = RecipeService()
gemini_service = GeminiService()

# set up bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# store conversation history for each user
conversation_histories = {}

@bot.event
async def on_ready():
    # connection
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='chat')
async def chat(ctx, *, message):
    # retrieve/create conversation history for the user
    user_id = str(ctx.author.id)
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    
    # show typing indicator
    async with ctx.typing():
        try:
            # search for recipes
            recipes = recipe_service.search_recipes_db(message)
            if not recipes:
                recipes = recipe_service.search_spoonacular(message)
            
            # generate response
            context = {'recipes': recipes} if recipes else None
            response = gemini_service.generate_response(
                message,
                context,
                conversation_histories[user_id]
            )
            
            # update conversation history
            conversation_histories[user_id].append({
                'role': 'user',
                'content': message
            })
            conversation_histories[user_id].append({
                'role': 'assistant',
                'content': response
            })
            
            # send response
            await ctx.send(response)
            
        except Exception as e:
            # handle error
            print(f"Error in Discord chat: {e}")
            await ctx.send("Sorry, I encountered an error. Please try again.")

@bot.command(name='clear')
async def clear(ctx):
    # clear conversation history for the user
    user_id = str(ctx.author.id)
    conversation_histories[user_id] = []
    await ctx.send("Conversation history cleared!")

# run bot
bot.run(os.getenv('DISCORD_TOKEN')) 