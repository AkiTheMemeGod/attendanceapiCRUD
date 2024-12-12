from assets import *

d = Fetch()

subs = ["cs1", "cs2", "cs3", "cs4", "cs5"]
r = d.fetch_all_rolls()
for i in subs:
    for j in r:
        d.reset_attendance(j,i)