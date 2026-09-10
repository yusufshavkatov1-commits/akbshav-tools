from __future__ import annotations
import html, json, logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import Application, BusinessConnectionHandler, BusinessMessagesDeletedHandler, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from common.config import AUTO_REPLY_COOLDOWN, COMMAND_PREFIX, REQUIRED_CHANNEL, RATE_LIMIT_PER_MINUTE
from common.i18n import LANGS, t
from db.database import clear_state, connection, execute, fetch, fetchrow, get_state, init_db, insert_event, insert_function_error, insert_security_event, rate_limit, set_state
from user_bot.features import FUNCTIONS, bubble, coin, dumb, glitch, heart, leet, limited_repeat, matrix, nospace, normalize, reverse, spoiler, words, print_effect, command_help
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log=logging.getLogger("akbshav.user")
STATE_SUPPORT="support"
def lang_keyboard(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇷🇺 Русский",callback_data="lang:ru"),InlineKeyboardButton("🇺🇿 O'zbek",callback_data="lang:uz")],[InlineKeyboardButton("🇬🇧 English",callback_data="lang:en")]])
def rules_keyboard(lang): return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"accept"),callback_data="rules:yes"),InlineKeyboardButton(t(lang,"decline"),callback_data="rules:no")]])
def subscription_keyboard(lang): return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"subscribe"),url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")],[InlineKeyboardButton(t(lang,"check"),callback_data="sub:check")]])
def main_keyboard(lang): return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"functions"),callback_data="menu:functions"),InlineKeyboardButton(t(lang,"automation"),callback_data="menu:auto")],[InlineKeyboardButton(t(lang,"library"),callback_data="menu:library"),InlineKeyboardButton(t(lang,"support"),callback_data="menu:support")],[InlineKeyboardButton(t(lang,"settings"),callback_data="menu:settings"),InlineKeyboardButton(t(lang,"help"),callback_data="menu:help")]])
def back_keyboard(lang): return InlineKeyboardMarkup([[InlineKeyboardButton(t(lang,"back"),callback_data="back")]])
def settings_keyboard(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇷🇺 RU",callback_data="setlang:ru"),InlineKeyboardButton("🇺🇿 UZ",callback_data="setlang:uz"),InlineKeyboardButton("🇬🇧 EN",callback_data="setlang:en")],[InlineKeyboardButton("⬅️",callback_data="back")]])
async def upsert_user(user): await execute("INSERT INTO app_users(telegram_id,username,first_name,last_name) VALUES($1,$2,$3,$4) ON CONFLICT(telegram_id) DO UPDATE SET username=$2,first_name=$3,last_name=$4,last_seen_at=NOW()",user.id,user.username,user.first_name,user.last_name)
async def get_lang(uid):
    r=await fetchrow("SELECT language FROM app_users WHERE telegram_id=$1",uid); return r["language"] if r and r["language"] in LANGS else "ru"
async def check_subscription(bot,uid):
    try: m=await bot.get_chat_member(REQUIRED_CHANNEL,uid); ok=m.status in {ChatMemberStatus.MEMBER,ChatMemberStatus.ADMINISTRATOR,ChatMemberStatus.OWNER}
    except Exception as exc: log.warning("subscription check failed: %s",type(exc).__name__); ok=False
    await execute("UPDATE app_users SET subscription_ok=$1 WHERE telegram_id=$2",ok,uid); return ok
async def has_access(bot,uid):
    r=await fetchrow("SELECT rules_accepted,blocked FROM app_users WHERE telegram_id=$1",uid); return bool(r and r["rules_accepted"] and not r["blocked"] and await check_subscription(bot,uid))
async def require_access(update,context):
    u=update.effective_user
    if not u:return False
    lang=await get_lang(u.id)
    if await has_access(context.bot,u.id):return True
    try:
        if update.callback_query: await update.callback_query.edit_message_text(t(lang,"access_denied"),reply_markup=subscription_keyboard(lang))
        elif update.effective_message: await update.effective_message.reply_text(t(lang,"access_denied"),reply_markup=subscription_keyboard(lang))
    except Exception: pass
    return False
async def start(update,context):
    if not update.effective_user or not update.message:return
    uid=update.effective_user.id; await upsert_user(update.effective_user); await clear_state("app_user_states","user_id",uid); lang=await get_lang(uid); r=await fetchrow("SELECT rules_accepted,blocked FROM app_users WHERE telegram_id=$1",uid)
    if r and r["rules_accepted"] and not r["blocked"]:
        subscribed=await check_subscription(context.bot,uid); await update.message.reply_text(t(lang,"main") if subscribed else t(lang,"sub_required"),reply_markup=main_keyboard(lang) if subscribed else subscription_keyboard(lang)); return
    await update.message.reply_text(t(lang,"choose_lang"),reply_markup=lang_keyboard())
async def cancel(update,context):
    if not update.effective_user or not update.effective_message:return
    await clear_state("app_user_states","user_id",update.effective_user.id); lang=await get_lang(update.effective_user.id); await update.effective_message.reply_text(t(lang,"cancelled"),reply_markup=main_keyboard(lang))
async def callback(update,context):
    q=update.callback_query; u=q.from_user; data=q.data or ""; lang=await get_lang(u.id)
    if len(data)>64: await q.answer(t(lang,"server_error"),show_alert=True); return
    await upsert_user(u); await q.answer()
    if data.startswith("lang:"):
        x=data.split(":",1)[1]
        if x not in LANGS:return
        await execute("UPDATE app_users SET language=$1 WHERE telegram_id=$2",x,u.id); await q.edit_message_text(t(x,"rules_title")+"\n\n"+t(x,"rules"),reply_markup=rules_keyboard(x)); return
    if data=="rules:yes":
        await execute("UPDATE app_users SET rules_accepted=TRUE WHERE telegram_id=$1",u.id); lang=await get_lang(u.id)
        if await check_subscription(context.bot,u.id): await insert_event("onboarding_completed",{"user_id":u.id,"language":lang}); await q.edit_message_text(t(lang,"main"),reply_markup=main_keyboard(lang))
        else: await q.edit_message_text(t(lang,"sub_required"),reply_markup=subscription_keyboard(lang))
        return
    if data=="rules:no": await q.edit_message_text(t(lang,"access_denied")); return
    if data=="sub:check":
        if await has_access(context.bot,u.id): await insert_event("onboarding_completed",{"user_id":u.id,"language":lang}); await q.edit_message_text(t(lang,"main"),reply_markup=main_keyboard(lang))
        else: await q.edit_message_text(t(lang,"sub_required"),reply_markup=subscription_keyboard(lang))
        return
    if data.startswith("setlang:"):
        x=data.split(":",1)[1]
        if x in LANGS: await execute("UPDATE app_users SET language=$1 WHERE telegram_id=$2",x,u.id); lang=x
        await q.edit_message_text(t(lang,"settings_text"),parse_mode=ParseMode.HTML,reply_markup=settings_keyboard()); return
    if not await require_access(update,context):return
    if data=="back": await clear_state("app_user_states","user_id",u.id); await q.edit_message_text(t(lang,"main"),reply_markup=main_keyboard(lang))
    elif data=="menu:functions": await q.edit_message_text(command_help(),parse_mode=ParseMode.HTML,reply_markup=back_keyboard(lang))
    elif data=="menu:auto":
        r=await fetchrow("SELECT is_enabled FROM app_business_connections WHERE user_id=$1",u.id); await q.edit_message_text((t(lang,"automation_status_on") if r and r["is_enabled"] else t(lang,"automation_status_off"))+"\n\n"+t(lang,"automation_help"),parse_mode=ParseMode.HTML,reply_markup=back_keyboard(lang))
    elif data=="menu:library":
        rows=await fetch("SELECT shortcut,text FROM app_quick_replies WHERE user_id=$1 ORDER BY id DESC LIMIT 20",u.id); body=t(lang,"library_title")+"\n\n"+("\n".join(f"<code>.{html.escape(r['shortcut'])}</code> — {html.escape(r['text'][:80])}" for r in rows) or t(lang,"library_empty")); await q.edit_message_text(body,parse_mode=ParseMode.HTML,reply_markup=back_keyboard(lang))
    elif data=="menu:support": await set_state("app_user_states","user_id",u.id,STATE_SUPPORT,{},30); await q.edit_message_text(t(lang,"support_prompt"),reply_markup=back_keyboard(lang))
    elif data=="menu:settings": await q.edit_message_text(t(lang,"settings_text"),parse_mode=ParseMode.HTML,reply_markup=settings_keyboard())
    elif data=="menu:help": await q.edit_message_text(t(lang,"help_text"),parse_mode=ParseMode.HTML,reply_markup=back_keyboard(lang))
async def create_ticket(uid,text):
    async with connection() as conn:
        async with conn.transaction(): tid=await conn.fetchval("INSERT INTO app_tickets(user_id) VALUES($1) RETURNING id",uid); await conn.execute("INSERT INTO app_ticket_messages(ticket_id,sender_type,sender_id,text) VALUES($1,'user',$2,$3)",tid,uid,text); return int(tid)
async def support_message(update,context):
    if not update.effective_user or not update.effective_message or not update.effective_message.text:return
    st=await get_state("app_user_states","user_id",update.effective_user.id)
    if not st or st[0]!=STATE_SUPPORT or not await require_access(update,context):return
    text=update.effective_message.text.strip()[:3500]
    if not text:return
    tid=await create_ticket(update.effective_user.id,text); await clear_state("app_user_states","user_id",update.effective_user.id); await insert_event("ticket_created",{"ticket_id":tid,"user_id":update.effective_user.id}); lang=await get_lang(update.effective_user.id); await update.message.reply_text(t(lang,"ticket_created",id=tid),reply_markup=main_keyboard(lang))
async def business_connection(update,context):
    b=update.business_connection
    if not b:return
    await upsert_user(b.user); rights=b.rights.to_dict() if b.rights else {}
    await execute("INSERT INTO app_business_connections(user_id,connection_id,is_enabled,rights_json) VALUES($1,$2,$3,$4::jsonb) ON CONFLICT(user_id) DO UPDATE SET connection_id=$2,is_enabled=$3,rights_json=$4::jsonb,updated_at=NOW()",b.user.id,b.id,b.is_enabled,json.dumps(rights,ensure_ascii=False)); await insert_event("business_connected" if b.is_enabled else "business_disconnected",{"user_id":b.user.id,"username":b.user.username,"connection_id":b.id})
    try: await context.bot.send_message(b.user.id,t(await get_lang(b.user.id),"connected") if b.is_enabled else t(await get_lang(b.user.id),"disconnected"))
    except Exception: pass
async def archive_business_message(m,uid): await execute("INSERT INTO app_message_archive(user_id,connection_id,chat_id,message_id,sender_id,text,message_date,kind) VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT(connection_id,chat_id,message_id) DO NOTHING",uid,m.business_connection_id,m.chat.id,m.message_id,m.from_user.id if m.from_user else None,m.text or m.caption,m.date,"text" if m.text else "media")
async def is_feature_enabled(key):
    r=await fetchrow("SELECT enabled FROM app_functions WHERE key=$1",key); return bool(r and r["enabled"])
async def mark_usage(uid,key): await execute("INSERT INTO app_usage(user_id,function_key) VALUES($1,$2)",uid,key); await execute("UPDATE app_functions SET usage_count=usage_count+1 WHERE key=$1",key)
async def send_business_text(bot,m,text):
    r=await fetchrow("SELECT rights_json,is_enabled FROM app_business_connections WHERE connection_id=$1",m.business_connection_id)
    if not r or not r["is_enabled"]:raise PermissionError("business connection disabled")
    rights=r["rights_json"] or {}; rights=json.loads(rights) if isinstance(rights,str) else rights
    if rights.get("can_reply") is False:raise PermissionError("can_reply denied")
    await bot.send_message(chat_id=m.chat.id,text=str(text)[:3500],business_connection_id=m.business_connection_id)
async def maybe_auto_reply(m,context,uid):
    if not await is_feature_enabled("auto_reply"):return
    r=await fetchrow("SELECT enabled,text,cooldown_seconds FROM app_auto_replies WHERE user_id=$1",uid)
    if not r or not r["enabled"] or not r["text"]:return
    cooldown=max(float(r["cooldown_seconds"]),AUTO_REPLY_COOLDOWN)
    if not await fetchrow("UPDATE app_auto_replies SET last_reply_at=NOW() WHERE user_id=$1 AND (last_reply_at IS NULL OR last_reply_at<=NOW()-($2*INTERVAL '1 second')) RETURNING user_id",uid,cooldown):return
    try:await send_business_text(context.bot,m,r["text"])
    except Exception as exc:await insert_function_error(uid,"auto_reply","ERR_AUTO_REPLY_FAILED",{"error":type(exc).__name__})
async def handle_business_command(m,context,uid,raw):
    body=raw[len(COMMAND_PREFIX):].strip(); parts=body.split(maxsplit=2)
    if not parts:return
    cmd=parts[0].lower(); args=parts[1:]; text=args[-1] if args else ""; lang=await get_lang(uid)
    try:
        if cmd not in FUNCTIONS:
            r=await fetchrow("SELECT text FROM app_quick_replies WHERE user_id=$1 AND shortcut=$2",uid,cmd); result=r["text"] if r else t(lang,"invalid_command")
        else:
            result={"help":command_help(),"помощь":command_help(),"reverse":reverse(normalize(text)),"nospace":nospace(text),"bubble":bubble(text),"leet":leet(text),"dumb":dumb(text),"glitch":glitch(text),"spoiler":spoiler(text),"words":words(text),"heart":heart(text),"print":print_effect(text),"matrix":matrix(text),"coin":coin(),"монета":coin()}.get(cmd)
            if cmd=="repeat":
                if len(args)<2:raise ValueError
                result=limited_repeat(args[1],int(args[0]))
            elif cmd=="quote":result=f"❝ {(m.reply_to_message.text or m.reply_to_message.caption)[:1000]} ❞" if m.reply_to_message and (m.reply_to_message.text or m.reply_to_message.caption) else ".quote: reply to a message"
            elif cmd=="autoreply":
                sub=body.split(maxsplit=1)
                if len(sub)==1:r=await fetchrow("SELECT enabled,text FROM app_auto_replies WHERE user_id=$1",uid); result=f"Auto Reply: {'ON' if r and r['enabled'] else 'OFF'}\n{(r['text'] if r else '')[:500]}"
                else:await execute("INSERT INTO app_auto_replies(user_id,enabled,text) VALUES($1,TRUE,$2) ON CONFLICT(user_id) DO UPDATE SET enabled=TRUE,text=$2,updated_at=NOW()",uid,sub[1][:500]); result="✅ Auto Reply enabled."
            elif cmd=="autoreplyoff":await execute("UPDATE app_auto_replies SET enabled=FALSE,updated_at=NOW() WHERE user_id=$1",uid); result="✅ Auto Reply disabled."
            elif cmd=="timer":
                if len(args)<2 or not 1<=int(args[0])<=3600:raise ValueError
                await execute("INSERT INTO app_jobs(job_type,user_id,run_at,payload) VALUES($1,$2,NOW()+($3*INTERVAL '1 second'),$4::jsonb)","business_message",uid,int(args[0]),json.dumps({"chat_id":m.chat.id,"connection_id":m.business_connection_id,"text":args[1][:3500]})); result=f"⏱ Scheduled in {args[0]}s."
            elif cmd=="save":
                if len(args)<2:raise ValueError
                shortcut=args[0].lower()[:32]; await execute("INSERT INTO app_quick_replies(user_id,shortcut,text) VALUES($1,$2,$3) ON CONFLICT(user_id,shortcut) DO UPDATE SET text=$3",uid,shortcut,args[1][:500]); result=f"✅ Saved .{shortcut}"
            elif cmd=="unsave":
                if not args:raise ValueError
                shortcut=args[0].lower()[:32]; await execute("DELETE FROM app_quick_replies WHERE user_id=$1 AND shortcut=$2",uid,shortcut); result=f"✅ Removed .{shortcut}"
            if result is None:result=t(lang,"invalid_command")
    except (ValueError,IndexError):result=t(lang,"invalid_command")
    except Exception as exc:await insert_function_error(uid,cmd,"ERR_FUNCTION_FAILED",{"error":type(exc).__name__}); result=t(lang,"server_error")
    await mark_usage(uid,cmd)
    try:await send_business_text(context.bot,m,result)
    except Exception as exc:await insert_function_error(uid,cmd,"ERR_BUSINESS_COMMAND_FAILED",{"error":type(exc).__name__})
async def business_message(update,context):
    m=update.business_message
    if not m or not m.business_connection_id or not m.from_user or getattr(m,"sender_business_bot",False):return
    r=await fetchrow("SELECT user_id,is_enabled FROM app_business_connections WHERE connection_id=$1",m.business_connection_id)
    if not r or not r["is_enabled"]:return
    uid=int(r["user_id"])
    if not await rate_limit(uid,"business_message",RATE_LIMIT_PER_MINUTE):await insert_security_event(uid,"rate_limit","warning",{"bucket":"business_message"});return
    if await is_feature_enabled("message_archive"):
        try:await archive_business_message(m,uid)
        except Exception as exc:await insert_function_error(uid,"message_archive","ERR_ARCHIVE_FAILED",{"error":type(exc).__name__})
    text=m.text or ""
    if text.startswith(COMMAND_PREFIX):
        if await is_feature_enabled("command_tools"):await handle_business_command(m,context,uid,text)
    else:await maybe_auto_reply(m,context,uid)
async def edited_business_message(update,context):
    m=update.edited_business_message
    if m and m.business_connection_id:await execute("UPDATE app_message_archive SET text=$1 WHERE connection_id=$2 AND chat_id=$3 AND message_id=$4",m.text or m.caption,m.business_connection_id,m.chat.id,m.message_id)
async def deleted_business_messages(update,context):
    d=update.deleted_business_messages
    if d:await execute("UPDATE app_message_archive SET deleted_at=NOW() WHERE connection_id=$1 AND chat_id=$2 AND message_id=ANY($3::bigint[])",d.business_connection_id,d.chat.id,list(d.message_ids)); await insert_event("business_messages_deleted",{"connection_id":d.business_connection_id,"chat_id":d.chat.id,"message_ids":list(d.message_ids)})
async def global_error(update,context):
    uid=getattr(getattr(update,"effective_user",None),"id",None); log.error("Unhandled Telegram update: %r",context.error,exc_info=context.error)
    try:await insert_function_error(uid,"system","ERR_UNHANDLED_UPDATE",{"error":type(context.error).__name__ if context.error else "unknown"})
    except Exception:pass
    m=getattr(update,"effective_message",None)
    if m:
        try:await m.reply_text(t(await get_lang(uid),"server_error") if uid else t("ru","server_error"))
        except Exception:pass
async def seed_registry():
    registry={"command_tools":("Commands","tools"),"message_archive":("Message Archive","messages"),"auto_reply":("Auto Reply","automation"),"help":("Help","utilities"),**{k:(k.replace("_"," ").title(),"text") for k in FUNCTIONS}}
    for k,(name,cat) in registry.items():
        await execute("INSERT INTO app_functions(key,category) VALUES($1,$2) ON CONFLICT DO NOTHING",k,cat)
        await execute("INSERT INTO app_function_registry(key,name,category) VALUES($1,$2,$3) ON CONFLICT DO NOTHING",k,name,cat)

async def post_init(application):
    await init_db(); await seed_registry()
async def post_shutdown(application):
    from db.database import close_db
    await close_db()
def build_app():
    from common.config import USER_BOT_TOKEN
    app=Application.builder().token(USER_BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build(); app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("cancel",cancel)); app.add_handler(CallbackQueryHandler(callback)); app.add_handler(BusinessConnectionHandler(business_connection)); app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE,business_message)); app.add_handler(MessageHandler(filters.UpdateType.EDITED_BUSINESS_MESSAGE,edited_business_message)); app.add_handler(BusinessMessagesDeletedHandler(deleted_business_messages)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,support_message),group=5); app.add_error_handler(global_error); return app
def main():build_app().run_polling(allowed_updates=["message","callback_query","business_connection","business_message","edited_business_message","deleted_business_messages"],close_loop=True)
if __name__=="__main__":main()
