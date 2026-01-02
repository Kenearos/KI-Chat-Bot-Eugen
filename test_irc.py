#!/usr/bin/env python3
"""
Simple IRC test to see if messages are received
"""
import irc.bot
from dotenv import load_dotenv
import os

load_dotenv()

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        token = os.getenv("TWITCH_OAUTH_TOKEN")
        nickname = os.getenv("TWITCH_BOT_NICKNAME")
        channel = os.getenv("TWITCH_CHANNEL")

        print(f"Bot: {nickname}")
        print(f"Channel: {channel}")
        print(f"Token: {token[:15]}...")

        irc.bot.SingleServerIRCBot.__init__(
            self,
            [("irc.chat.twitch.tv", 6667, token)],
            nickname,
            nickname
        )
        self.channel = channel

    def on_welcome(self, connection, event):
        print(f"✅ Connected! Joining {self.channel}")
        connection.cap("REQ", ":twitch.tv/membership")
        connection.cap("REQ", ":twitch.tv/tags")
        connection.cap("REQ", ":twitch.tv/commands")
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        username = event.source.nick
        message = event.arguments[0]
        print(f"📨 MESSAGE | {username}: {message}")

if __name__ == "__main__":
    print("Starting IRC test bot...")
    print("Write a message in your Twitch chat!")
    print("Press Ctrl+C to stop")
    print()

    bot = TestBot()
    bot.start()
