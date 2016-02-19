import multiprocessing

# If not using inside docker, this should probably be 127.0.0.1 with a nginx/apache proxy in front
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslogfile = '/dev/stdout'
errorlogfile = '/dev/stderr'
reload = True
