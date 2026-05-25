"""Language onboarding: welcome channel, buttons, role assignment."""

from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.db import Database
from utils.embeds import error_embed, success_embed
from utils.flags import ONBOARDING_LANGUAGES, MASTER_LANGUAGES

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
        for label, emoji, role_key in ONBOARDING_LANGUAGES[:8]:
            self.add_item(LanguageButton(label, emoji, role_key))
        self.add_item(LanguageDropdown(bot))

    #async def interaction_check(self, interaction: discord.Interaction) -> bool:
        #return interaction.guild is not None


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
        await self._handle_language_selection(interaction, self.role_key, self.language_label)

    async def _handle_language_selection(self, interaction: discord.Interaction, role_key: str, label: str) -> None:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return
        db: Database = interaction.client.db  # type: ignore[attr-defined]
        role_map = await db.get_language_roles(interaction.guild.id)
        role_id = role_map.get(role_key)
        if not role_id:
            await interaction.response.send_message(
                embed=error_embed(
                    f"No **@{role_key}** role mapped. Ask an admin to run `/setup-top-languages`."
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

        # Remove other language roles
        to_remove = [
            interaction.guild.get_role(rid)
            for key, rid in role_map.items()
            if key != role_key and interaction.guild.get_role(rid)
        ]
        await interaction.user.remove_roles(
            *[r for r in to_remove if r],
            reason="xGalactic language switch",
        )
        await interaction.user.add_roles(role, reason="xGalactic language onboarding")

        await interaction.response.send_message(
            embed=success_embed(f"You're set to **{label}** ({role.mention})."),
            ephemeral=True,
        )

class LanguageDropdown(discord.ui.Select):
    """Dropdown for additional languages."""

    def __init__(self, bot: commands.Bot) -> None:
        options = [
            discord.SelectOption(label=label, emoji=emoji, value=key)
            for label, emoji, key in MASTER_LANGUAGES[8:33]
        ]
        if not options:
            options = [discord.SelectOption(label="No additional languages available", value="none", default=True)]

        super().__init__(
            placeholder="More Languages...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="xgal_lang_dropdown",
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction) -> None:
        role_key = self.values[0]
        if role_key == "none":
            await interaction.response.send_message(
                "No additional languages available at this time.", 
                ephemeral=True
            )
            return
        # Find the label for the selected key
        label = next((label for label, emoji, key in MASTER_LANGUAGES if key == role_key), role_key)
        await self._handle_language_selection(interaction, role_key, label)

    async def _handle_language_selection(self, interaction: discord.Interaction, role_key: str, label: str) -> None:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return
        db: Database = interaction.client.db  # type: ignore[attr-defined]
        role_map = await db.get_language_roles(interaction.guild.id)
        role_id = role_map.get(role_key)
        if not role_id:
            await interaction.response.send_message(
                embed=error_embed(
                    f"No **@{role_key}** role mapped. Ask an admin to run `setup top languages` or `add language` for your specific language."
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

        # Remove other language roles
        to_remove = [
            interaction.guild.get_role(rid)
            for key, rid in role_map.items()
            if key != role_key and interaction.guild.get_role(rid)
        ]
        await interaction.user.remove_roles(
            *[r for r in to_remove if r],
            reason="xGalactic language switch",
        )
        await interaction.user.add_roles(role, reason="xGalactic language onboarding")

        await interaction.response.send_message(
            embed=success_embed(f"You're set to **{label}** ({role.mention})."),
            ephemeral=True,
        )

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

        # Auto-create and map English if it doesn't exist yet
        english_role = discord.utils.get(interaction.guild.roles, name="English")
        if not english_role:
            english_role = await interaction.guild.create_role(
                name="English",
                mentionable=True,
                reason="xGalactic default language role",
            )
            me = interaction.guild.me
            if me and me.top_role > english_role:
                try:
                    await english_role.edit(position=me.top_role.position - 1)
                except discord.HTTPException:
                    pass
        await self.db.set_language_role(interaction.guild.id, "english", english_role.id)
        
        embed = discord.Embed(
            title=WELCOME_EMBED_TITLE,
            description=WELCOME_EMBED_DESC,
            color=0x1DA1F2,
        )
        embed.set_footer(text="xGalactic · Grok-Powered Galactic Standard")

        view_a = LanguageSelectView(self.bot)
        #view_b = LanguageSelectViewB(self.bot)
        await channel.send(embed=embed, view=view_a)
        #await channel.send("More languages:", view=view_b)

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
    @app_commands.command(
        name="list-languages",
        description="Show available languages you can add",
    )
    @app_commands.describe(count="How many languages to show (default 62)")
    @app_commands.default_permissions(manage_roles=True)
    async def list_languages(
        self, interaction: discord.Interaction, count: int = 62
    ) -> None:
        if not interaction.guild:
            return
        max_available = len(MASTER_LANGUAGES)
        count = min(count, max_available)
        lines = [f"{emoji} {label} (`{key}`)" for label, emoji, key in MASTER_LANGUAGES[:count]]
        await interaction.response.send_message(
            embed=success_embed(f"**Available Languages** ({count}/{max_available})\n" + "\n".join(lines)),
            ephemeral=True,
        )
    
    @app_commands.command(
        name="list-installed-languages",
        description="Show currently installed language roles on this server",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def list_installed_languages(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return

        mappings = await self.db.get_language_roles(interaction.guild.id)
        if not mappings:
            await interaction.response.send_message(
                embed=success_embed("No language roles are currently installed."),
                ephemeral=True,
            )
            return

        lines = []
        for key, role_id in sorted(mappings.items()):
            role = interaction.guild.get_role(role_id)
            if role:
                lines.append(f"{role.mention} (`{key}`)")
            else:
                lines.append(f"❌ Unknown / deleted role (ID: {role_id}) (`{key}`)")

        await interaction.response.send_message(
            embed=success_embed("**Installed Language Roles**\n" + "\n".join(lines)),
            ephemeral=True,
        )

    @app_commands.command(
        name="setup-top-languages",
        description="Automatically create and map the top N languages (default 10)",
    )
    @app_commands.describe(count="Number of languages to create (default 10)")
    @app_commands.default_permissions(manage_roles=True)
    async def setup_top_languages(
        self, interaction: discord.Interaction, count: int = 10
    ) -> None:
        if not interaction.guild:
            return

        await interaction.response.defer(ephemeral=True)

        max_available = len(MASTER_LANGUAGES)
        count = max(1, min(count, max_available))

        created = []
        for label, emoji, key in MASTER_LANGUAGES[:count]:
            role = discord.utils.get(interaction.guild.roles, name=label)
            if not role:
                role = await interaction.guild.create_role(
                    name=label,
                    mentionable=True,
                    reason="xGalactic top languages setup",
                )
                # Position bot role above it
                me = interaction.guild.me
                if me and me.top_role > role:
                    try:
                        await role.edit(position=me.top_role.position - 1)
                    except discord.HTTPException:
                        pass

            await self.db.set_language_role(interaction.guild.id, key, role.id)
            created.append(f"{emoji} {label} (`{key}`)")

        await interaction.followup.send(
            embed=success_embed(
                f"✅ Created and mapped **{len(created)}** languages:\n" + "\n".join(created)
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="add-language",
        description="Add a single language by name (fuzzy search)",
    )
    @app_commands.describe(name="Language name or keyword (e.g. chinese, filipino, indonesian)")
    @app_commands.default_permissions(manage_roles=True)
    async def add_language(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        if not interaction.guild:
            return

        search = name.lower().strip()
        found = None
        for label, emoji, key in MASTER_LANGUAGES:
            if search in label.lower() or search in key.lower():
                found = (label, emoji, key)
                break

        if not found:
            await interaction.response.send_message(
                embed=error_embed(
                    f"Could not find language matching '{name}'.\n\n"
                    f"Use `/list-languages` to see all supported languages."
                ),
                ephemeral=True,
            )
            return

        label, emoji, key = found
        role = discord.utils.get(interaction.guild.roles, name=label)
        if not role:
            role = await interaction.guild.create_role(
                name=label,
                mentionable=True,
                reason="xGalactic manual language add",
            )
            me = interaction.guild.me
            if me and me.top_role > role:
                try:
                    await role.edit(position=me.top_role.position - 1)
                except discord.HTTPException:
                    pass

        await self.db.set_language_role(interaction.guild.id, key, role.id)

        await interaction.response.send_message(
            embed=success_embed(f"✅ Added {emoji} **{label}** (`{key}`)"),
            ephemeral=True,
        )
    
    @app_commands.command(
        name="remove-language",
        description="Remove a single language role and mapping",
    )
    @app_commands.describe(name="Language name or keyword")
    @app_commands.default_permissions(manage_roles=True)
    async def remove_language(
        self, interaction: discord.Interaction, name: str
    ) -> None:
        if not interaction.guild:
            return

        search = name.lower().strip()
        found = None
        for label, emoji, key in MASTER_LANGUAGES:
            if search in label.lower() or search in key.lower():
                found = (label, key)
                break

        if not found:
            await interaction.response.send_message(
                embed=error_embed(
                    f"Could not find language '{name}'.\n\n"
                    f"Use `/list-installed-languages` to see currently installed language roles."
                ),
                ephemeral=True,
            )
            return

        label, key = found
        role = discord.utils.get(interaction.guild.roles, name=label)

        if role:
            await role.delete(reason="xGalactic language removal")
            await self.db.set_language_role(interaction.guild.id, key, None)  # remove mapping
            await interaction.response.send_message(
                embed=success_embed(f"✅ Removed role **{label}** and mapping."),
                ephemeral=True,
            )
        else:
            await self.db.set_language_role(interaction.guild.id, key, None)
            await interaction.response.send_message(
                embed=success_embed(f"✅ Removed mapping for **{label}** (role not found)."),
                ephemeral=True,
            )

    @app_commands.command(
        name="cleanup-languages",
        description="Remove ALL xGalactic language roles and mappings (with confirmation)",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def cleanup_languages(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return

        await interaction.response.send_message(
            embed=error_embed("⚠️ This will delete ALL xGalactic language roles.\n\n"
                              "Type `YES` to confirm (this cannot be undone easily)."),
            ephemeral=True,
        )

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.upper() == "YES"

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await interaction.followup.send("Timed out. Cleanup cancelled.", ephemeral=True)
            return

        # Strong cleanup - delete ALL language role mappings for this guild
        async with self.db._db() as db:
            await db.execute(
                "DELETE FROM language_roles WHERE guild_id = ?",
                (interaction.guild.id,)
            )
            await db.commit()
        # Cleanup - delete the roles themselves
        roles_removed = 0
        for label, emoji, key in MASTER_LANGUAGES:
            role = discord.utils.get(interaction.guild.roles, name=label)
            if role:
                try:
                    await role.delete(reason="xGalactic full language cleanup")
                    roles_removed += 1
                except discord.HTTPException:
                    pass
            #await self.db.set_language_role(interaction.guild.id, key, None)

        await interaction.followup.send(
            embed=success_embed(
                f"✅ Cleaned up **{roles_removed}** language roles and all mappings."
            ),
            ephemeral=True,
        )

async def setup(bot: commands.Bot) -> None:
    bot.add_view(LanguageSelectView(bot))
    await bot.add_cog(OnboardingCog(bot))
