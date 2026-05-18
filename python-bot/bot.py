
import os
import asyncio
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler,
)

# ── Config ─────────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.environ["8796607447:AAHrAD8XAGypkwmooCq_q4NUqKOLEd-_ITw"]
API_BASE_URL = os.environ["https://cinemamax-api.onrender.com"].rstrip("/")   
WEB_APP_URL  = os.environ.get("WEB_APP_URL", f"{API_BASE_URL}/")

STANDARD_PRICE = 20
VIP_PRICE      = 50
MOVIES_PER_PAGE = 6

# Conversation states
CHOICE, GALLERY, TIMES, SEATS, CONFIRM = range(5)


# ── HTTP helpers (async, uses aiohttp) ────────────────────────────────────────

async def api_get(path: str):
    """GET /api/… and return parsed JSON."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}{path}") as r:
            r.raise_for_status()
            return await r.json()


async def api_post(path: str, payload: dict):
    """POST /api/… with JSON body and return parsed JSON."""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}{path}", json=payload) as r:
            data = await r.json()
            return r.status, data


# ── Data helpers ───────────────────────────────────────────────────────────────

async def get_movies():
    return await api_get("/api/movies")

async def get_showtimes(movie_id: int):
    return await api_get(f"/api/movies/{movie_id}/showtimes")

async def get_booked_seats(showtime_id: int):
    return set(await api_get(f"/api/showtimes/{showtime_id}/seats"))

async def book_seats(showtime_id: int, seats: list[str]):
    status, data = await api_post("/api/bookings", {
        "showtimeId": showtime_id,
        "seats": seats,
    })
    return data  # {success, message, totalPrice}


# ── Formatting helpers ─────────────────────────────────────────────────────────

def seat_label(pos: str) -> str:
    row, col = pos.split("-")
    return f"{chr(65 + int(row))}{int(col) + 1}"

def avail_label(avail: int) -> str:
    return f"⚠️ {avail} left" if avail < 15 else f"✅ {avail} seats"


# ── /start & Choice ────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("📱 Open Web App", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("🤖 Book in Telegram", callback_data="choice:telegram")]
    ]
    text = "Welcome to CinemaMax! 🎬\n\nHow would you like to book your tickets?"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOICE

async def on_choice(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "choice:telegram":
        ctx.user_data['page'] = 0
        return await show_gallery(update, ctx)
    return CHOICE


# ── Step 1: Movie gallery ──────────────────────────────────────────────────────

async def show_gallery(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    movies = await get_movies()
    page   = ctx.user_data.get('page', 0)

    total_pages = (len(movies) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE
    page_movies = movies[page * MOVIES_PER_PAGE:(page + 1) * MOVIES_PER_PAGE]

    keyboard = []
    for m in page_movies:
        star  = "⭐ " if m["blockbuster"] else ""
        label = f"{star}{m['title']}  [{m['genre']}]  ({m['showCount']} showings)"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"movie:{m['id']}:{m['title']}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page:{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"page:{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="back:start")])

    await update.callback_query.edit_message_text(
        f"🎬 *CinemaMax — Now Showing*\n\nPick a movie (Page {page+1}/{total_pages}):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GALLERY

async def on_page_change(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    ctx.user_data['page'] = int(query.data.split(":")[1])
    return await show_gallery(update, ctx)

async def on_movie_selected(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, movie_id, title = query.data.split(":", 2)
    ctx.user_data["movie_id"]    = int(movie_id)
    ctx.user_data["movie_title"] = title
    return await show_showtimes(update, ctx)


# ── Step 2: Showtimes ──────────────────────────────────────────────────────────

async def show_showtimes(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    rows  = await get_showtimes(ctx.user_data["movie_id"])
    title = ctx.user_data["movie_title"]

    keyboard = []
    for s in rows:
        vip   = "★ VIP  " if s["vip"] else ""
        label = f"{vip}{s['hallName']}  {s['showTime']}  — {avail_label(s['available'])}"
        keyboard.append([InlineKeyboardButton(
            label,
            callback_data=f"show:{s['id']}:{s['hallName']}:{s['showTime']}:{1 if s['vip'] else 0}"
        )])

    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back:gallery")])

    await update.callback_query.edit_message_text(
        f"🎭 *{title}*\n\nChoose a showtime:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TIMES

async def on_showtime_selected(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, sid, hall, time, vip_flag = query.data.split(":", 4)
    ctx.user_data.update({
        "showtime_id": int(sid),
        "hall": hall,
        "time": time,
        "is_vip": vip_flag == "1",
        "selected": [],
    })
    return await show_seat_map(update, ctx)


# ── Step 3: Seat selection ─────────────────────────────────────────────────────

async def show_seat_map(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    sid    = ctx.user_data["showtime_id"]
    is_vip = ctx.user_data["is_vip"]
    title  = ctx.user_data["movie_title"]
    hall   = ctx.user_data["hall"]
    time   = ctx.user_data["time"]
    sel    = set(ctx.user_data.get("selected", []))
    booked = await get_booked_seats(sid)

    rows = 4 if is_vip else 8
    cols = 6 if is_vip else 12

    keyboard = [[InlineKeyboardButton(str(c + 1), callback_data="noop") for c in range(cols)]]
    for r in range(rows):
        row_btns = [InlineKeyboardButton(chr(65 + r), callback_data="noop")]
        for c in range(cols):
            pos = f"{r}-{c}"
            if pos in booked:
                emoji, cb = "🔴", "noop"
            elif pos in sel:
                emoji, cb = "🟢", f"seat:deselect:{pos}"
            else:
                emoji, cb = "⬜", f"seat:select:{pos}"
            row_btns.append(InlineKeyboardButton(emoji, callback_data=cb))
        keyboard.append(row_btns)

    count  = len(sel)
    price  = VIP_PRICE if is_vip else STANDARD_PRICE
    total  = count * price
    labels = sorted(seat_label(p) for p in sel)
    summary = f"Selected: {', '.join(labels) if labels else '—'}\nTotal: ${total}.00"

    keyboard.append([
        InlineKeyboardButton("✅ Confirm Booking", callback_data="confirm"),
        InlineKeyboardButton("⬅️ Back",            callback_data="back:times"),
    ])

    vip_tag = "  ★ VIP" if is_vip else ""
    header_text = (
        f"🎬 *{title}*{vip_tag}\n"
        f"📍 {hall}  🕐 {time}\n"
        f"⬜ Available  🟢 Selected  🔴 Booked\n\n"
        f"{summary}"
    )

    await update.callback_query.edit_message_text(
        header_text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SEATS

async def on_seat_toggle(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    _, action, pos = query.data.split(":", 2)
    sel = ctx.user_data.setdefault("selected", [])
    if action == "select" and pos not in sel:
        sel.append(pos)
    elif action == "deselect" and pos in sel:
        sel.remove(pos)
    return await show_seat_map(update, ctx)


# ── Step 4: Confirm & book ─────────────────────────────────────────────────────

async def on_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    sel = ctx.user_data.get("selected", [])
    if not sel:
        await query.answer("❗ Please select at least one seat first.", show_alert=True)
        return SEATS

    is_vip = ctx.user_data["is_vip"]
    price  = VIP_PRICE if is_vip else STANDARD_PRICE
    total  = len(sel) * price
    labels = sorted(seat_label(p) for p in sel)

    ticket = (
        f"🎟 *Booking Summary*\n\n"
        f"🎬 *Film:* {ctx.user_data['movie_title']}\n"
        f"📍 *Hall:* {'★ VIP Platinum' if is_vip else ctx.user_data['hall']}\n"
        f"🕐 *Time:* {ctx.user_data['time']}\n"
        f"💺 *Seats:* {', '.join(labels)}\n"
        f"🎫 *Tickets:* {len(sel)} × ${price}.00\n"
        f"💰 *Total:* ${total}.00"
    )

    await query.edit_message_text(ticket, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Pay & Book", callback_data="book"),
        InlineKeyboardButton("⬅️ Back",       callback_data="back:seats"),
    ]]))
    return CONFIRM

async def on_book(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    sel   = ctx.user_data.get("selected", [])
    sid   = ctx.user_data["showtime_id"]
    title = ctx.user_data["movie_title"]

    try:
        result = await book_seats(sid, sel)
        if result.get("success"):
            labels = sorted(seat_label(p) for p in sel)
            await query.edit_message_text(
                f"✅ *Booking Confirmed!*\n\n"
                f"🎬 {title}\n"
                f"💺 Seats: {', '.join(labels)}\n"
                f"💰 Total: ${result['totalPrice']}.00\n\n"
                f"Enjoy the show! 🍿\n\nType /start to book again.",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"❌ {result.get('message', 'Booking failed.')}\n\nType /start to try again."
            )
    except Exception as e:
        await query.edit_message_text(f"❌ Error: {e}\n\nType /start to try again.")

    ctx.user_data.clear()
    return ConversationHandler.END


# ── Back navigation ────────────────────────────────────────────────────────────

async def on_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    dest = query.data.split(":")[1]
    if dest == "start":      return await start(update, ctx)
    elif dest == "gallery":  return await show_gallery(update, ctx)
    elif dest == "times":    return await show_showtimes(update, ctx)
    elif dest == "seats":    return await show_seat_map(update, ctx)

async def noop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOICE:  [CallbackQueryHandler(on_choice, pattern=r"^choice:")],
            GALLERY: [
                CallbackQueryHandler(on_movie_selected, pattern=r"^movie:"),
                CallbackQueryHandler(on_page_change,    pattern=r"^page:"),
                CallbackQueryHandler(on_back,           pattern=r"^back:start"),
            ],
            TIMES:   [
                CallbackQueryHandler(on_showtime_selected, pattern=r"^show:"),
                CallbackQueryHandler(on_back,              pattern=r"^back:"),
            ],
            SEATS:   [
                CallbackQueryHandler(on_seat_toggle, pattern=r"^seat:"),
                CallbackQueryHandler(on_confirm,     pattern=r"^confirm$"),
                CallbackQueryHandler(on_back,        pattern=r"^back:"),
                CallbackQueryHandler(noop,           pattern=r"^noop$"),
            ],
            CONFIRM: [
                CallbackQueryHandler(on_book, pattern=r"^book$"),
                CallbackQueryHandler(on_back, pattern=r"^back:"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
    )

    app.add_handler(conv)
    print("✅ CinemaMax bot running (calls Java API)…  (Ctrl-C to stop)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
