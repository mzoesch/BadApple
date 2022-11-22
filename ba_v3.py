import json
import os
import cv2
from concurrent.futures import ThreadPoolExecutor
import time
from PIL import Image
import curses
from pathlib import Path
import multiprocessing
import threading
from curses import wrapper
from playsound import playsound as ps

global l


class Log():

    def __init__(self, path) -> None:
        self.path = path
        self.time = time.perf_counter()

    def write(self, obj: object) -> None:
        with open(self.path, 'a') as f:
            f.write(
                f'{time.perf_counter() - self.time:.4f}s in : {obj.__str__()}\r'
            )

    def clear(self) -> None:
        with open(self.path, 'w') as f:
            f.write('')


class Frame():

    ASCII_CHARS = ['.', ',', ':', ';', '+', '*', '?', '%', 'S', '#', '@']

    def __init__(self, index: int, img: Image, width: int) -> None:
        self.index: int = index
        self.img: Image = img
        self.width = width
        self.i_ascii = None

    def pre_render(self) -> None:
        self.img = self.resize(self.img, self.width)
        self.img = self.img.convert('L')
        px = self.img.getdata()
        i_ascii = ' '.join(
            [self.ASCII_CHARS[pixel // 25] for pixel in px]
        )

        length = len(i_ascii)
        self.i_ascii = '\n'.join(  # *2 because of the space between chars
            i_ascii[
                i*2:(i+self.width)*2
            ]
            for i in range(0, length, self.width*2)
        )

        return

    def __str__(self) -> str:
        return self.i_ascii

    @staticmethod
    def resize(i: Image, new_w: int) -> Image:

        if new_w == i.width:
            return i

        w, h = i.size
        ratio = h / w
        h = int(new_w * ratio)
        return i.resize((new_w, h))


def add_worker(pool: ThreadPoolExecutor, workers: list, width: int, **kwargs) -> None:

    i = 0
    f_v, event = kwargs['f_v'], kwargs['event']
    src = cv2.VideoCapture(f_v.__str__())

    while ...:

        if event.is_set():
            l.write('Event set. CreateThread is breaking . . . ')
            break

        _, img = src.read()

        try:
            frame = Frame(
                i, Image.fromarray(img), width
            )

        except Exception as e:
            break

        worker = pool.submit(frame.pre_render)
        workers.append((i, worker, frame))
        i += 1

    l.write('Stopped adding workers to the pool at frame: {:0>6}.'.format(i))
    return


def receive_workers(workers: list, audio_process: multiprocessing.Process, stdscr) -> None:

    def wait_for_next_frame(start, frame) -> None:
        FPS = 30
        rate = 1 / FPS

        time_to_next_frame = rate * (frame + 1)
        time_elapsed = time.perf_counter() - start

        if time_elapsed > time_to_next_frame:
            l.write('Frame {:0>6} took {:.4f}s too long to render.'.
                    format(frame, time_elapsed - time_to_next_frame)
                    )
            return

        time.sleep(time_to_next_frame - time_elapsed)
        return

    audio_process.start()
    l.write('Audio process started.')
    time.sleep(0.75)  # Estimated time for audio process to start in s

    pref_time = time.perf_counter()
    while ...:

        if len(workers) <= 0:
            l.write('No workers found. ReceiveThread waiting . . . ')
        while len(workers) <= 0:
            continue

        i, worker, frame = workers[0]
        if i == -1:
            workers.pop(0)
            l.write('Received throw worker. ReceiveThread breaking . . . ')
            break
        worker.result()

        try:
            stdscr.addstr(0, 0, frame.__str__())
            stdscr.refresh()
        except curses.error:
            l.write('Curses error. ReceiveThread breaking . . . ')
            break

        wait_for_next_frame(pref_time, i)
        workers.pop(0)


def main(stdscr) -> None:

    global l
    l = Log('log.txt')
    l.clear()

    MAX_WORKERS = 15
    curses.use_default_colors()

    with open('set.json', 'r') as f:
        _settings = json.load(f)
    cwd = Path(os.getcwd())
    f_v = cwd
    for i in range(len(_settings['const']['f_v'])):
        f_v /= _settings['const']['f_v'][i]

    event = threading.Event()
    pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    workers = []  # (i, worker, frame)
    audio_process = multiprocessing.Process(target=ps, args=(f_v,))
    thread_create = threading.Thread(
        target=add_worker,
        args=(
            pool,
            workers,
            _settings['small']['width'],
        ),
        kwargs={
            'f_v': f_v,
            'event': event,
        },
    )
    thread_receive = threading.Thread(
        target=receive_workers,
        args=(
            workers,
            audio_process,
            stdscr,
        )
    )

    thread_create.start()
    l.write('CreateThread started.')
    thread_receive.start()
    l.write('ReceiveThread started.')

    time.sleep(2)  # Check if ReceiveThread throws
    if not thread_receive.is_alive() and thread_create.is_alive():
        l.write('Other threads are still alive. Terminating . . . ')
        if audio_process.is_alive():
            audio_process.terminate()
            l.write('Audio process terminated.')
        event.set()
        thread_create.join()  # Wait for next iteration
        workers = []
        pool.shutdown(wait=False)
        l.write('Pool shutdown (forced).')
        l.write('App failed successfully.')
        return

    thread_create.join()
    workers.append((-1, None, None))
    l.write('Added throw worker.')
    pool.shutdown(wait=True)
    l.write('Pool shutdown (soft).')

    # Wait for v to throw
    thread_receive.join()
    if not thread_receive.is_alive() and audio_process.is_alive():
        audio_process.terminate()
        l.write('Audio process terminated.')

    l.write('Exit with code 0.')
    # input('Press any key to exit . . . ')
    return


if __name__ == '__main__':
    wrapper(main)
