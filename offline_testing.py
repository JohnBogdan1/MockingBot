import emoji

print(emoji.emojize('Python is :thumbs_up:'))
print(emoji.demojize('hello 😇'))
print(emoji.demojize('hello 😈'))

import threading


def func():
    print("Hello")


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


set_interval(func, 5)
