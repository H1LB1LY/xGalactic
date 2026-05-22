"""Async SQLite persistence for guild config, usage, and mirroring."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

import aiosqlite

DEFAULT_DB = "data/xgalactic.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id INTEGER PRIMARY KEY,
    xai_api_key TEXT,
    grok_model TEXT DEFAULT 'grok-4.1-fast',
    monthly_budget_usd REAL,
    translation_style TEXT,
    welcome_channel_id INTEGER,
    log_channel_id INTEGER,
    auto_detect_language INTEGER DEFAULT 0,
    paused INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    user_id INTEGER,
    tokens_prompt INTEGER DEFAULT 0,
    tokens_completion INTEGER DEFAULT 0,
    model TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mirror_pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    source_channel_id INTEGER NOT NULL,
    target_channel_id INTEGER NOT NULL,
    target_language TEXT NOT NULL,
    webhook_id INTEGER,
    webhook_token TEXT,
    UNIQUE(guild_id, source_channel_id, target_channel_id)
);

CREATE TABLE IF NOT EXISTS mirror_message_map (
    source_message_id INTEGER PRIMARY KEY,
    target_message_id INTEGER NOT NULL,
    mirror_pair_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS language_roles (
    guild_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    language_key TEXT NOT NULL,
    PRIMARY KEY (guild_id, language_key)
);
"""


