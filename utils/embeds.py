"""Discord embed builders for xGalactic."""

from __future__ import annotations

import discord

BRAND_COLOR = 0x1DA1F2  # X-like blue
ERROR_COLOR = 0xE0245E
SUCCESS_COLOR = 0x17BF63


def translation_embed(
    translation: str,
    language: str,
    *,
    original_author: str | None = None,
    model: str = "grok-4.1-fast",
) -> discord.Embed:
    """X-style Grok translation embed."""
    embed = discord.Embed(
        title=f"🌍 Grok Translation → {language}",
        description=translation[:4096],
        color=BRAND_COLOR,
    )
    if original_author:
        embed.set_footer(text=f"Original by {original_author} · {model}")
    else:
        embed.set_footer(text=f"Powered by Grok · {model}")
    return embed


def error_embed(message: str) -> discord.Embed:
    return discord.Embed(title="xGalactic", description=message, color=ERROR_COLOR)


def success_embed(message: str) -> discord.Embed:
    return discord.Embed(title="xGalactic", description=message, color=SUCCESS_COLOR)


def stats_embed(
    *,
    total_requests: int,
    total_tokens: int,
    estimated_cost_usd: float,
    budget_cap: float | None,
    budget_used_pct: float | None,
    model: str,
    period_days: int = 30,
) -> discord.Embed:
    embed = discord.Embed(
        title="📊 xGalactic Usage Stats",
        color=BRAND_COLOR,
    )
    embed.add_field(name="Total Translations", value=str(total_requests), inline=True)
    embed.add_field(name="Est. Tokens Used", value=f"{total_tokens:,}", inline=True)
    embed.add_field(
        name=f"Est. Cost ({period_days}d)",
        value=f"${estimated_cost_usd:.4f}",
        inline=True,
    )
    embed.add_field(name="Active Model", value=model, inline=True)
    if budget_cap is not None:
        pct = budget_used_pct or 0
        embed.add_field(
            name="Monthly Budget",
            value=f"${budget_cap:.2f} ({pct:.1f}% used)",
            inline=True,
        )
    embed.set_footer(text="Admin pays all Grok usage · Pay-as-you-go billing")
    return embed
