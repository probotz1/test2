import time
import math

def progress_for_pyrogram(current, total, start, type_of_transfer, message):
    """
    Displays the progress of a file transfer operation.

    :param current: The current amount of bytes transferred.
    :param total: The total amount of bytes to be transferred.
    :param start: The start time of the transfer.
    :param type_of_transfer: A string describing the type of transfer (e.g., "Upload", "Download").
    :param message: The message object to edit with the progress.
    """
    now = time.time()
    diff = now - start
    if diff == 0:
        return "Calculating..."
    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed
    human_speed = humanbytes(speed)

    progress_str = "{0}: [{1}{2}] {3}%\nSpeed: {4}/s\nETA: {5}".format(
        type_of_transfer,
        ''.join(["■" for i in range(math.floor(percentage / 10))]),
        ''.join(["□" for i in range(10 - math.floor(percentage / 10))]),
        round(percentage, 2),
        human_speed,
        time.strftime("%H:%M:%S", time.gmtime(eta))
    )
    await message.edit_text(progress_str)

def convert(seconds):
    """
    Converts seconds to a human-readable format (D days, H hours, M minutes, S seconds).

    :param seconds: The number of seconds to convert.
    :return: A string representing the time in a human-readable format.
    """
    result = []
    intervals = (
        ('weeks', 604800),  # 60 * 60 * 24 * 7
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        ('seconds', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result)

def humanbytes(size):
    """
    Converts bytes to a human-readable format (e.g., KB, MB, GB).

    :param size: The number of bytes.
    :return: A string representing the size in a human-readable format.
    """
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: 'Bytes', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB'}
    while size > power:
        size /= power
        n += 1
    return "{:.2f} {}".format(size, Dic_powerN[n])
