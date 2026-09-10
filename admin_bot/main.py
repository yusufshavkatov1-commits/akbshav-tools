from __future__ import annotations

import hashlib
import hmac
import html
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from common.config import ADMIN_IDS, ADMIN_OWNER_ID, ADMIN_PASSWORD, ADMIN_PASSWORD_HASH, ADMIN_SESSION_HOURS, ADMIN_BOT_TOKEN, BROADCAST_BATCH_SIZE
from db.database import clear_state, close_db, execute, fetch, fetchrow, fetchval, get_state, init_db, insert_security_event, set_state

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("akbshav.admin")

LOGIN_STATE = "admin_login"
BROADCAST_STATE = "broadcast"
SEARCH_STATE = "search"
SCHEDULE_STATE = "broadcast_schedule"

PERMISSIONS = {
    "owner": {"users", "stats", "tickets", "broadcast", "functions", "channel", "events", "admins", "system"},
    "admin": {"users", "stats", "tickets", "broadcast", "functions", "channel", "events"},
    "moderator": {"users", "stats", "tickets", "events"},
}


def esc(value: object) -> str:
    return html.escape(str(value))


def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Пользователи", callback_data="users:0"), InlineKeyboardButton("📊 Аналитика", callback_data="stats")],
        [InlineKeyboardButton("🎫 Тикеты", callback_data="tickets:0"), InlineKeyboardButton("📨 Рассылки", callback_data="broadcast")],
        [InlineKeyboardButton("⚡ Функции", callback_data="functions:0"), InlineKeyboardButton("📢 Канал", callback_data="channel")],
        [InlineKeyboardButton("📋 Аудит", callback_data="events:0"), InlineKeyboardButton("👮 Админы", callback_data="admins")],
        [InlineKeyboardButton("🚨 Система", callback_data="system"), InlineKeyboardButton("🔒 Выйти", callback_data="logout")],
    ])


def back_kb(target: str = "home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data=target)]])


def user_list_kb(rows, offset: int) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(f"{r['telegram_id']} | @{r['username'] or '-'}", callback_data=f"user:{r['telegram_id']}")] for r in rows]
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"users:{max(0, offset-10)}"))
    if len(rows) == 10:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"users:{offset+10}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("🔎 Поиск", callback_data="search")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="home")])
    return InlineKeyboardMarkup(buttons)


async def admin_role(uid: int) -> str | None:
    if uid not in ADMIN_IDS:
        return None
    row = await fetchrow("SELECT role,enabled FROM app_admins WHERE telegram_id=$1", uid)
    if not row or not row["enabled"]:
        return None
    return str(row["role"])


async def has_permission(uid: int, permission: str) -> bool:
    role = await admin_role(uid)
    if role is None:
        return False
    if permission in PERMISSIONS.get(role, set()):
        return True
    row = await fetchrow("SELECT 1 FROM app_admin_permissions WHERE telegram_id=$1 AND permission=$2", uid, permission)
    return bool(row)


async def session_ok(uid: int) -> bool:
    if await admin_role(uid) is None:
        return False
    row = await fetchrow("SELECT expires_at FROM app_admin_sessions WHERE telegram_id=$1", uid)
    return bool(row and row["expires_at"] > datetime.now(timezone.utc))


async def audit(uid: int, action: str, target_id: int | None = None, details: dict | None = None) -> None:
    await execute("INSERT INTO app_admin_actions(admin_id,action,target_id,details) VALUES($1,$2,$3,$4::jsonb)", uid, action, target_id, json.dumps(details or {}, ensure_ascii=False))


def password_matches(value: str) -> bool:
    if ADMIN_PASSWORD_HASH:
        try:
            algo, iterations, salt, digest = ADMIN_PASSWORD_HASH.split("$", 3)
            if algo != "pbkdf2_sha256":
                return False
            actual = hashlib.pbkdf2_hmac("sha256", value.encode(), salt.encode(), int(iterations)).hex()
            return hmac.compare_digest(actual, digest)
        except (ValueError, TypeError):
            return False
    return bool(ADMIN_PASSWORD) and hmac.compare_digest(value, ADMIN_PASSWORD)


