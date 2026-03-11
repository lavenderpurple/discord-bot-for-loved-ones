# This is the Python code for your bot.
# You will need to install these libraries first.
# Open your terminal or command prompt and type:
# pip install discord.py
# pip install aiohttp
# pip install nltk
import os
from dotenv import load_dotenv

load_dotenv()
import discord
import aiohttp # Used to make requests to APIs
import random
import json
import os # Still needed for os.path.exists
import re # For cleaning text
from collections import Counter # For counting words
try:
    import nltk
    from nltk.corpus import stopwords
except ImportError:
    print("NLTK library not found. Please run: pip install nltk")
    exit()

# --- BOT SETUP ---
# 'intents' tell Discord what your bot needs permission to "see".
# We need the 'message_content' intent to read messages.
intents = discord.Intents.default()
intents.message_content = True

# 'client' is our connection to Discord.
client = discord.Client(intents=intents)

# --- USER CONFIGURATION ---
# This will store all trigger configurations
# The structure will be:
# { 
#   "owner_id_1": {
#     "target_user_id": 12345,
#     "triggers": {"hi": "hello"},
#     "is_logging_enabled": False
#   },
#   "owner_id_2": { ... }
# }
MASTER_TRIGGER_CONFIG = {} 
MESSAGE_LOG = {} # Will hold logged messages, e.g., {"target_id": ["msg1", "msg2"]}

# This file will store the config so the bot remembers after a restart
CONFIG_FILE = "bot_config.json"
MESSAGE_LOG_FILE = "message_log.json"

# --- CONFIG HELPER FUNCTIONS ---

def load_config():
    """Loads config from CONFIG_FILE into global variables."""
    global MASTER_TRIGGER_CONFIG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                MASTER_TRIGGER_CONFIG = config.get("trigger_configs", {})
                print(f"Loaded {len(MASTER_TRIGGER_CONFIG)} owner configurations.")
        except Exception as e:
            print(f"Error loading {CONFIG_FILE}: {e}")
            MASTER_TRIGGER_CONFIG = {}
    else:
        print(f"{CONFIG_FILE} not found, using default empty config.")
        MASTER_TRIGGER_CONFIG = {}

def save_config():
    """Saves the current global config variables to CONFIG_FILE."""
    global MASTER_TRIGGER_CONFIG
    try:
        with open(CONFIG_FILE, 'w') as f:
            config = {"trigger_configs": MASTER_TRIGGER_CONFIG}
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config file: {e}")
        return False

def load_message_log():
    """Loads message log from MESSAGE_LOG_FILE."""
    global MESSAGE_LOG
    if os.path.exists(MESSAGE_LOG_FILE):
        try:
            with open(MESSAGE_LOG_FILE, 'r') as f:
                MESSAGE_LOG = json.load(f)
                print(f"Loaded message logs for {len(MESSAGE_LOG)} users.")
        except Exception as e:
            print(f"Error loading {MESSAGE_LOG_FILE}: {e}")
            MESSAGE_LOG = {}
    else:
        print(f"{MESSAGE_LOG_FILE} not found, starting with empty log.")
        MESSAGE_LOG = {}