class Database:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.getenv("DATABASE_PATH", DEFAULT_DB)
        self._schema_ready = False

    @asynccontextmanager
    async def _db(self) -> AsyncIterator[aiosqlite.Connection]:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        db = await aiosqlite.connect(self.path)
        db.row_factory = aiosqlite.Row
        try:
            if not self._schema_ready:
                await db.executescript(_SCHEMA)
                await db.commit()
                self._schema_ready = True
            yield db
        finally:
            await db.close()

    async def connect(self) -> None:
        """Initialize schema on bot startup."""
        async with self._db():
            pass

    async def get_guild_config(self, guild_id: int) -> dict[str, Any] | None:
        async with self._db() as db:
            async with db.execute(
                "SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    async def upsert_guild_config(self, guild_id: int, **fields: Any) -> None:
        existing = await self.get_guild_config(guild_id)
        async with self._db() as db:
            if existing is None:
                cols = ["guild_id"] + list(fields.keys())
                placeholders = ", ".join("?" * len(cols))
                await db.execute(
                    f"INSERT INTO guild_config ({', '.join(cols)}) VALUES ({placeholders})",
                    (guild_id, *fields.values()),
                )
            else:
                sets = ", ".join(f"{k} = ?" for k in fields)
                await db.execute(
                    f"UPDATE guild_config SET {sets}, updated_at = datetime('now') WHERE guild_id = ?",
                    (*fields.values(), guild_id),
                )
            await db.commit()

    async def log_usage(
        self,
        guild_id: int,
        user_id: int | None,
        tokens_prompt: int,
        tokens_completion: int,
        model: str,
    ) -> None:
        async with self._db() as db:
            await db.execute(
                """INSERT INTO usage_log
                   (guild_id, user_id, tokens_prompt, tokens_completion, model)
                   VALUES (?, ?, ?, ?, ?)""",
                (guild_id, user_id, tokens_prompt, tokens_completion, model),
            )
            await db.commit()

    async def get_usage_stats(self, guild_id: int, days: int = 30) -> dict[str, Any]:
        async with self._db() as db:
            async with db.execute(
                """SELECT COUNT(*) as requests,
                          COALESCE(SUM(tokens_prompt), 0) as prompt_tokens,
                          COALESCE(SUM(tokens_completion), 0) as completion_tokens
                   FROM usage_log
                   WHERE guild_id = ? AND created_at >= datetime('now', ?)""",
                (guild_id, f"-{days} days"),
            ) as cur:
                row = await cur.fetchone()
                return dict(row) if row else {
                    "requests": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                }

    async def get_monthly_spend_estimate(self, guild_id: int) -> float:
        """Rough USD estimate: $0.20/1M input + $0.50/1M output tokens."""
        stats = await self.get_usage_stats(guild_id, days=30)
        prompt = stats.get("prompt_tokens", 0) or 0
        completion = stats.get("completion_tokens", 0) or 0
        return (prompt * 0.20 + completion * 0.50) / 1_000_000

    async def is_budget_exceeded(self, guild_id: int) -> bool:
        cfg = await self.get_guild_config(guild_id)
        if not cfg or not cfg.get("monthly_budget_usd"):
            return False
        spend = await self.get_monthly_spend_estimate(guild_id)
        return spend >= float(cfg["monthly_budget_usd"])

    async def add_mirror_pair(
        self,
        guild_id: int,
        source_id: int,
        target_id: int,
        language: str,
        webhook_id: int | None = None,
        webhook_token: str | None = None,
    ) -> int:
        async with self._db() as db:
            await db.execute(
                """INSERT OR REPLACE INTO mirror_pairs
                   (guild_id, source_channel_id, target_channel_id, target_language, webhook_id, webhook_token)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (guild_id, source_id, target_id, language, webhook_id, webhook_token),
            )
            await db.commit()
            async with db.execute("SELECT last_insert_rowid()") as cur:
                row = await cur.fetchone()
                return row[0] if row else 0

    async def get_mirror_pairs_for_source(self, guild_id: int, source_id: int) -> list[dict]:
        async with self._db() as db:
            async with db.execute(
                "SELECT * FROM mirror_pairs WHERE guild_id = ? AND source_channel_id = ?",
                (guild_id, source_id),
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]

    async def get_mirror_pairs_for_target(self, guild_id: int, target_id: int) -> list[dict]:
        async with self._db() as db:
            async with db.execute(
                "SELECT * FROM mirror_pairs WHERE guild_id = ? AND target_channel_id = ?",
                (guild_id, target_id),
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]

    async def remove_mirror_pair(self, guild_id: int, source_id: int, target_id: int) -> bool:
        async with self._db() as db:
            cur = await db.execute(
                """DELETE FROM mirror_pairs
                   WHERE guild_id = ? AND source_channel_id = ? AND target_channel_id = ?""",
                (guild_id, source_id, target_id),
            )
            await db.commit()
            return cur.rowcount > 0

    async def list_mirror_pairs(self, guild_id: int) -> list[dict]:
        async with self._db() as db:
            async with db.execute(
                "SELECT * FROM mirror_pairs WHERE guild_id = ?", (guild_id,)
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]

    async def map_mirror_message(
        self, source_msg_id: int, target_msg_id: int, pair_id: int
    ) -> None:
        async with self._db() as db:
            await db.execute(
                """INSERT OR REPLACE INTO mirror_message_map
                   (source_message_id, target_message_id, mirror_pair_id)
                   VALUES (?, ?, ?)""",
                (source_msg_id, target_msg_id, pair_id),
            )
            await db.commit()

    async def get_mapped_target(self, source_msg_id: int) -> int | None:
        async with self._db() as db:
            async with db.execute(
                "SELECT target_message_id FROM mirror_message_map WHERE source_message_id = ?",
                (source_msg_id,),
            ) as cur:
                row = await cur.fetchone()
                return row[0] if row else None

    async def get_mapped_source(self, target_msg_id: int) -> tuple[int, int] | None:
        async with self._db() as db:
            async with db.execute(
                """SELECT source_message_id, mirror_pair_id
                   FROM mirror_message_map WHERE target_message_id = ?""",
                (target_msg_id,),
            ) as cur:
                row = await cur.fetchone()
                return (row[0], row[1]) if row else None

    async def set_language_role(self, guild_id: int, language_key: str, role_id: int) -> None:
        async with self._db() as db:
            await db.execute(
                """INSERT OR REPLACE INTO language_roles (guild_id, language_key, role_id)
                   VALUES (?, ?, ?)""",
                (guild_id, language_key, role_id),
            )
            await db.commit()

    async def get_language_roles(self, guild_id: int) -> dict[str, int]:
        async with self._db() as db:
            async with db.execute(
                "SELECT language_key, role_id FROM language_roles WHERE guild_id = ?",
                (guild_id,),
            ) as cur:
                rows = await cur.fetchall()
                return {r["language_key"]: r["role_id"] for r in rows}
