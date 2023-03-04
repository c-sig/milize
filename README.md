project management bot built with discord.py

built for scanlation


# Setup
How to setup:
1. Download .ZIP and unzip it.

2. Put in the values for these settings:
prefix = '!'
TOKEN = '' # Your bot's token.
application_id = 123 # Your bot's ID (integer)
sg = '' # Your scanlation group name.

3. Start the bot by running main.py (or run.bat on windows)

4. Navigate to `/bot/configs` and input your Discord ID (Something like 1019070453509259315) to botowners.txt

5.
Run `{prefix}sync` and `{prefix}updatelist` (replace {prefix} with the prefix you specified.)

6.
Run `/help` for all the commands! You're all done!

# Information
To add bot owners, put another id into `/bot/configs/botowners.txt` on a new line, and run `{prefix}updatelist`.
To add a scanlation group owner (who can add members), run `/group addscanowner`. Run `/group removescanowner` to remove.
To add a scanlation group member, run `/group addscanmember`. Run `/group removescanmember` to remove.
