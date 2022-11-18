import curses
from curses import wrapper
import json
from playsound import playsound as ps
import threading
from pathlib import Path
import os
import time
import multiprocessing
from PIL import Image


def wait_for_next_frame(t_start, frame: int):
    FPS = 30
    rate = 1 / FPS

    time_to_next_frame_after_start = rate * (frame + 1)
    time_elapsed = time.perf_counter() - t_start

    if time_elapsed > time_to_next_frame_after_start:
        return 'Frame {:0>6} took {} seconds too long to render.'.format(
            frame,
            time_elapsed - time_to_next_frame_after_start
        )
    if time_elapsed < time_to_next_frame_after_start:
        time.sleep(time_to_next_frame_after_start - time_elapsed)

    return


def resize(i: Image, new_w: int) -> Image:

    if new_w == i.width:
        return i

    w, h = i.size
    ratio = h / w
    h = int(new_w * ratio)
    return i.resize((new_w, h))


def grayify(i: Image) -> Image:

    return i.convert('L')


def i_to_ascii(i: Image) -> str:

    ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

    px = i.getdata()
    return ' '.join([ASCII_CHARS[pixel // 25] for pixel in px])


def get_ascii_i(p, w) -> str:

    try:
        i = Image.open(p)
    except Exception as e:
        print(f'Last frame reached.\n{e}')
        return '-1'

    if i is None:
        return '-1'

    i = grayify(
        resize(
            i, w
        )
    )

    ascii_i = i_to_ascii(i)
    l = len(ascii_i)
    ascii_i_formatted = '\n'.join(  # *2 because of the space between chars
        ascii_i[
            i*2:(i+w)*2
        ]
        for i in range(0, l, w*2)
    )

    return ascii_i_formatted


def v_thread(*args, **kwargs):
    width = args[0]
    path, stdscr = kwargs['p_f'], kwargs['stdscr']
    prefix, suffix = kwargs['prefix'], kwargs['suffix']

    i = 0
    l = []
    t_start = time.perf_counter()
    while 1:
        n = '{:0>6}'.format(i)
        p = path / f'{prefix}{n}{suffix}'

        ascii_i = get_ascii_i(p, width)
        if ascii_i == '-1':
            break

        stdscr.addstr(0, 0, ascii_i)
        stdscr.refresh()

        t = wait_for_next_frame(t_start, i)
        l.append(t) if t is not None else ...

        i += 1

    if len(l) < 1:
        return

    with open('log.txt', 'w') as f:
        f.write('\n'.join(l))
    return


def main(stdscr):
    curses.use_default_colors()

    with open('set.json', 'r') as f:
        _settings = json.load(f)

    p_f = Path(os.getcwd())
    for i in range(len(_settings['const']['p_f'])):
        p_f /= _settings['const']['p_f'][i]
    f_m = Path(os.getcwd())
    for i in range(len(_settings['const']['f_m'])):
        f_m /= _settings['const']['f_m'][i]

    audio = multiprocessing.Process(target=ps, args=(f_m,))
    threadV = threading.Thread(
        target=v_thread,
        args=(
            _settings['small']['width'],
        ),
        kwargs={
            'p_f': p_f,
            'prefix': _settings['const']['prefix'],
            'suffix': _settings['const']['suffix'],
            'stdscr': stdscr,
        }
    )

    audio.start()
    threadV.start()
    threadV.join()

    if not threadV.is_alive():
        audio.terminate()

    input('Press any key to exit... ')
    return


if __name__ == '__main__':
    wrapper(main)
