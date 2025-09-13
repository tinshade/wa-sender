import os

from threading import Thread
from playsound import playsound

def play(path):
    """
    Play sound file in a separate thread
    (don't block current thread)
    """
    print(path)
    def play_thread_function():
        playsound("success.mp3")

    play_thread = Thread(target=play_thread_function)
    play_thread.start()


play(os.path.join(os.getcwd(),'sounds', 'success.mp3'))
# play('failure')