"""Usage statistics and estimated billing."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import Database
from utils.embeds import stats_embed
from utils.helpers import get_guild_model


class StatsCog(commands.Cog):
    """Real-time usage and estimated monthly cost."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db  # type: ignore[attr-defined]

    @app_commands.command(
        name="stats",
        description="View Grok translation usage and estimated cost",
    )
    @app_commands.default_permissions(manage_guild=True)
    async def stats(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return
        await interaction.response.defer(ephemeral=True)

        usage = await self.db.get_usage_stats(interaction.guild.id, days=30)
        spend = await self.db.get_monthly_spend_estimate(interaction.guild.id)
        cfg = await self.db.get_guild_config(interaction.guild.id)
        budget = (cfg or {}).get("monthly_budget_usd")
        budget_pct = None
        if budget and budget > 0:
            budget_pct = min(100.0, (spend / float(budget)) * 100)

        total_tokens = (usage.get("prompt_tokens") or 0) + (
            usage.get("completion_tokens") or 0
        )

        embed = stats_embed(
            total_requests=usage.get("requests") or 0,
            total_tokens=total_tokens,
            estimated_cost_usd=spend,
            budget_cap=float(budget) if budget else None,
            budget_used_pct=budget_pct,
            model=await get_guild_model(self.db, interaction.guild.id),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCog(bot))
