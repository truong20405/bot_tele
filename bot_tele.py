import os
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue
from call_api import get_link_bao, tom_tat_bao, tro_chuyen

def get_link_file(chat_id):
    """Lấy tên file link.txt dựa trên chat_id."""
    return f"link_{chat_id}.txt"

def read_saved_links(chat_id):
    """Đọc danh sách các liên kết đã lưu từ tệp của chat_id."""
    link_file = get_link_file(chat_id)
    if not os.path.exists(link_file):
        return set()
    with open(link_file, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)

def save_link(chat_id, link):
    """Lưu liên kết mới vào tệp của chat_id nếu nó chưa tồn tại."""
    link_file = get_link_file(chat_id)
    with open(link_file, "a", encoding="utf-8") as file:
        file.write(f"{link}\n")

async def clear_links(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xóa tất cả các liên kết trong tệp của chat_id."""
    chat_id = context.job.chat_id
    link_file = get_link_file(chat_id)
    print(f"Xóa danh sách liên kết cho chat_id: {chat_id}...")
    open(link_file, "w", encoding="utf-8").close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Chào mừng {update.effective_user.first_name}! Tôi là bot trợ giúp của bạn. Hãy dùng /help để xem tôi có thể làm gì.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hiển thị chi tiết các lệnh hỗ trợ"""
    help_text = """🤖 Danh sách các lệnh hỗ trợ:
/start - Bắt đầu trò chuyện với bot
/help - Hiển thị danh sách các lệnh hỗ trợ
/tu_dong - Bật chế độ tự động gửi tóm tắt bài báo mỗi 5 phút
/dung_lai - Dừng chế độ tự động gửi tóm tắt
/talk <nội dung> - Gửi câu hỏi của bạn tới bot để được trả lời

Ghi chú:
- Bot sẽ không gửi lại bài báo đã tóm tắt trước đó
- Chỉ hỗ trợ tóm tắt bài báo từ VNExpress
- Mỗi lần bật /tu_dong sẽ ghi đè cài đặt trước đó"""
    
    await update.message.reply_text(help_text)

async def auto_send_summary(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    link = get_link_bao()
    saved_links = read_saved_links(chat_id)

    if link not in saved_links:
        text = tom_tat_bao(link)
        vietnam_tz = timezone(timedelta(hours=7))
        timestamp = datetime.now(vietnam_tz).strftime("[%Y-%m-%d %H:%M:%S]")
        print(f'Gửi đến id: {chat_id},{timestamp}')
        await context.bot.send_message(chat_id=chat_id, text=f"{timestamp}\n{text}")
        save_link(chat_id, link)

async def start_auto_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(f"auto_summary_{chat_id}")
    for job in current_jobs:
        job.schedule_removal()
    context.job_queue.run_repeating(
        auto_send_summary, 
        interval=300,
        first=0, 
        chat_id=chat_id, 
        name=f"auto_summary_{chat_id}"
    )
    print(f"Bật chế độ tự động cho chat_id: {chat_id}-", update.effective_user.first_name)

async def stop_auto_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(f"auto_summary_{chat_id}")
    for job in current_jobs:
        job.schedule_removal()
    print(f"Tắt chế độ tự động cho chat_id: {chat_id}")
    await update.message.reply_text("Đã tắt chế độ tự động gửi tóm tắt.")

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi câu hỏi từ người dùng tới hàm tro_chuyen."""
    if context.args:
        question = " ".join(context.args)
        response = tro_chuyen(question)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Vui lòng nhập nội dung câu hỏi sau lệnh /talk.")

def main():
    app = ApplicationBuilder().token("7645912732:AAGsRAUdriJysS6hO5_JHYStMhEdaj-8Brg").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tu_dong", start_auto_summary))
    app.add_handler(CommandHandler("dung_lai", stop_auto_summary))
    app.add_handler(CommandHandler("talk", talk_command))
    
    # Thêm job xóa liên kết định kỳ mỗi 3 ngày cho từng chat_id
    app.job_queue.run_repeating(clear_links, interval=259200, first=0)
    
    os.system('clear')
    print('Bắt đầu chạy bot ....')
    app.run_polling()