def save_message_log():
    """Saves the current message log to MESSAGE_LOG_FILE."""
    global MESSAGE_LOG
    try:
        with open(MESSAGE_LOG_FILE, 'w') as f:
            json.dump(MESSAGE_LOG, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving message log: {e}")
        return False

# --- NLTK Setup ---
def setup_nltk():
    """Downloads necessary NLTK data."""
    try:
        nltk.data.find('corpora/stopwords')
        print("NLTK stopwords already downloaded.")
    except LookupError:
        print("Downloading NLTK stopwords...")
        nltk.download('stopwords')
        print("Download complete.")

# --- API URLs ---
# These are free APIs that give us random cute pictures.
CAT_API_URL = "https://aws.random.cat/meow"
DOG_API_URL = "https://random.dog/woof.json"

# --- CUTE LISTS ---
# Add your own messages and gif links to these lists!
CUTE_MESSAGES = [
    "You're my favorite person! (ɔˆ ³(ˆ⌣ˆc)",
    "I'm so lucky to have you. ❤️",
    "Thinking of you! 💖",
    "You make my heart go... 💓",
    "Sending you a virtual hug!",
    "Hi cutie! (´｡• ᵕ •｡`) ♡"
]

KISS_GIFS = [
    "https://media.tenor.com/gL-8hK8A-nEAAAAC/kiss-love.gif",
    "https://media.tenor.com/h-Q0nE5LIDoAAAAC/love-you-kiss.gif",
    "https.media.tenor.com/2b-s-preoJAAAAAC/kiss-anime.gif",
    "https.media.tenor.com/SgeK-mGbsyMAAAAC/mwah-kiss.gif",
    # You can find more GIFs on sites like Tenor or Giphy and paste the "Share" link here
]

# --- EVENTS ---

@client.event
async def on_ready():
    """This function runs when the bot successfully connects to Discord."""
    setup_nltk() # Download NLTK data if needed
    load_config() # Load all trigger configs
    load_message_log() # Load all past messages
            
    print(f'We have logged in as {client.user}')
    print('Bot is ready and waiting for commands!')
    print('------------------------------------')
    # Set the bot's "Playing" status to show the help command
    await client.change_presence(activity=discord.Game(name="!help for commands"))

@client.event
async def on_message(message):
    """This function runs every time a message is sent in the server."""
    
    # --- FIX for SyntaxError ---
    # This must be at the top of the function
    global MASTER_TRIGGER_CONFIG
    global MESSAGE_LOG
    # ---------------------------
    
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # --- SPECIAL WORD TRIGGER & LOGGING ---
    if not message.content.startswith('!'):
        author_id = message.author.id
        author_id_str = str(author_id)
        
        # Loop through all saved configs
        # config_data = {"target_user_id": 123, "triggers": {...}, "is_logging_enabled": True}
        for owner_id, config_data in MASTER_TRIGGER_CONFIG.items():
            
            # Check if the message author is this owner's target
            if author_id == config_data.get("target_user_id"):
                
                # --- 1. Check for Triggers ---
                target_triggers = config_data.get("triggers", {})
                for trigger, reply in target_triggers.items():
                    if trigger in message.content.lower():
                        await message.reply(reply)
                        # We don't return, in case multiple owners have triggers for this person
                
                # --- 2. Check for Logging ---
                if config_data.get("is_logging_enabled", False):
                    if author_id_str not in MESSAGE_LOG:
                        MESSAGE_LOG[author_id_str] = []
                    MESSAGE_LOG[author_id_str].append(message.content)
                    save_message_log() # Save after logging
        
        return # It was a normal message, no commands to process

    # --- COMMANDS ---

    # Command: !setpartner @user
    if message.content.startswith('!setpartner'):
        
        # Try to delete the user's command message for privacy
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("Bot is missing 'Manage Messages' permission to delete command.")
        except Exception as e:
            print(f"Error deleting message: {e}")

        # Check if a user was mentioned
        if not message.mentions:
            await message.author.send("You need to @mention the user you want to set as your partner! (e.g., `!setpartner @username`)")
            return

        mentioned_user = message.mentions[0]
        owner_id_str = str(message.author.id) # The command user is the owner

        # Create new config for this owner if it doesn't exist
        if owner_id_str not in MASTER_TRIGGER_CONFIG:
            MASTER_TRIGGER_CONFIG[owner_id_str] = {"triggers": {}, "is_logging_enabled": False}

        # Set their target user
        MASTER_TRIGGER_CONFIG[owner_id_str]["target_user_id"] = mentioned_user.id
        
        # Save the config and send private confirmation
        if save_config():
            await message.author.send(
                f"Success! (´• ω •`)♡ I've set {mentioned_user.mention} as your one partner. "
                "You can now use `!addtrigger` to add replies for them."
            )
        else:
            await message.author.send("I set the user, but I had trouble saving the config file. 😥")
        
        return # We're done processing this command

    # Command: !addtrigger "trigger" "reply"
    if message.content.startswith('!addtrigger'):
        
        # Try to delete the user's command message for privacy
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("Bot is missing 'Manage Messages' permission to delete command.")
        except Exception as e:
            print(f"Error deleting message: {e}")

        owner_id_str = str(message.author.id)

        # --- Permission Check ---
        # Check if this user has set a partner
        if owner_id_str not in MASTER_TRIGGER_CONFIG or "target_user_id" not in MASTER_TRIGGER_CONFIG[owner_id_str]:
            await message.author.send("Sorry, you must set a partner first using `!setpartner @user` before adding triggers.")
            return
        # --- End Permission Check ---

        try:
            # Parse the command, e.g., !addtrigger "trigger phrase" "reply phrase"
            command_body = message.content.split("!addtrigger ", 1)[1]
            parts = command_body.split('"')
            
            if len(parts) < 5:
                raise ValueError("Invalid format")

            trigger = parts[1].lower() # Always store trigger as lowercase
            reply = parts[3]
            
            if not trigger or not reply: # Make sure they're not empty
                 raise ValueError("Trigger or reply is empty")

            # Add trigger to this owner's specific trigger list
            MASTER_TRIGGER_CONFIG[owner_id_str]["triggers"][trigger] = reply 
            
            if save_config():
                # Send confirmation privately
                await message.author.send(f"✅ Trigger added! When your partner says `{trigger}`, I will reply.")
            else:
                await message.author.send("Oops, I couldn't save the config file. 😥")
        
        except Exception as e:
            print(f"Error parsing !addtrigger: {e}")
            await message.author.send('Oops! Please use the correct format: `!addtrigger "trigger" "reply"`')
        
        return

    # Command: !removetrigger "trigger"
    if message.content.startswith('!removetrigger'):

        # Try to delete the user's command message for privacy
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("Bot is missing 'Manage Messages' permission to delete command.")
        except Exception as e:
            print(f"Error deleting message: {e}")
        
        owner_id_str = str(message.author.id)

        # --- Permission Check ---
        if owner_id_str not in MASTER_TRIGGER_CONFIG or not MASTER_TRIGGER_CONFIG[owner_id_str].get("triggers"):
            await message.author.send("Sorry, you don't have any triggers to remove. Use `!addtrigger` first.")
            return
        # --- End Permission Check ---

        try:
            # Parse the command, e.g., !removetrigger "trigger phrase"
            command_body = message.content.split("!removetrigger ", 1)[1]
            trigger = command_body.split('"')[1].lower() # Get the text in quotes
            
            if trigger in MASTER_TRIGGER_CONFIG[owner_id_str]["triggers"]:
                # Remove it from this owner's map
                del MASTER_TRIGGER_CONFIG[owner_id_str]["triggers"][trigger] 
                if save_config():
                    await message.author.send(f"🗑️ Trigger removed: `{trigger}`")
                else:
                    await message.author.send("Oops, I couldn't save the config file. 😥")
            else:
                await message.author.send(f"I couldn't find a trigger called `{trigger}` in your list.")
        
        except Exception as e:
            print(f"Error parsing !removetrigger: {e}")
            await message.author.send('Oops! Please use the correct format: `!removetrigger "trigger"`')
        
        return

    # Command: !listtriggers
    if message.content.startswith('!listtriggers'):

        # Try to delete the user's command message for privacy
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("Bot is missing 'Manage Messages' permission to delete command.")
        except Exception as e:
            print(f"Error deleting message: {e}")
        
        owner_id_str = str(message.author.id)

        # --- Permission Check ---
        if owner_id_str not in MASTER_TRIGGER_CONFIG:
            await message.author.send("You don't have any triggers set up yet. Use `!setpartner` and `!addtrigger` to create some.")
            return
        
        my_triggers = MASTER_TRIGGER_CONFIG[owner_id_str].get("triggers", {})
        target_id = MASTER_TRIGGER_CONFIG[owner_id_str].get("target_user_id")
        
        target_name = "your partner"
        if target_id:
            try:
                user = await client.fetch_user(int(target_id))
                target_name = user.display_name
            except Exception:
                target_name = f"User ID {target_id}"
        
        # Build a nice embed to DM to the user
        embed = discord.Embed(
            title=f"Your Special Triggers for {target_name}",
            description=f"Here are all the triggers *you* have set for *your* partner.",
            color=discord.Color.blue()
        )
        
        if not my_triggers:
             embed.description = "You have not set any triggers for your partner yet."
        else:
            for trigger, reply in my_triggers.items():
                embed.add_field(name=f"Trigger: `{trigger}`", value=f"Reply: *\"{reply}\"*", inline=False)
            
        try:
            await message.author.send(embed=embed) # Send to user's DMs
        except discord.errors.Forbidden:
            await message.channel.send(f"{message.author.mention}, I couldn't DM you! Please check your privacy settings.")
        
        return
    
    # Command: !togglelog
    if message.content.startswith('!togglelog'):
        # Try to delete the user's command message for privacy
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("Bot is missing 'Manage Messages' permission to delete command.")
        except Exception as e:
            print(f"Error deleting message: {e}")
        
        owner_id_str = str(message.author.id)

        # --- Permission Check ---
        if owner_id_str not in MASTER_TRIGGER_CONFIG or "target_user_id" not in MASTER_TRIGGER_CONFIG[owner_id_str]:
            await message.author.send("Sorry, you must set a partner first using `!setpartner @user` before you can toggle logging.")
            return
        
        # Get current status, default to False if not set
        current_status = MASTER_TRIGGER_CONFIG[owner_id_str].get("is_logging_enabled", False)
        # Flip the status
        new_status = not current_status
        MASTER_TRIGGER_CONFIG[owner_id_str]["is_logging_enabled"] = new_status
        
        if save_config():
            status_text = "ON" if new_status else "OFF"
            await message.author.send(f"Message logging for your partner is now **{status_text}**.")
        else:
            await message.author.send("Oops, I couldn't save the config file. 😥")
        
        return

    # Command: !suggesttriggers
    if message.content.startswith('!suggesttriggers'):
        # Try to delete the user's command message for privacy
        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("Bot is missing 'Manage Messages' permission to delete command.")
        except Exception as e:
            print(f"Error deleting message: {e}")
            
        owner_id_str = str(message.author.id)

        # --- Permission Check ---
        if owner_id_str not in MASTER_TRIGGER_CONFIG or "target_user_id" not in MASTER_TRIGGER_CONFIG[owner_id_str]:
            await message.author.send("Sorry, you must set a partner first using `!setpartner @user`.")
            return
        
        target_id_str = str(MASTER_TRIGGER_CONFIG[owner_id_str].get("target_user_id"))
        
        if not target_id_str or target_id_str not in MESSAGE_LOG or not MESSAGE_LOG[target_id_str]:
            await message.author.send("I don't have enough message data for your partner yet. Make sure `!togglelog` is on and they have sent some messages.")
            return
            
        # --- Start NLP Processing ---
        try:
            await message.author.send("Analyzing messages... this might take a moment. 🧠")
            
            # 1. Combine all messages into one big text blob
            all_text = " ".join(MESSAGE_LOG[target_id_str])
            
            # 2. Find all words, make lowercase
            all_words = re.findall(r'\b\w+\b', all_text.lower())
            
            # 3. Define stop words (common words to ignore)
            stop_words = set(stopwords.words('english'))
            
            # 4. Add our own custom English and Hinglish words to ignore
            custom_stop_words = [
                # English
                "ok", "yes", "no", "okey", "yea", "yeah", "hmm", "hm", "oh", "lol", "lmao", 
                "u", "r", "im", "pls", "plz", "gonna", "wanna", "ya", "bro", "bruh",
                "like", "actually", "basically", "really",
                
                # Hinglish / Hindi
                "hai", "ka", "ki", "ko", "ke", "kya", "bhi", "aur", "mein", "main", "tum",
                "toh", "tha", "thi", "the", "se", "pe", "par", "ho", "hi", "he", "na",
                "nai", "nahi", "kar", "kuch", "kuchh", "batao", "acha", "accha", "bas",
                "bhai", "toh", "abhi", "bhi", "ek", "do", "woh", "haan", "han", "ab"
            ]
            stop_words.update(custom_stop_words)
            
            # 5. Filter out stop words and short words
            filtered_words = [
                word for word in all_words 
                if word not in stop_words and len(word) > 2 # Ignores 1-2 letter words
            ]
            
            if not filtered_words:
                await message.author.send("I've logged messages, but after filtering, no common words were found. Maybe they need to talk more! 😅")
                return

            # 6. Count the most common words
            word_counts = Counter(filtered_words)
            top_10_words = word_counts.most_common(10)
            
            # 7. Send the results in an embed
            embed = discord.Embed(
                title="Top 10 Trigger Suggestions",
                description="Here are the most common (non-boring) words your partner has said. You can use `!addtrigger` to add them!",
                color=discord.Color.green()
            )
            
            for word, count in top_10_words:
                embed.add_field(name=f"Word: `{word}`", value=f"Used {count} times", inline=False)
                
            await message.author.send(embed=embed)
            
        except Exception as e:
            print(f"Error during trigger suggestion: {e}")
            await message.author.send("An error occurred while analyzing the messages. 😥")
            
        return

    # Command: !hello
    if message.content.startswith('!hello'):
        # Send a reply back to the same channel
        await message.channel.send(f'Hello, {message.author.name}! (◕‿◕)♡')

    # Command: !cat
    if message.content.startswith('!cat'):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(CAT_API_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        await message.channel.send(data['file'])
                    else:
                        await message.channel.send("Sorry, I couldn't get a cat picture right now. 😿")
        except Exception as e:
            print(f"Error fetching cat: {e}")
            await message.channel.send("Oops, something went wrong. 🙀")

    # Command: !dog
    if message.content.startswith('!dog'):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DOG_API_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        await message.channel.send(data['url'])
                    else:
                        await message.channel.send("Sorry, I couldn't get a dog picture right now. 🐶")
        except Exception as e:
            print(f"Error fetching dog: {e}")
            await message.channel.send("Oops, something went wrong. 🦴")

    # Command: !ship
    if message.content.startswith('!ship'):
        if not message.mentions:
            await message.channel.send(
                f"Aww, {message.author.name}! Who do you want to send love to? "
                "Don't forget to @mention them! (e.g., `!ship @your_bf`)"
            )
            return
        
        mentioned_user = message.mentions[0]
        random_message = random.choice(CUTE_MESSAGES)
        random_gif = random.choice(KISS_GIFS)
        
        embed = discord.Embed(
            description=f"**{message.author.name} is sending love to {mentioned_user.mention}!**",
            color=discord.Color.from_rgb(255, 105, 180) # Hot pink!
        )
        embed.add_field(name="A special message for you:", value=f"*{random_message}*", inline=False)
        embed.set_image(url=random_gif) # Set the main image
        
        await message.channel.send(embed=embed)

    # Command: !help
    if message.content.startswith('!help'):
        embed = discord.Embed(
            title="CuteBot Help! ✨",
            description="Here are all the commands I know:",
            color=discord.Color.pink() # You can change the color!
        )
        embed.add_field(name="!hello", value="I'll say hello back to you!", inline=False)
        embed.add_field(name="!cat", value="I'll show you a random cat picture.", inline=False)
        embed.add_field(name="!dog", value="I'll show you a random dog picture.", inline=False)
        embed.add_field(name="!ship @user", value="Send a random cute message and kiss gif to someone special!", inline=False)
        
        embed.add_field(name="--- Special Trigger Commands ---", value="Set up special replies for one target user:", inline=False)
        embed.add_field(name="!setpartner @user", value="Set (or change) your *one* special partner.", inline=False)
        embed.add_field(name='!addtrigger "trigger" "reply"', value='Add a trigger for *your* set partner.', inline=False)
        embed.add_field(name='!removetrigger "trigger"', value='Remove a trigger for *your* set partner.', inline=False)
        embed.add_field(name="!listtriggers", value="I will DM you *your* trigger list for *your* set partner.", inline=False)
        
        embed.add_field(name="--- Trigger Suggestion (NLP) ---", value="Analyze your partner's messages:", inline=False)
        embed.add_field(name="!togglelog", value="Turn message logging for your partner ON or OFF (for privacy).", inline=False)
        embed.add_field(name="!suggesttriggers", value="I'll DM you the Top 10 words your partner uses (if logging is on).", inline=False)
        
        embed.set_footer(text="I hope you have a great day! (´• ω •`)")
        
        await message.channel.send(embed=embed)


# --- RUN THE BOT (FOR VS CODE / LOCAL) ---
# PASTE YOUR BOT TOKEN HERE IN THE QUOTES
try:
    client.run(os.getenv("DISCORD_TOKEN")) # Uses the hidden token
except discord.errors.LoginFailure:
    print("--------------------------------------------------")
    print("Error: Improper token passed.")
    print("Please make sure your token is correct.")
    print("--------------------------------------------------")
except Exception as e:
    print(f"An error occurred: {e}")

