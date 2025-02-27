
import os
import re

source = r"C:\Users\ycham\Downloads"
destination = r"C:\Users\ycham\Downloads"

allfiles = os.listdir(source)

def move(file,source,destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
    os.rename(os.path.join(source, file), os.path.join(destination, file))

for file in allfiles:
    if re.match(".*\.(pdf|docx|ppt|txt)$", file):
        move(file,source,os.path.join(destination,"pdfs"))
    if re.match(".*\.(png|jpg|jpeg|svg|webp|)$", file):
        move(file,source,os.path.join(destination,"images"))
    if re.match(".*\.(csv|xlsx)$", file):
        move(file,source,os.path.join(destination,"datasheets"))
    if re.match(".*\.(mp4|mkv|webm)$", file):
        move(file,source,os.path.join(destination,"videos"))
    if re.match(".*\.(mp3)$", file):
        move(file,source,os.path.join(destination,"audios"))
    if re.match(".*\.(exe|apk|msi)$", file):
        move(file,source,os.path.join(destination,"softwares"))
    if re.match(".*\.(zip)$", file):
        move(file,source,os.path.join(destination,"zips"))
    # if re.match(".*\.(html|en|xcf|js|py|mdl|tm)$", file):
    #     move(file,source,os.path.join(destination,"others"))

    