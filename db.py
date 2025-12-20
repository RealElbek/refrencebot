import aiosqlite

DB = "users.db"
#5516186645
#848376801
ADMIN_IDS = [848376801,5516186645,699724818]  # your Telegram ID(s)


async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            referrer_id INTEGER,
            joined_channel INTEGER DEFAULT 0,
            is_participant INTEGER DEFAULT 0,
            username TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS battle (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            is_active INTEGER DEFAULT 0
        )
        """)
        await db.execute(
            "INSERT OR IGNORE INTO battle (id, is_active) VALUES (1, 0)"
        )
        await db.commit()


async def add_user(user_id, referrer_id=None, username=None):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users(user_id, referrer_id, username)
        VALUES (?, ?, ?)
        """, (user_id, referrer_id, username))
        await db.commit()


async def set_participant(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET is_participant = 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


async def set_joined(user_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT joined_channel FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = await cur.fetchone()
        if not row or row[0] == 1:
            return
        await db.execute(
            "UPDATE users SET joined_channel = 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


async def get_referral_count(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM users WHERE referrer_id = ? AND joined_channel = 1",
            (user_id,)
        )
        res = await cur.fetchone()
        return res[0] if res else 0

async def reset_battle_data():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            UPDATE users
            SET
                referrer_id = NULL,
                joined_channel = 0,
                is_participant = 0
            WHERE user_id NOT IN ({})
        """.format(",".join(map(str, ADMIN_IDS))))
        await db.commit()



async def get_top_referrers(limit=10):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT u.referrer_id,
               COUNT(*) as cnt,
               r.username
        FROM users u
        LEFT JOIN users r ON r.user_id = u.referrer_id
        WHERE u.referrer_id IS NOT NULL
          AND u.joined_channel = 1
        GROUP BY u.referrer_id
        ORDER BY cnt DESC
        LIMIT ?
        """, (limit,))
        return await cur.fetchall()



async def set_battle(active: bool):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE battle SET is_active = ? WHERE id = 1",
            (1 if active else 0,)
        )
        await db.commit()


async def is_battle_active():
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("SELECT is_active FROM battle WHERE id = 1")
        row = await cur.fetchone()
        return bool(row[0])


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
