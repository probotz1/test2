import math
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def progress_for_pyrogram(current, total, message, start):
    now = time.time()
    diff = now - start

    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        estimated_total_time = (total / speed) * 1000

        progress = "[{0}{1}] \n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))])
        )

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            TimeFormatter(estimated_total_time - elapsed_time)
        )

        try:
            message.edit_text(
                text="{}\n{}".format(
                    tmp,
                    "Downloaded"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "Cancel",
                            callback_data="cancel"
                        )
                    ]]
                )
            )
        except Exception as e:
            print(e)

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}B"

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    tmp = (
        (str(days) + "d, ") if days else ""
    ) + (
        (str(hours) + "h, ") if hours else ""
    ) + (
        (str(minutes) + "m, ") if minutes else ""
    ) + (
        (str(seconds) + "s, ") if seconds else ""
    ) + (
        (str(milliseconds) + "ms, ") if milliseconds else ""
    )
    return tmp[:-2]
