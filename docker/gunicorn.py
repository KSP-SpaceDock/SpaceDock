import multiprocessing

# If not using inside docker, this should probably be 127.0.0.1 with a nginx/apache proxy in front
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
errorlog = '-'
reload = True
