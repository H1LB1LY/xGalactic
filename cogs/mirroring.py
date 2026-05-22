"""Linked-channel auto-mirroring via webhooks with edit/delete sync."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import Database
from utils.embeds import error_embed, success_embed
from utils.flags import resolve_language_name
from utils.grok import GrokClient
from utils.helpers import get_guild_api_key, get_guild_model, is_guild_paused
from utils.security import sanitize_webhook_name

logger = logging.getLogger(__name__)


class MirroringCog(commands.Cog):
    """Opt-in channel mirroring with webhook-native appearance."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db  # type: ignore[attr-defined]
        self.grok: GrokClient = bot.grok  # type: ignore[attr-defined]

    mirror_group = app_commands.Group(
        name="setup-mirroring",
        description="Link channels for automatic Grok-translated mirroring",
    )

    @mirror_group.command(name="link", description="Link source channel to target (translated)")
    @app_commands.describe(
        source="Channel messages originate from",
        target="Channel where translations are posted",
        language="Target language for this mirror",
    )
    @app_commands.default_permissions(manage_channels=True)
    async def link_channels(
        self,
        interaction: discord.Interaction,
        source: discord.TextChannel,
        target: discord.TextChannel,
        language: str,
    ) -> None:
        if not interaction.guild:
            return
        lang = resolve_language_name(language) or language
        webhook = await target.create_webhook(name="xGalactic Mirror")
        pair_id = await self.db.add_mirror_pair(
            interaction.guild.id,
            source.id,
            target.id,
            lang,
            webhook_id=webhook.id,
            webhook_token=webhook.token,
        )
        await interaction.response.send_message(
            embed=success_embed(
                f"Mirroring **{source.mention}** → **{target.mention}** ({lang}).\n"
                f"Pair ID: `{pair_id}`"
            ),
            ephemeral=True,
        )

    @mirror_group.command(name="unlink", description="Remove a mirror link")
    @app_commands.describe(source="Source channel", target="Target channel")
    @app_commands.default_permissions(manage_channels=True)
    async def unlink_channels(
        self,
        interaction: discord.Interaction,
        source: discord.TextChannel,
        target: discord.TextChannel,
    ) -> None:
        if not interaction.guild:
            return
        removed = await self.db.remove_mirror_pair(
            interaction.guild.id, source.id, target.id
        )
        if removed:
            await interaction.response.send_message(
                embed=success_embed("Mirror link removed."),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=error_embed("No mirror link found for those channels."),
                ephemeral=True,
            )

    @mirror_group.command(name="list", description="List active mirror pairs")
    @app_commands.default_permissions(manage_channels=True)
    async def list_mirrors(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return
        pairs = await self.db.list_mirror_pairs(interaction.guild.id)
        if not pairs:
            await interaction.response.send_message(
                embed=error_embed("No mirror pairs configured."),
                ephemeral=True,
            )
            return
        lines = []
        for p in pairs:
            src = interaction.guild.get_channel(p["source_channel_id"])
            tgt = interaction.guild.get_channel(p["target_channel_id"])
            lines.append(
                f"• {src.mention if src else p['source_channel_id']} → "
                f"{tgt.mention if tgt else p['target_channel_id']} "
                f"({p['target_language']})"
            )
        await interaction.response.send_message(
            embed=success_embed("\n".join(lines)),
            ephemeral=True,
        )

    async def _mirror_message(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot or not message.content.strip():
            return

        paused, _ = await is_guild_paused(self.db, message.guild.id)
        if paused:
            return

        pairs = await self.db.get_mirror_pairs_for_source(
            message.guild.id, message.channel.id
        )
        if not pairs:
            return

        api_key = await get_guild_api_key(self.db, message.guild.id)
        model = await get_guild_model(self.db, message.guild.id)

        for pair in pairs:
            try:
                result = await self.grok.translate(
                    message.content,
                    pair["target_language"],
                    api_key=api_key,
                    model=model,
                )
            except Exception:
                logger.exception("Mirror translation failed for pair %s", pair.get("id"))
                continue

            await self.db.log_usage(
                message.guild.id,
                message.author.id,
                result.prompt_tokens,
                result.completion_tokens,
                result.model,
            )

            target_ch = message.guild.get_channel(pair["target_channel_id"])
            if not isinstance(target_ch, discord.TextChannel):
                continue

            try:
                webhook = await self.bot.fetch_webhook(pair["webhook_id"])
            except (discord.NotFound, discord.HTTPException):
                webhook = await target_ch.create_webhook(name="xGalactic Mirror")
                await self.db.add_mirror_pair(
                    message.guild.id,
                    pair["source_channel_id"],
                    target_ch.id,
                    pair["target_language"],
                    webhook_id=webhook.id,
                    webhook_token=webhook.token,
                )

            wh_msg = await webhook.send(
                content=result.text,
                username=sanitize_webhook_name(message.author.display_name),
                avatar_url=message.author.display_avatar.url,
                wait=True,
            )

            await self.db.map_mirror_message(message.id, wh_msg.id, pair["id"])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self._mirror_message(message)

async def setup(bot: commands.Bot) -> None:
    cog = MirroringCog(bot)
    await bot.add_cog(cog)

    