import time

def progress_for_pyrogram(current, total, status, message):
    percentage = current * 100 / total
    message.edit_text(f"{status}: {percentage:.2f}%")
