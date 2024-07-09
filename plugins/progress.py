import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

def run_command(command):
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def remove_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-an', output_file]
    return run_command(command)

def trim_video(input_file, start_time, end_time, output_file):
    command = [
        'ffmpeg', '-i', input_file,
        '-ss', start_time,
        '-to', end_time,
        '-c', 'copy',
        output_file
    ]
    return run_command(command)

def process_video(action, input_file, output_file, start_time=None, end_time=None):
    if action == 'remove_audio':
        return executor.submit(remove_audio, input_file, output_file).result()
    elif action == 'trim_video':
        return executor.submit(trim_video, input_file, start_time, end_time, output_file).result()
    else:
        raise ValueError("Invalid action")

def progress_bar_template(percentage):
    length = 50  # Length of the progress bar
    block = int(round(length * percentage))
    return f"[{'#' * block + '-' * (length - block)}] {percentage * 100:.2f}%"
