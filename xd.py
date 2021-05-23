import csv
from itertools import dropwhile, takewhile

def getstuff(filename, criterion):
    with open(filename, "rb") as csvfile:
        datareader = csv.reader(csvfile)
        yield next(datareader)  # yield the header row
        # first row, plus any subsequent rows that match, then stop
        # reading altogether
        # Python 2: use `for row in takewhile(...): yield row` instead
        # instead of `yield from takewhile(...)`.
        yield from takewhile(
            lambda r: r[3] == criterion,
            dropwhile(lambda r: r[3] != criterion, datareader))
        return

