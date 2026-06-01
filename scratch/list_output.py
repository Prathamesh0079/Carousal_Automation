import os, glob

files = glob.glob("output/slide_*.png")
files.sort()
for f in files:
    stat = os.stat(f)
    print(f"{f}: size={stat.st_size} bytes, mod_time={stat.st_mtime}")
