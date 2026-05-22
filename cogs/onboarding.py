"""Language onboarding: welcome channel, buttons, role assignment."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import Database
from utils.embeds import error_embed, success_embed
from utils.flags import ONBOARDING_LANGUAGES

logger = logging.getLogger(__name__)

WELCOME_EMBED_TITLE = "🌍 Welcome — Choose Your Language"
WELCOME_EMBED_DESC = (
    "Select your preferred language below. You'll receive a language role "
    "that unlocks your community's language channels.\n\n"
    "**Global channels** stay visible to everyone — react with any flag "
    "emoji on messages for instant Grok translations (X-style)."
)


class LanguageSelectView(discord.ui.View):
    """Persistent language selection buttons."""

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        for label, emoji, role_key in ONBOARDING_LANGUAGES[:5]:
            self.add_item(LanguageButton(label, emoji, role_key))
        # Second row via separate view or overflow — Discord max 5 per row, 5 rows
        # We use 10 languages across 2 views in setup command

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is not None


class LanguageButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, role_key: str) -> None:
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=label,
            emoji=emoji,
            custom_id=f"xgal_lang_{role_key}",
        )
        self.role_key = role_key
        self.language_label = label

    async def callback(self, interaction: discord.Interaction) -> None:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return
        db: Database = interaction.client.db  # type: ignore[attr-defined]
        role_map = await db.get_language_roles(interaction.guild.id)
        role_id = role_map.get(self.role_key)
        if not role_id:
            await interaction.response.send_message(
                embed=error_embed(
                    f"No **@{self.role_key}** role mapped. Ask an admin to run `/setup-welcome`."
                ),
                ephemeral=True,
            )
            return

        role = interaction.guild.get_role(role_id)
        if not role:
            await interaction.response.send_message(
                embed=error_embed("Language role no longer exists."),
                ephemeral=True,
            )
            return

        # Remove other language roles from this guild's map
        to_remove = [
            interaction.guild.get_role(rid)
            for key, rid in role_map.items()
            if key != self.role_key and interaction.guild.get_role(rid)
        ]
        await interaction.user.remove_roles(
            *[r for r in to_remove if r],
            reason="xGalactic language switch",
        )
        await interaction.user.add_roles(role, reason="xGalactic language onboarding")
        await interaction.response.send_message(
            embed=success_embed(f"You're set to **{self.language_label}** ({role.mention})."),
            ephemeral=True,
        )


class LanguageSelectViewB(discord.ui.View):
    """Second row of language buttons."""

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        for label, emoji, role_key in ONBOARDING_LANGUAGES[5:]:
            self.add_item(LanguageButton(label, emoji, role_key))


class OnboardingCog(commands.Cog):
    """Welcome channel setup and language role architecture helpers."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db: Database = bot.db  # type: ignore[attr-defined]

    @app_commands.command(
        name="setup-welcome",
        description="Post the language selection panel in a channel",
    )
    @app_commands.describe(channel="Welcome / onboarding channel")
    @app_commands.default_permissions(manage_guild=True)
    async def setup_welcome(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
    ) -> None:
        if not interaction.guild:
            return

        embed = discord.Embed(
            title=WELCOME_EMBED_TITLE,
            description=WELCOME_EMBED_DESC,
            color=0x1DA1F2,
        )
        embed.set_footer(text="xGalactic · Grok-Powered Galactic Standard")

        view_a = LanguageSelectView(self.bot)
        view_b = LanguageSelectViewB(self.bot)
        await channel.send(embed=embed, view=view_a)
        await channel.send("More languages:", view=view_b)

        await self.db.upsert_guild_config(
            interaction.guild.id,
            welcome_channel_id=channel.id,
        )
        await interaction.response.send_message(
            embed=success_embed(
                f"Welcome panel posted in {channel.mention}. "
                "Map roles with `/map-language-role`."
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="map-language-role",
        description="Map a language key to an existing Discord role",
    )
    @app_commands.describe(
        language_key="Key from onboarding (e.g. english, español)",
        role="Discord role to assign",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def map_language_role(
        self,
        interaction: discord.Interaction,
        language_key: str,
        role: discord.Role,
    ) -> None:
        if not interaction.guild:
            return
        key = language_key.strip().lower()
        await self.db.set_language_role(interaction.guild.id, key, role.id)
        await interaction.response.send_message(
            embed=success_embed(f"Mapped `{key}` → {role.mention}"),
            ephemeral=True,
        )

    @app_commands.command(
        name="setup-channel-visibility",
        description="Hide a channel from @everyone; allow one language role",
    )
    @app_commands.describe(
        channel="Language-specific channel",
        language_role="Role that can view and send messages",
    )
    @app_commands.default_permissions(manage_channels=True)
    async def setup_channel_visibility(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        language_role: discord.Role,
    ) -> None:
        """Admin-friendly helper: language channels hidden from @everyone."""
        if not interaction.guild:
            return
        everyone = interaction.guild.default_role
        await channel.set_permissions(
            everyone,
            view_channel=False,
            send_messages=False,
            reason="xGalactic language channel isolation",
        )
        await channel.set_permissions(
            language_role,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            reason="xGalactic language role access",
        )
        await interaction.response.send_message(
            embed=success_embed(
                f"{channel.mention} is now visible only to {language_role.mention} "
                "(plus roles above it in hierarchy)."
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="create-language-role",
        description="Create a language role and map it (admin helper)",
    )
    @app_commands.describe(
        name="Role name (e.g. Español)",
        language_key="Internal key (e.g. español)",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def create_language_role(
        self,
        interaction: discord.Interaction,
        name: str,
        language_key: str,
    ) -> None:
        if not interaction.guild:
            return
        role = await interaction.guild.create_role(
            name=name,
            mentionable=True,
            reason="xGalactic language role",
        )
        me = interaction.guild.me
        if me and me.top_role > role:
            try:
                await role.edit(position=me.top_role.position - 1)
            except discord.HTTPException:
                pass
        key = language_key.strip().lower()
        await self.db.set_language_role(interaction.guild.id, key, role.id)
        await interaction.response.send_message(
            embed=success_embed(
                f"Created {role.mention}. Place bot role **above** language roles. "
                f"Mapped key `{key}`."
            ),
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    bot.add_view(LanguageSelectView(bot))
    bot.add_view(LanguageSelectViewB(bot))
    await bot.add_cog(OnboardingCog(bot))
