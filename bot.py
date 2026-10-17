import os
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
db = sqlite3.connect("workshop.db", check_same_thread=False)
db.execute("""CREATE TABLE IF NOT EXISTS records (
date TEXT, kind TEXT, amount INTEGER, description TEXT
)""")
db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام آرش جان 👷\n"
        "ربات حسابداری کارگاه\n\n"
        "/expense مبلغ شرح - ثبت هزینه\n"
        "/income مبلغ شرح - ثبت دریافتی\n"
        "/worker مبلغ نام - ثبت دستمزد\n"
        "/report - گزارش حساب‌ها"
    )

async def save(update, context, kind):
    if len(context.args) < 2:
        await update.message.reply_text("مبلغ و شرح رو بنویس")
        return
    try:
        amount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("مبلغ باید عدد باشه")
        return
    desc = " ".join(context.args[1:])
    db.execute(
        "INSERT INTO records VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), kind, amount, desc)
    )
    db.commit()
    await update.message.reply_text(f"✅ ثبت شد\n{desc}\n{amount:,} تومان")

async def expense(u, c):
    await save(u, c, "هزینه")

async def income(u, c):
    await save(u, c, "دریافتی")

async def worker(u, c):
    await save(u, c, "دستمزد")

async def report(update, context):
    rows = db.execute(
        "SELECT kind, SUM(amount) FROM records GROUP BY kind"
    ).fetchall()
    result = "📊 گزارش حساب کارگاه\n"
    totals = dict(rows)
    for kind in ("دریافتی", "هزینه", "دستمزد"):
        result += f"{kind}: {totals.get(kind, 0):,} تومان\n"
    balance = totals.get("دریافتی", 0) - totals.get("هزینه", 0) - totals.get("دستمزد", 0)
    result += f"\nمانده حساب: {balance:,} تومان"
    await update.message.reply_text(result)

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("expense", expense))
app.add_handler(CommandHandler("income", income))
app.add_handler(CommandHandler("worker", worker))
app.add_handler(CommandHandler("report", report))
app.run_polling()