async def login_blocked(uid: int) -> bool:
    count = await fetchval("SELECT COUNT(*) FROM app_admin_logins WHERE telegram_id=$1 AND success=FALSE AND created_at > NOW()-INTERVAL '15 minutes'", uid)
    return int(count or 0) >= 8


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.effective_message:
        return
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.effective_message.reply_text("⛔ Доступ запрещён.")
        return
    if await session_ok(uid):
        await update.effective_message.reply_text("🛡 AKBSHAV TOOLS ADMIN", reply_markup=main_kb())
        return
    if await login_blocked(uid):
        await update.effective_message.reply_text("🛑 Слишком много неудачных попыток. Попробуйте позже.")
        return
    await execute("INSERT INTO app_admins(telegram_id,role) VALUES($1,$2) ON CONFLICT DO NOTHING", uid, "owner" if uid == ADMIN_OWNER_ID else "admin")
    await set_state("app_admin_states","admin_id",uid,LOGIN_STATE,{},15)
    await update.effective_message.reply_text("🔐 Введите пароль администратора:")


async def auth_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not update.effective_user or not update.effective_message.text:
        return
    uid = update.effective_user.id
    text = update.effective_message.text.strip()
    state = await get_state("app_admin_states","admin_id",uid)
    if state and state[0] == LOGIN_STATE:
        await clear_state("app_admin_states","admin_id",uid)
        if await login_blocked(uid) or uid not in ADMIN_IDS or not password_matches(text):
            await execute("INSERT INTO app_admin_logins(telegram_id,success) VALUES($1,FALSE)", uid)
            await insert_security_event(uid, "admin_login_failed", "warning")
            await update.message.reply_text("❌ Неверный пароль.")
            return
        await execute("INSERT INTO app_admin_logins(telegram_id,success) VALUES($1,TRUE)", uid)
        token = secrets.token_urlsafe(48)
        digest = hashlib.sha256(token.encode()).hexdigest()
        expires = datetime.now(timezone.utc) + timedelta(hours=ADMIN_SESSION_HOURS)
        await execute("INSERT INTO app_admins(telegram_id,role,enabled) VALUES($1,$2,TRUE) ON CONFLICT(telegram_id) DO UPDATE SET enabled=TRUE", uid, "owner" if uid == ADMIN_OWNER_ID else "admin")
        await execute("INSERT INTO app_admin_sessions(telegram_id,session_hash,expires_at) VALUES($1,$2,$3) ON CONFLICT(telegram_id) DO UPDATE SET session_hash=$2,expires_at=$3", uid, digest, expires)
        await audit(uid, "login")
        await update.message.reply_text("✅ Авторизация успешна.", reply_markup=main_kb())
        return

    if not await session_ok(uid):
        return
    state = await get_state("app_admin_states","admin_id",uid)
    if state and state[0] == BROADCAST_STATE:
        await clear_state("app_admin_states","admin_id",uid)
        await create_broadcast(uid, text, scheduled_at=None, update=update)
        return
    if state and state[0] == SCHEDULE_STATE:
        await clear_state("app_admin_states","admin_id",uid)
        try:
            stamp, body = text.split("|", 1)
            when = datetime.fromisoformat(stamp.strip().replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            await create_broadcast(uid, body.strip(), scheduled_at=when, update=update)
        except (ValueError, TypeError):
            await update.message.reply_text("Формат: 2026-09-10 18:30+00:00 | текст", reply_markup=main_kb())
        return
    if state and state[0] == SEARCH_STATE:
        await clear_state("app_admin_states","admin_id",uid)
        if not await has_permission(uid, "users"):
            return
        rows = await fetch("SELECT telegram_id,username,first_name,last_name FROM app_users WHERE CAST(telegram_id AS TEXT) ILIKE $1 OR COALESCE(username,'') ILIKE $1 OR COALESCE(first_name,'') ILIKE $1 OR COALESCE(last_name,'') ILIKE $1 ORDER BY last_seen_at DESC LIMIT 20", f"%{text}%")
        buttons = [[InlineKeyboardButton(f"{r['telegram_id']} | @{r['username'] or '-'}", callback_data=f"user:{r['telegram_id']}")] for r in rows]
        await update.message.reply_text("🔎 Результаты:" if rows else "Ничего не найдено.", reply_markup=InlineKeyboardMarkup(buttons or [[InlineKeyboardButton("⬅️ Назад", callback_data="home")]]))


async def create_broadcast(admin_id: int, text: str, scheduled_at: datetime | None, update: Update) -> None:
    if not await has_permission(admin_id, "broadcast"):
        await update.message.reply_text("⛔ Недостаточно прав.")
        return
    text = text.strip()[:4000]
    if not text:
        await update.message.reply_text("Пустая рассылка запрещена.")
        return
    status = "scheduled" if scheduled_at else "queued"
    row = await fetchrow("INSERT INTO app_broadcasts(admin_id,text,status,scheduled_at) VALUES($1,$2,$3,$4) RETURNING id", admin_id, text, status, scheduled_at)
    run_at = scheduled_at or datetime.now(timezone.utc)
    await execute("INSERT INTO app_jobs(job_type,user_id,run_at,payload) VALUES('broadcast',NULL,$1,$2::jsonb)", run_at, json.dumps({"broadcast_id": int(row["id"])}, ensure_ascii=False))
    await audit(admin_id, "broadcast_create", details={"broadcast_id": int(row["id"]), "scheduled_at": scheduled_at.isoformat() if scheduled_at else None})
    await update.message.reply_text(f"📨 Рассылка #{row['id']} {'запланирована' if scheduled_at else 'поставлена в очередь'}.", reply_markup=main_kb())


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    uid = q.from_user.id
    await q.answer()
    if not await session_ok(uid):
        await q.edit_message_text("⛔ Сессия истекла. Используйте /start.")
        return
    data = q.data or ""
    if len(data) > 64:
        await q.answer("Некорректный callback.", show_alert=True); return
    if data.startswith(("users:", "user:", "toggleblock:", "utickets:", "tickets:", "ticket:", "closeticket:", "togglefn:", "broadcast_cancel:", "events:")):
        try:
            int(data.split(":", 1)[1])
        except (ValueError, IndexError):
            await q.answer("Некорректный запрос.", show_alert=True); return
    if data == "home":
        await q.edit_message_text("🛡 AKBSHAV TOOLS ADMIN", reply_markup=main_kb()); return
    if data == "logout":
        await execute("DELETE FROM app_admin_sessions WHERE telegram_id=$1", uid); await audit(uid, "logout")
        await q.edit_message_text("🔒 Вы вышли из админ-панели."); return
    if data == "search":
        if not await has_permission(uid, "users"): return
        await set_state("app_admin_states","admin_id",uid,SEARCH_STATE,{},15); await q.edit_message_text("🔎 Введите ID, username или имя:", reply_markup=back_kb()); return
    if data == "broadcast":
        if not await has_permission(uid, "broadcast"): await q.answer("Недостаточно прав", show_alert=True); return
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("✉️ Новая",callback_data="broadcast:new")],[InlineKeyboardButton("🕐 Запланировать",callback_data="broadcast:schedule")],[InlineKeyboardButton("📅 Запланированные",callback_data="broadcast:scheduled")],[InlineKeyboardButton("📊 История",callback_data="broadcast:history")],[InlineKeyboardButton("❌ Отмена",callback_data="broadcast:cancel")],[InlineKeyboardButton("⬅️ Назад",callback_data="home")]])
        await q.edit_message_text("📨 <b>Рассылки</b>", parse_mode=ParseMode.HTML, reply_markup=kb); return
    if data == "broadcast:new":
        await set_state("app_admin_states","admin_id",uid,BROADCAST_STATE,{},15); await q.edit_message_text("✉️ Отправьте текст. Перед запуском запись попадёт в очередь.\n/cancel — отмена", reply_markup=back_kb()); return
    if data == "broadcast:schedule":
        await set_state("app_admin_states","admin_id",uid,SCHEDULE_STATE,{},15)
        await q.edit_message_text("🕐 Отправьте: YYYY-MM-DD HH:MM+00:00 | текст\n/cancel — отмена", reply_markup=back_kb("broadcast")); return
    if data == "broadcast:scheduled":
        rows=await fetch("SELECT id,scheduled_at,status FROM app_broadcasts WHERE status='scheduled' ORDER BY scheduled_at LIMIT 20")
        body="🕐 <b>Запланированные</b>\n\n"+("\n".join(f"#{r['id']} — {r['scheduled_at']}" for r in rows) or "Нет")
        await q.edit_message_text(body,parse_mode=ParseMode.HTML,reply_markup=back_kb("broadcast")); return
    if data == "broadcast:history":
        rows=await fetch("SELECT id,status,targeted,sent,failed,created_at,finished_at FROM app_broadcasts ORDER BY id DESC LIMIT 20")
        body="📊 <b>История</b>\n\n"+("\n".join(f"#{r['id']} {r['status']} | target {r['targeted']} | sent {r['sent']} | failed {r['failed']}" for r in rows) or "Нет")
        await q.edit_message_text(body,parse_mode=ParseMode.HTML,reply_markup=back_kb("broadcast")); return
    if data == "broadcast:cancel":
        rows=await fetch("SELECT id,scheduled_at FROM app_broadcasts WHERE status='scheduled' ORDER BY scheduled_at LIMIT 20")
        buttons=[[InlineKeyboardButton(f"❌ #{r['id']} — {r['scheduled_at']}",callback_data=f"broadcast_cancel:{r['id']}")] for r in rows]
        buttons.append([InlineKeyboardButton("⬅️ Назад",callback_data="broadcast")])
        await q.edit_message_text("Выберите рассылку для отмены:",reply_markup=InlineKeyboardMarkup(buttons)); return
    if data.startswith("broadcast_cancel:"):
        bid=int(data.split(":",1)[1]); await execute("UPDATE app_broadcasts SET status='cancelled',cancelled_at=NOW() WHERE id=$1 AND status='scheduled'",bid); await execute("UPDATE app_jobs SET status='cancelled',finished_at=NOW() WHERE job_type='broadcast' AND status='pending' AND payload->>'broadcast_id'=$1",str(bid)); await audit(uid,"broadcast_cancel",details={"broadcast_id":bid}); await q.edit_message_text("❌ Рассылка отменена.",reply_markup=back_kb("broadcast")); return
    if data == "stats":
        if not await has_permission(uid,"stats"): return
        vals=await fetchrow("""SELECT (SELECT COUNT(*) FROM app_users) total, (SELECT COUNT(*) FROM app_users WHERE last_seen_at>NOW()-INTERVAL '1 day') dau, (SELECT COUNT(*) FROM app_users WHERE last_seen_at>NOW()-INTERVAL '7 days') wau, (SELECT COUNT(*) FROM app_users WHERE last_seen_at>NOW()-INTERVAL '30 days') mau, (SELECT COUNT(*) FROM app_users WHERE blocked) blocked, (SELECT COUNT(*) FROM app_business_connections WHERE is_enabled) connected""")
        langs=await fetch("SELECT language,COUNT(*) n FROM app_users GROUP BY language ORDER BY n DESC")
        errors=await fetchval("SELECT COUNT(*) FROM app_function_errors WHERE created_at>NOW()-INTERVAL '24 hours'")
        retention=await fetchrow("""SELECT COALESCE(ROUND(100.0*COUNT(*) FILTER (WHERE EXISTS(SELECT 1 FROM app_users u2 WHERE u2.telegram_id=u.telegram_id AND u2.last_seen_at>=u.created_at+INTERVAL '1 day'))/NULLIF(COUNT(*),0),2),0) d1 FROM app_users u WHERE created_at<NOW()-INTERVAL '1 day'""")
        lang_text=", ".join(f"{r['language']}={r['n']}" for r in langs) or "нет данных"
        body=f"📊 <b>Analytics</b>\n\nDAU: {vals['dau']}\nWAU: {vals['wau']}\nMAU: {vals['mau']}\nUsers: {vals['total']}\nBlocked: {vals['blocked']}\nBusiness: {vals['connected']}\nErrors 24h: {errors}\nD1 retention: {retention['d1']}%\nLanguages: {esc(lang_text)}"
        await q.edit_message_text(body,parse_mode=ParseMode.HTML,reply_markup=back_kb()); return
    if data.startswith("users:"):
        if not await has_permission(uid,"users"): return
        offset=int(data.split(":")[1]); rows=await fetch("SELECT telegram_id,username FROM app_users ORDER BY created_at DESC LIMIT 10 OFFSET $1",offset); total=await fetchval("SELECT COUNT(*) FROM app_users")
        await q.edit_message_text(f"👥 Пользователи: {total}\nСтраница: {offset//10+1}",reply_markup=user_list_kb(rows,offset)); return
    if data.startswith("user:"):
        if not await has_permission(uid,"users"): return
        target=int(data.split(":",1)[1]); row=await fetchrow("SELECT * FROM app_users WHERE telegram_id=$1",target)
        if not row: await q.edit_message_text("Пользователь не найден.",reply_markup=back_kb()); return
        conn=await fetchrow("SELECT is_enabled FROM app_business_connections WHERE user_id=$1",target)
        body=(f"<b>Пользователь</b>\nID: <code>{row['telegram_id']}</code>\nUsername: @{esc(row['username'] or '-')}\nИмя: {esc((row['first_name'] or '')+' '+(row['last_name'] or ''))}\nЯзык: {row['language']}\nПравила: {'да' if row['rules_accepted'] else 'нет'}\nПодписка: {'да' if row['subscription_ok'] else 'нет'}\nЗаблокирован: {'да' if row['blocked'] else 'нет'}\nПоследняя активность: {row['last_seen_at']}\nАвтоматизация: {'да' if conn and conn['is_enabled'] else 'нет'}")
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("🚫 Заблокировать" if not row['blocked'] else "✅ Разблокировать",callback_data=f"toggleblock:{target}")],[InlineKeyboardButton("🎫 Тикеты",callback_data=f"utickets:{target}")],[InlineKeyboardButton("⬅️ Пользователи",callback_data="users:0")]])
        await q.edit_message_text(body,parse_mode=ParseMode.HTML,reply_markup=kb); return
    if data.startswith("toggleblock:"):
        if not await has_permission(uid,"users"): return
        target=int(data.split(":",1)[1]); await execute("UPDATE app_users SET blocked=NOT blocked WHERE telegram_id=$1",target); await audit(uid,"user_block_toggle",target); await q.edit_message_text("✅ Статус изменён.",reply_markup=back_kb()); return
    if data.startswith("utickets:"):
        if not await has_permission(uid,"tickets"): return
        target=int(data.split(":",1)[1]); rows=await fetch("SELECT id,status,updated_at FROM app_tickets WHERE user_id=$1 ORDER BY updated_at DESC LIMIT 20",target); body="🎫 Тикеты:\n\n"+("\n".join(f"#{r['id']} — {r['status']} — {r['updated_at']}" for r in rows) or "нет")
        await q.edit_message_text(body,reply_markup=back_kb()); return
    if data.startswith("tickets:"):
        if not await has_permission(uid,"tickets"): return
        offset=int(data.split(":")[1]); rows=await fetch("SELECT t.id,t.status,t.user_id,t.updated_at,u.username FROM app_tickets t JOIN app_users u ON u.telegram_id=t.user_id ORDER BY t.updated_at DESC LIMIT 10 OFFSET $1",offset); buttons=[[InlineKeyboardButton(f"#{r['id']} | {r['status']} | {r['username'] or r['user_id']}",callback_data=f"ticket:{r['id']}")] for r in rows]; buttons.append([InlineKeyboardButton("⬅️ Назад",callback_data="home")]); await q.edit_message_text("🎫 Тикеты",reply_markup=InlineKeyboardMarkup(buttons)); return
    if data.startswith("ticket:"):
        if not await has_permission(uid,"tickets"): return
        tid=int(data.split(":",1)[1]); row=await fetchrow("SELECT t.*,u.username FROM app_tickets t JOIN app_users u ON u.telegram_id=t.user_id WHERE t.id=$1",tid); msgs=await fetch("SELECT sender_type,text,created_at FROM app_ticket_messages WHERE ticket_id=$1 ORDER BY id LIMIT 30",tid)
        if not row: await q.edit_message_text("Тикет не найден.",reply_markup=back_kb()); return
        body=f"🎫 <b>#{tid}</b> | {row['status']} | @{esc(row['username'] or '-')}\n\n"+"\n".join(f"<b>{m['sender_type']}</b>: {esc(m['text'][:500])}" for m in msgs)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Закрыть",callback_data=f"closeticket:{tid}")],[InlineKeyboardButton("⬅️ Тикеты",callback_data="tickets:0")]])
        await q.edit_message_text(body[:3900],parse_mode=ParseMode.HTML,reply_markup=kb); return
    if data.startswith("closeticket:"):
        if not await has_permission(uid,"tickets"): return
        tid=int(data.split(":",1)[1]); await execute("UPDATE app_tickets SET status='closed',updated_at=NOW() WHERE id=$1 AND status<>'closed'",tid); await audit(uid,"ticket_close",details={"ticket_id":tid}); await q.edit_message_text("🔒 Тикет закрыт.",reply_markup=back_kb()); return
    if data.startswith("functions:"):
        if not await has_permission(uid,"functions"): return
        rows=await fetch("SELECT key,enabled,usage_count FROM app_functions ORDER BY key"); buttons=[[InlineKeyboardButton(f"{'🟢' if r['enabled'] else '🔴'} {r['key']} ({r['usage_count']})",callback_data=f"togglefn:{r['key']}")] for r in rows]; buttons.append([InlineKeyboardButton("⬅️ Назад",callback_data="home")]); await q.edit_message_text("⚡ Функции. Состояние проверяется backend-ом.",reply_markup=InlineKeyboardMarkup(buttons)); return
    if data.startswith("togglefn:"):
        if not await has_permission(uid,"functions"): return
        key=data.split(":",1)[1]; row=await fetchrow("SELECT enabled FROM app_functions WHERE key=$1",key)
        if not row: await execute("INSERT INTO app_functions(key,enabled) VALUES($1,FALSE)",key); new=False
        else: new=not row["enabled"]; await execute("UPDATE app_functions SET enabled=$1 WHERE key=$2",new,key)
        await audit(uid,"function_toggle",details={"key":key,"enabled":new}); await q.edit_message_text(f"⚡ {key}: {'ON' if new else 'OFF'}",reply_markup=back_kb()); return
    if data == "channel":
        if not await has_permission(uid,"channel"): return
        await q.edit_message_text("📢 Обязательный канал: @akbshav_channel\nПроверка подписки выполняется через Bot API.",reply_markup=back_kb()); return
    if data.startswith("events:"):
        if not await has_permission(uid,"events"): return
        rows=await fetch("SELECT admin_id,action,target_id,details,created_at FROM app_admin_actions ORDER BY id DESC LIMIT 30"); body="📋 <b>Audit Log</b>\n\n"+"\n".join(f"{r['created_at']} · {r['admin_id']} · {r['action']} · {r['target_id'] or '-'}" for r in rows) or "нет данных"; await q.edit_message_text(body[:3900],parse_mode=ParseMode.HTML,reply_markup=back_kb()); return
    if data == "admins":
        if not await has_permission(uid,"admins"): return
        rows=await fetch("SELECT telegram_id,role,enabled FROM app_admins ORDER BY created_at"); body="👮 <b>Администраторы</b>\n\n"+"\n".join(f"{r['telegram_id']} — {r['role']} — {'ON' if r['enabled'] else 'OFF'}" for r in rows) or "нет"; await q.edit_message_text(body,parse_mode=ParseMode.HTML,reply_markup=back_kb()); return
    if data == "system":
        if not await has_permission(uid,"system"): return
        pending=await fetchval("SELECT COUNT(*) FROM app_jobs WHERE status='pending'"); failed=await fetchval("SELECT COUNT(*) FROM app_jobs WHERE status='failed'"); db_users=await fetchval("SELECT COUNT(*) FROM app_users"); await q.edit_message_text(f"🚨 <b>System</b>\n\nUsers: {db_users}\nPending jobs: {pending}\nFailed jobs: {failed}",parse_mode=ParseMode.HTML,reply_markup=back_kb()); return


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid=update.effective_user.id
    if not await session_ok(uid) or not await has_permission(uid,"tickets"): return
    args=update.effective_message.text.split(maxsplit=2)
    if len(args)<3: await update.message.reply_text("Использование: /reply TICKET_ID текст"); return
    try: tid=int(args[1])
    except ValueError: await update.message.reply_text("Неверный ID тикета."); return
    text=args[2][:3500]; ticket=await fetchrow("SELECT user_id,status FROM app_tickets WHERE id=$1",tid)
    if not ticket: await update.message.reply_text("Тикет не найден."); return
    if ticket["status"]=="closed": await update.message.reply_text("Тикет закрыт."); return
    await execute("INSERT INTO app_ticket_messages(ticket_id,sender_type,sender_id,text) VALUES($1,'admin',$2,$3)",tid,uid,text); await execute("UPDATE app_tickets SET status='answered',updated_at=NOW(),unread_user=unread_user+1 WHERE id=$1",tid); await audit(uid,"ticket_reply",details={"ticket_id":tid})
    try: await update.get_bot().send_message(ticket["user_id"],f"👨‍💻 Team AKBSHAV TOOLS answered you:\n\n{text}")
    except Exception as exc: log.warning("ticket reply delivery failed: %s",exc)
    await update.message.reply_text("✅ Ответ отправлен.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await clear_state("app_admin_states","admin_id",update.effective_user.id)
    await update.effective_message.reply_text("❌ Отменено.",reply_markup=main_kb())


async def event_worker(context: ContextTypes.DEFAULT_TYPE) -> None:
    async with __import__("db.database",fromlist=["connection"]).connection() as conn:
        async with conn.transaction():
            rows=await conn.fetch("""WITH picked AS (SELECT id FROM app_events WHERE delivered=FALSE AND (locked_at IS NULL OR locked_at<NOW()-INTERVAL '60 seconds') ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 20) UPDATE app_events e SET locked_at=NOW() FROM picked WHERE e.id=picked.id RETURNING e.id,e.event_type,e.payload""")
    if not rows: return
    admin_ids=list(ADMIN_IDS)
    for row in rows:
        payload=row["payload"]; text=f"📋 {esc(row['event_type'])}\n{esc(json.dumps(payload,ensure_ascii=False)[:1000])}"
        if row["event_type"]=="business_connected": text=f"🔗 <b>Новое подключение</b>\nID: <code>{payload.get('user_id')}</code>\nUsername: @{esc(payload.get('username') or '-')}"
        elif row["event_type"]=="ticket_created": text=f"🎫 <b>Новый тикет</b>\n#{payload.get('ticket_id')}\nUser ID: <code>{payload.get('user_id')}</code>"
        delivered=True
        for aid in admin_ids:
            try: await context.bot.send_message(aid,text,parse_mode=ParseMode.HTML)
            except Exception: delivered=False
        if delivered and admin_ids: await execute("UPDATE app_events SET delivered=TRUE,delivered_at=NOW(),locked_at=NULL WHERE id=$1",row["id"])
        elif not admin_ids: await execute("UPDATE app_events SET locked_at=NULL WHERE id=$1",row["id"])
        else: await execute("UPDATE app_events SET locked_at=NULL WHERE id=$1",row["id"])


async def global_error(update, context):
    uid = getattr(getattr(update, "effective_user", None), "id", None)
    log.error("Unhandled admin update: %r", context.error, exc_info=context.error)
    try:
        await insert_security_event(uid, "admin_unhandled_error", "error", {"error": type(context.error).__name__ if context.error else "unknown"})
    except Exception:
        pass
    message = getattr(update, "effective_message", None)
    if message:
        try: await message.reply_text("⚠️ Не удалось обработать запрос. Попробуйте ещё раз.")
        except Exception: pass


async def post_init(application: Application) -> None:
    await init_db()


def build_app() -> Application:
    app=Application.builder().token(ADMIN_BOT_TOKEN).post_init(post_init).post_shutdown(lambda app: close_db()).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("reply",reply_command)); app.add_handler(CommandHandler("cancel",cancel)); app.add_handler(CallbackQueryHandler(callback)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,auth_message)); app.add_error_handler(global_error)
    if app.job_queue is not None: app.job_queue.run_repeating(event_worker,interval=3,first=1)
    return app


def main() -> None:
    build_app().run_polling(close_loop=True)


if __name__ == "__main__":
    main()
