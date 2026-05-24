"""On-demand Grok translation: flag reactions, context menu, slash command."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import Database
from utils.embeds import error_embed, translation_embed
from utils.flags import flag_to_language, resolve_language_name
from utils.grok import GrokClient
from utils.helpers import (
    check_rate_limits,
    get_guild_api_key,
    get_guild_model,
    is_guild_paused,
    log_to_channel,
    user_preferred_language,
)
from utils.rate_limit import RateLimiter
from utils.security import sanitize_text

logger = logging.getLogger(__name__)


class TranslationCog(commands.Cog):
    """X-like on-demand translation via reactions and commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db  # type: ignore[attr-defined]
        self.grok: GrokClient = bot.grok  # type: ignore[attr-defined]
        self.guild_limiter: RateLimiter = bot.guild_limiter  # type: ignore[attr-defined]
        self.user_limiter: RateLimiter = bot.user_limiter  # type: ignore[attr-defined]

    async def _do_translate(
        self,
        interaction_or_message: discord.Interaction | discord.Message,
        text: str,
        target_language: str,
        *,
        reply_to: discord.Message | None = None,
        defer_ephemeral: bool = False,
    ) -> None:
        if isinstance(interaction_or_message, discord.Interaction):
            guild = interaction_or_message.guild
            user = interaction_or_message.user
            is_interaction = True
        else:
            guild = interaction_or_message.guild
            user = interaction_or_message.author
            is_interaction = False

        if not guild:  # Prevent crash in DMs
            if is_interaction:
                await interaction_or_message.response.send_message(
                    embed=error_embed("This command only works inside servers."), 
                    ephemeral=True
                )
            return

        paused, reason = await is_guild_paused(self.db, guild.id)
        if paused:
            msg = error_embed(reason or "Translation unavailable.")
            if is_interaction:
                if interaction_or_message.response.is_done():
                    await interaction_or_message.followup.send(embed=msg, ephemeral=True)
                else:
                    await interaction_or_message.response.send_message(embed=msg, ephemeral=True)
            return

        rl_msg = check_rate_limits(
            self.guild_limiter, self.user_limiter, guild.id, user.id
        )
        if rl_msg:
            msg = error_embed(rl_msg)
            if is_interaction:
                if not interaction_or_message.response.is_done():
                    await interaction_or_message.response.send_message(embed=msg, ephemeral=True)
                else:
                    await interaction_or_message.followup.send(embed=msg, ephemeral=True)
            return

        api_key = await get_guild_api_key(self.db, guild.id)
        model = await get_guild_model(self.db, guild.id)
        cfg = await self.db.get_guild_config(guild.id)
        style = (cfg or {}).get("translation_style")

        if is_interaction and defer_ephemeral:
            await interaction_or_message.response.defer(ephemeral=True)

        try:
            result = await self.grok.translate(
                text,
                target_language,
                api_key=api_key,
                model=model,
                style_hint=style,
            )
        except ValueError as e:
            embed = error_embed(str(e))
            if is_interaction:
                if interaction_or_message.response.is_done():
                    await interaction_or_message.followup.send(embed=embed, ephemeral=defer_ephemeral)
                else:
                    await interaction_or_message.response.send_message(embed=embed, ephemeral=defer_ephemeral)
            return
        except Exception as e:
            logger.exception("Grok translation failed")
            embed = error_embed(f"Translation failed: {e}")
            if is_interaction:
                if interaction_or_message.response.is_done():
                    await interaction_or_message.followup.send(embed=embed, ephemeral=defer_ephemeral)
                else:
                    await interaction_or_message.response.send_message(embed=embed, ephemeral=defer_ephemeral)
            return

        await self.db.log_usage(
            guild.id,
            user.id,
            result.prompt_tokens,
            result.completion_tokens,
            result.model,
        )

        author_name = None
        if reply_to and reply_to.author:
            author_name = str(reply_to.author.display_name)

        embed = translation_embed(
            result.text,
            target_language,
            original_author=author_name,
            model=result.model,
        )

        if is_interaction:
            await interaction_or_message.followup.send(embed=embed)
        elif isinstance(interaction_or_message, discord.Message):
            await interaction_or_message.reply(embed=embed, mention_author=False)
    
    @app_commands.command(
        name="groktranslate",
        description="Translate text with Grok (X-like natural translation)",
    )
    @app_commands.describe(
        text="Text to translate",
        language="Target language (e.g. Spanish, Japanese)",
    )
    async def groktranslate(
        self,
        interaction: discord.Interaction,
        text: str,
        language: str | None = None,
    ) -> None:
        if not interaction.guild:  # Prevent crash in DMs
            await interaction.response.send_message(
                embed=error_embed("This command only works inside servers."), 
                ephemeral=True
            )
            return
        
        target = resolve_language_name(language) if language else user_preferred_language(
            interaction.user  # type: ignore[arg-type]
        )
        if not target:
            target = "English"
        await interaction.response.defer()
        await self._do_translate(
            interaction,
            sanitize_text(text),
            target,
            defer_ephemeral=False,
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.user_id == self.bot.user.id:
            return

        emoji = str(payload.emoji)
        language = flag_to_language(emoji)
        if not language:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        channel = guild.get_channel(payload.channel_id)
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        # Allow flag reactions on bot embeds (xGalactic translations)
        content = message.content
        if not content and message.embeds:
            content = message.embeds[0].description or ""

        if not content.strip():
            return

        member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        paused, _ = await is_guild_paused(self.db, guild.id)
        if paused:
            return

        rl_msg = check_rate_limits(
            self.guild_limiter, self.user_limiter, guild.id, payload.user_id
        )
        if rl_msg:
            try:
                await member.send(embed=error_embed(rl_msg))  # type: ignore[union-attr]
            except discord.HTTPException:
                pass
            return

        api_key = await get_guild_api_key(self.db, guild.id)
        model = await get_guild_model(self.db, guild.id)
        cfg = await self.db.get_guild_config(guild.id)

        try:
            result = await self.grok.translate(
                content,
                language,
                api_key=api_key,
                model=model,
                style_hint=(cfg or {}).get("translation_style"),
            )
        except Exception:
            logger.exception("Reaction translation failed")
            return

        await self.db.log_usage(
            guild.id,
            payload.user_id,
            result.prompt_tokens,
            result.completion_tokens,
            result.model,
        )

        embed = translation_embed(
            result.text,
            language,
            original_author=str(message.author.display_name),
            model=result.model,
        )
        await message.reply(embed=embed, mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Optional auto language detection on first message (per-guild setting)."""
        if message.author.bot or not message.guild:
            return
        cfg = await self.db.get_guild_config(message.guild.id)
        if not cfg or not cfg.get("auto_detect_language"):
            return
        # Lightweight: only log detection for admins via optional future hook
        # Full onboarding handles role assignment separately.


# class TranslateContextMenu(commands.Cog):
#    """Right-click 'Translate with Grok' context menu."""
#
#    def __init__(self, bot: commands.Bot) -> None:
#        self.bot = bot
#        self.db: Database = bot.db  # type: ignore[attr-defined]
#        self.grok: GrokClient = bot.grok  # type: ignore[attr-defined]
#        self.guild_limiter: RateLimiter = bot.guild_limiter  # type: ignore[attr-defined]
#        self.user_limiter: RateLimiter = bot.user_limiter  # type: ignore[attr-defined]

@app_commands.context_menu(name="Translate with Grok")
async def translate_message(interaction: discord.Interaction, message: discord.Message) -> None:
    """Right-click 'Translate with Grok' context menu."""
    cog = interaction.client.get_cog("TranslationCog")
    if not isinstance(cog, TranslationCog):
        await interaction.response.send_message(
            embed=error_embed("Translation module not loaded."),
            ephemeral=True,
        )
        return

    text = message.content
    if not text and message.embeds:
        text = message.embeds[0].description or ""

    if not text.strip():
        await interaction.response.send_message(
            embed=error_embed("No text to translate on this message."),
            ephemeral=True,
        )
        return

    member = interaction.user
    if isinstance(member, discord.Member):
        target = user_preferred_language(member)
    else:
        target = "English"

    await cog._do_translate(
        interaction,
        text,
        target,
        reply_to=message,
        defer_ephemeral=True,
    )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TranslationCog(bot))
    bot.tree.add_command(translate_message)
    logger.info("Translation context menu added")
    logger.info("Translation command added")
    logger.info("Translation cog loaded")
    logger.info("Translation setup complete")
