import csv
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def rows():
    with open('2022_place_canvas_history.csv') as f:
        csvreader = csv.reader(f)
        # Discard the header
        next(csvreader)
        for row in csvreader:
            yield row


def make_datetime(timestamp):
    try:
        milliseconds = int(float(timestamp[19:].split(" ")[0])*1e3)
    except Exception:
        milliseconds = 0

    return datetime.strptime(timestamp[:19], '%Y-%m-%d %H:%M:%S') + timedelta(milliseconds=milliseconds)

tempdir = Path('tmp')
if not tempdir.is_dir():
    tempdir.mkdir()

with open(tempdir / 'quarter1_unsorted.csv', 'w') as f1, \
        open(tempdir / 'quarter2_unsorted.csv', 'w') as f2, \
        open(tempdir / 'quarter3_unsorted.csv', 'w') as f3, \
        open(tempdir / 'quarter4_unsorted.csv', 'w') as f4, \
        open(tempdir / 'dev_squares.csv', 'w') as f5:
    writer1 = csv.writer(f1)
    writer2 = csv.writer(f2)
    writer3 = csv.writer(f3)
    writer4 = csv.writer(f4)
    writer5 = csv.writer(f5)

    for i, (timestamp, user_id, color, coord) in enumerate(rows()):
        dt = make_datetime(timestamp)
        split_coords = [f'{int(i):04d}' for i in coord.split(",")]
        x, y = int(split_coords[0]), int(split_coords[1])
        writer = writer5 if len(split_coords) != 2 else \
                writer1 if x < 1000 and y < 1000 else \
                writer2 if x >= 1000 and y < 1000 else \
                writer3 if x < 1000 and y >= 1000 else writer4
        writer.writerow(split_coords + [dt.isoformat(timespec='milliseconds'), color, user_id[:16]])
        if i % 100000 == 0:
            print(f'Formatting and splitting: {100*i/160353085:.3f}%')

for i in [1,2,3,4]:
    unsorted_path = str(tempdir / f'quarter{i}_unsorted.csv')
    sorted_path = str(tempdir / f'quarter{i}.csv')
    print(f"Sorting {unsorted_path}")
    subprocess.run(f"sort {unsorted_path} > {sorted_path}", shell=True)
    subprocess.run(f"rm {unsorted_path}", shell=True)
