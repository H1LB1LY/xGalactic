"""Admin configuration: API key, model toggle, budget, style, logging."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import Database
from utils.embeds import error_embed, success_embed

VALID_MODELS = ("grok-4.1-fast", "grok-4.3")


class ConfigCog(commands.Cog):
    """Guild-level admin settings (admin pays for all Grok usage)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db  # type: ignore[attr-defined]

    config_group = app_commands.Group(
        name="config",
        description="xGalactic server configuration (admin only)",
    )

    @config_group.command(name="api-key", description="Set guild xAI API key (admin only)")
    @app_commands.describe(api_key="Your xAI API key from console.x.ai")
    @app_commands.default_permissions(administrator=True)
    async def set_api_key(
        self, interaction: discord.Interaction, api_key: str
    ) -> None:
        if not interaction.guild:
            return
        key = api_key.strip()
        if len(key) < 10:
            await interaction.response.send_message(
                embed=error_embed("Invalid API key format."),
                ephemeral=True,
            )
            return
        await self.db.upsert_guild_config(
            interaction.guild.id, xai_api_key=key
        )
        await interaction.response.send_message(
            embed=success_embed(
                "xAI API key saved for this server. "
                "It is stored locally in your database — never shared."
            ),
            ephemeral=True,
        )

    @config_group.command(name="model", description="Toggle Grok model")
    @app_commands.describe(model="grok-4.1-fast (default) or grok-4.3")
    @app_commands.choices(
        model=[
            app_commands.Choice(name="grok-4.1-fast (fast)", value="grok-4.1-fast"),
            app_commands.Choice(name="grok-4.3 (higher quality)", value="grok-4.3"),
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def set_model(self, interaction: discord.Interaction, model: str) -> None:
        if not interaction.guild:
            return
        if model not in VALID_MODELS:
            await interaction.response.send_message(
                embed=error_embed(f"Model must be one of: {', '.join(VALID_MODELS)}"),
                ephemeral=True,
            )
            return
        await self.db.upsert_guild_config(interaction.guild.id, grok_model=model)
        await interaction.response.send_message(
            embed=success_embed(f"Grok model set to **{model}**."),
            ephemeral=True,
        )

    @config_group.command(
        name="budget",
        description="Set monthly USD budget cap (bot pauses when reached)",
    )
    @app_commands.describe(monthly_usd="Monthly cap in USD (0 to disable)")
    @app_commands.default_permissions(administrator=True)
    async def set_budget(
        self, interaction: discord.Interaction, monthly_usd: float
    ) -> None:
        if not interaction.guild:
            return
        cap = monthly_usd if monthly_usd > 0 else None
        await self.db.upsert_guild_config(
            interaction.guild.id, monthly_budget_usd=cap
        )
        if cap:
            msg = f"Monthly budget cap set to **${cap:.2f}**."
        else:
            msg = "Monthly budget cap disabled."
        await interaction.response.send_message(embed=success_embed(msg), ephemeral=True)

    @config_group.command(
        name="style",
        description="Custom translation style hint for this server",
    )
    @app_commands.describe(
        style="e.g. 'formal business', 'casual gaming', 'preserve all slang'"
    )
    @app_commands.default_permissions(administrator=True)
    async def set_style(self, interaction: discord.Interaction, style: str) -> None:
        if not interaction.guild:
            return
        await self.db.upsert_guild_config(
            interaction.guild.id, translation_style=style[:500]
        )
        await interaction.response.send_message(
            embed=success_embed("Translation style updated."),
            ephemeral=True,
        )

    @config_group.command(
        name="log-channel",
        description="Channel for moderation / bot event logs",
    )
    @app_commands.default_permissions(administrator=True)
    async def set_log_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        if not interaction.guild:
            return
        await self.db.upsert_guild_config(
            interaction.guild.id, log_channel_id=channel.id
        )
        await interaction.response.send_message(
            embed=success_embed(f"Log channel set to {channel.mention}."),
            ephemeral=True,
        )

    @config_group.command(
        name="auto-detect",
        description="Enable auto language detection on messages",
    )
    @app_commands.describe(enabled="Toggle auto detection")
    @app_commands.default_permissions(administrator=True)
    async def set_auto_detect(
        self, interaction: discord.Interaction, enabled: bool
    ) -> None:
        if not interaction.guild:
            return
        await self.db.upsert_guild_config(
            interaction.guild.id, auto_detect_language=int(enabled)
        )
        await interaction.response.send_message(
            embed=success_embed(
                f"Auto language detection {'enabled' if enabled else 'disabled'}."
            ),
            ephemeral=True,
        )

    @config_group.command(name="pause", description="Pause all Grok translations")
    @app_commands.describe(paused="Pause or resume")
    @app_commands.default_permissions(administrator=True)
    async def set_pause(self, interaction: discord.Interaction, paused: bool) -> None:
        if not interaction.guild:
            return
        await self.db.upsert_guild_config(interaction.guild.id, paused=int(paused))
        await interaction.response.send_message(
            embed=success_embed(
                "Translations **paused**." if paused else "Translations **resumed**."
            ),
            ephemeral=True,
        )

    @config_group.command(name="show", description="Show current server config")
    @app_commands.default_permissions(manage_guild=True)
    async def show_config(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return
        cfg = await self.db.get_guild_config(interaction.guild.id)
        if not cfg:
            await interaction.response.send_message(
                embed=error_embed("No custom config — using environment defaults."),
                ephemeral=True,
            )
            return
        has_key = "✅" if cfg.get("xai_api_key") else "❌ (using .env)"
        embed = discord.Embed(title="xGalactic Config", color=0x1DA1F2)
        embed.add_field(name="API Key", value=has_key, inline=True)
        embed.add_field(name="Model", value=cfg.get("grok_model", "grok-4.1-fast"), inline=True)
        budget = cfg.get("monthly_budget_usd")
        embed.add_field(
            name="Budget Cap",
            value=f"${budget:.2f}" if budget else "None",
            inline=True,
        )
        embed.add_field(
            name="Paused",
            value="Yes" if cfg.get("paused") else "No",
            inline=True,
        )
        embed.add_field(
            name="Auto Detect",
            value="Yes" if cfg.get("auto_detect_language") else "No",
            inline=True,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    cog = ConfigCog(bot)
    await bot.add_cog(cog)
#    bot.tree.add_command(cog.config_group)  <-- commented out to avoid duplicate commands
