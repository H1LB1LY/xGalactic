"""
xGalactic — Grok-Powered Galactic Standard Translator for Discord

The X-like translation experience for international Discord servers.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.db import Database
from utils.grok import GrokClient
from utils.rate_limit import default_limiters

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("xgalactic")

COGS = [
    "cogs.translation",
    "cogs.mirroring",
    "cogs.onboarding",
    "cogs.config",
    "cogs.stats",
]

# Least-privilege intents
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.reactions = True
INTENTS.members = True
INTENTS.guilds = True


class XGalacticBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=INTENTS,
            help_command=None,
        )
        self.db = Database()
        self.grok = GrokClient()
        self.guild_limiter, self.user_limiter = default_limiters()

    async def setup_hook(self) -> None:
        await self.db.connect()
        for ext in COGS:
            try:
                await self.load_extension(ext)
                logger.info("Loaded extension %s", ext)
            except Exception:
                logger.exception("Failed to load %s", ext)
        # Sync slash commands globally (use guild-specific for dev)
        await self.tree.sync()
        logger.info("Slash commands synced")

    async def on_ready(self) -> None:
        logger.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "?")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="🌍 flag reactions · /groktranslate",
        )
        await self.change_presence(activity=activity)


async def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not set. Copy .env.example to .env")
        sys.exit(1)

    bot = XGalacticBot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down.")
