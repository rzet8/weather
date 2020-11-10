import time

def time_log():
    t = time.ctime()
    t = t.split(" ")[:-1][-1]
    t = "["+t+"]"
    return t

def log(text):
    log = open("logs.txt", "a")
    log.write(time_log()+text+"\n")
    log.close()
