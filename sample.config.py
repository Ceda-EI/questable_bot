# Create a new bot by messaging @BotFather and follow the instructions
# Replace the key by the actual token recieved from BotFather
api_key = "123456789:xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

gifs = [
        "https://media.giphy.com/media/2sXd62t0wSHmp56wNh/giphy.gif",
        "https://media.giphy.com/media/C9xI3u4xE7Xzf10UCx/giphy.gif",
        "https://media.giphy.com/media/LWps4ysfNAKDcxJQ8R/giphy.gif",
        "https://media.giphy.com/media/1wo19g2Fc6d8rqhSvp/giphy.gif",
        "https://media.giphy.com/media/l2vAhfuyG9m9lJQnyS/giphy.gif"
        ]

# Update method
# Available Modes: "polling", "webhook"
update_method = "polling"

# Webhook Config
# Check the following urls for more details
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks

webhook = {"listen": "0.0.0.0",
           "url": "https://example.com/" + api_key,
           "url_path": api_key,
           "port": 9999,
           }
