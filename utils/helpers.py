"""Shared helpers for cogs: API keys, budget checks, user language."""

from __future__ import annotations

import os

import discord

from utils.db import Database
from utils.flags import ROLE_TO_LANGUAGE
from utils.rate_limit import RateLimiter


async def get_guild_api_key(db: Database, guild_id: int) -> str | None:
    cfg = await db.get_guild_config(guild_id)
    if cfg and cfg.get("xai_api_key"):
        return cfg["xai_api_key"]
    return os.getenv("XAI_API_KEY")


async def get_guild_model(db: Database, guild_id: int) -> str:
    cfg = await db.get_guild_config(guild_id)
    if cfg and cfg.get("grok_model"):
        return cfg["grok_model"]
    return os.getenv("GROK_MODEL", "grok-4.1-fast")


async def is_guild_paused(db: Database, guild_id: int) -> tuple[bool, str | None]:
    if await db.is_budget_exceeded(guild_id):
        return True, "Monthly Grok budget cap reached. Contact a server admin."
    cfg = await db.get_guild_config(guild_id)
    if cfg and cfg.get("paused"):
        return True, "Translation is paused on this server."
    return False, None


def check_rate_limits(
    guild_limiter: RateLimiter,
    user_limiter: RateLimiter,
    guild_id: int,
    user_id: int,
) -> str | None:
    gkey = f"guild:{guild_id}"
    ukey = f"user:{user_id}"
    if not guild_limiter.check(gkey):
        return f"Server rate limit reached. Retry in {guild_limiter.retry_after(gkey):.0f}s."
    if not user_limiter.check(ukey):
        return f"Your rate limit reached. Retry in {user_limiter.retry_after(ukey):.0f}s."
    return None


def user_preferred_language(member: discord.Member) -> str:
    """Infer language from member's language roles, else English."""
    for role in member.roles:
        key = role.name.lower().lstrip("@")
        if key in ROLE_TO_LANGUAGE:
            return ROLE_TO_LANGUAGE[key]
    return "English"


async def log_to_channel(
    guild: discord.Guild,
    db: Database,
    embed: discord.Embed,
) -> None:
    cfg = await db.get_guild_config(guild.id)
    if not cfg or not cfg.get("log_channel_id"):
        return
    ch = guild.get_channel(cfg["log_channel_id"])
    if isinstance(ch, discord.TextChannel):
        try:
            await ch.send(embed=embed)
        except discord.HTTPException:
            pass
