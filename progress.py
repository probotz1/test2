import time

def progress(current, total, message, start_time):
    now = time.time()
    diff = now - start_time
    if diff == 0:
        return

    percentage = current * 100 / total
    speed = current / diff
    time_to_completion = (total - current) / speed
    estimated_total_time = diff + time_to_completion

    progress_str = "{0:.1f}%\n[{1}{2}]".format(
        percentage,
        ''.join(["#" for i in range(math.floor(percentage / 10))]),
        ''.join(["-" for i in range(10 - math.floor(percentage / 10))])
    )

    tmp = progress_str + "\n{0} of {1}\nSpeed: {2}/s\nETA: {3}".format(
        humanbytes(current),
        humanbytes(total),
        humanbytes(speed),
        time.strftime("%H:%M:%S", time.gmtime(estimated_total_time))
    )

    try:
        message.edit_text(text="Downloading...\n" + tmp)
    except:
        pass
