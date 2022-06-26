from datetime import datetime, timedelta
from PIL import Image
import sys
import sqlite3
import subprocess

# timestamp = datetime.fromisoformat(sys.argv[1]).timestamp() * 1000
start_timestamp = datetime.fromisoformat("2022-04-01T12:50:00")
x0, y0, x1, y1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
width, height = x1-x0, y1-y0

def load_color(color):
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


with sqlite3.connect('place.db') as connection:
    cur = connection.cursor()
    for i in range(4 * 24 * 60):
        timestamp = (start_timestamp + timedelta(minutes=i)).timestamp() * 1000
        cur.execute('select x, y, color from place where x >= :x0 and x < :x1 and y >= :y0 and y < :y1 and startTime <= :timestamp and endTime >= :timestamp', {'timestamp': timestamp, 'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1})

        img = Image.new('RGB', (width, height), color='white')
        px = img.load()

        for x, y, color in cur.fetchall():
            px[x-x0, y-y0] = load_color(color)

        img.save(f'out/{i:04d}.png')

if width > height:
    video_width = min(width*64, 1920)
    video_height = int(video_width * height / width)
else:
    video_height = min(height*64, 1080)
    video_width = int(video_height * width / height)

subprocess.run(f'ffmpeg -r 300 -i out/%04d.png -c:v libx264 -sws_flags neighbor -vf fps=25 -vf scale={video_width}x{video_height} -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -pix_fmt yuv420p out.mp4', shell=True)
subprocess.run('rm out/*.png', shell=True)
