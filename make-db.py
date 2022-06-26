import sqlite3
import csv
import itertools
from datetime import datetime

MAKE_RTREE = """
create virtual table rtree using rtree(
    id,
    startTime, endTime,
    x0, x1,
    y0, y1
);
"""
MAKE_DETAILS = """
create table details (
    id integer primary key,
    color text not null,
    userId text not null
);
"""
MAKE_VIEW = """
create view place as 
select
    rtree.x0 as x,
    rtree.y0 as y,
    rtree.startTime as startTime,
    rtree.endTime as endTime,
    details.color as color,
    details.userId as userId
from rtree join details on rtree.id = details.id;
"""
INSERT_RTREE = "insert into rtree (id, x0, x1, y0, y1, startTime, endTime) values (?,?,?,?,?,?,?);"
INSERT_DETAILS = "insert into details (id, color, userId) values (?,?,?);"


def lines():
    for i in [1,2,3,4]:
        with open(f'tmp/quarter{i}.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                yield row


def pairs():
    a, b = itertools.tee(lines())
    next(b)
    return zip(a, b)


with sqlite3.connect("place.db") as connection:
    connection.execute(MAKE_RTREE)
    connection.execute(MAKE_DETAILS)
    connection.execute(MAKE_VIEW)
    cur = connection.cursor()
    cur.execute('begin transaction;')

    for i, ( \
            (x0, y0, timestamp0, color0, userId0), \
            (x1, y1, timestamp1, color1, userId1), \
            ) in enumerate(pairs()):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        timestamp0 = int(datetime.fromisoformat(timestamp0).timestamp() * 1000)
        timestamp1 = int(datetime.fromisoformat(timestamp1).timestamp() * 1000) \
                if x0 == x1 and y0 == y1 else int(1e15)
        cur.execute(INSERT_RTREE, (i, x0, x0, y0, y0, timestamp0, timestamp1))
        cur.execute(INSERT_DETAILS, (i, color0, userId0))

        if i % 100000 == 0:
            print(f'Loading db: {i}/160353085 {100*i/160353085:.3f}%')
            cur.execute('commit;')

    cur.execute(INSERT_RTREE, (i+1, x1, x1, y1, y1, timestamp1, int(1e15)))
    cur.execute(INSERT_DETAILS, (i+1, color1, userId1))
    cur.execute('commit;')
