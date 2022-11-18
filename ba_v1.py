import os
import sys
import json
import pygame as pg
from PIL import Image
from pathlib import Path
import pygame.locals as pl


def grayify(i: Image) -> Image:

    return i.convert('L')


def resize(i: Image, new_w: int) -> Image:

    if new_w == i.width:
        return i

    w, h = i.size
    ratio = h / w
    h = int(new_w * ratio)
    return i.resize((new_w, h))


def i_to_ascii(i: Image) -> str:

    ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

    px = i.getdata()
    return ''.join([ASCII_CHARS[pixel // 25] for pixel in px])


def get_ascii_i(p, w) -> str:

    try:
        i = Image.open(p)
    except Exception as e:
        print(f'Last frame reached.\n{e}')
        return '-1'

    if i is None:
        exit_statement(0)

    i = grayify(
        resize(
            i, w
        )
    )

    ascii_i = i_to_ascii(i)
    l = len(ascii_i)
    ascii_i_formatted = '\n'.join(
        ascii_i[
            i:(i+w)
        ]
        for i in range(0, l, w)
    )

    return ascii_i_formatted


def show(screen, f, t, line_delta) -> None:
    screen.fill((0, 0, 0))
    t = t.split('\n')

    for i in range(len(t)):
        l = f.render(t[i], True, (255, 255, 255))
        screen.blit(l, (0, i * line_delta))

    return


def exit_statement(i: int) -> None:

    def user_exit() -> None:

        def exit() -> None:
            pg.mixer.quit()
            pg.quit()
            sys.exit()

        for event in pg.event.get():
            exit() if event.type == pl.QUIT else ...
            exit() if event.type == pl.KEYDOWN and event.key == pl.K_ESCAPE else ...

    if i == -1:
        pg.mixer.quit()
        while 1:
            user_exit()
            pg.display.update()

    user_exit()


def main(*args, **kwargs) -> None:
    p_f,   f_m = kwargs['p_f'], kwargs['f_m']
    prefix, suffix = kwargs['prefix'], kwargs['suffix']
    for a in args:
        width, display, char_size, line_delta = a

    pg.init()
    pg.display.set_caption('【東方】Bad Apple!! ＰＶ【影絵】')
    screen = pg.display.set_mode(display)
    f = pg.font.SysFont('lucidaconsole', char_size)
    mC = pg.time.Clock()
    pg.mixer.music.load(f_m)
    pg.mixer.music.play()

    i = 0
    while 1:
        n = '{:0>6}'.format(i)
        p = p_f / f'{prefix}{n}{suffix}'

        ascii_i = get_ascii_i(p, width)
        exit_statement(int(ascii_i)) if ascii_i == '-1' else ...

        show(
            screen, f, ascii_i, line_delta
        )

        i += 1
        exit_statement(0)
        pg.display.update()
        mC.tick(30)

    return


if __name__ == '__main__':

    with open('set.json', 'r') as f:
        _settings = json.load(f)

    f_music = Path(os.getcwd())
    for i in range(len(_settings['const']['f_m'])):
        f_music /= _settings['const']['f_m'][i]
    p_frames = Path(os.getcwd())
    for i in range(len(_settings['const']['p_f'])):
        p_frames /= _settings['const']['p_f'][i]

    main(
        [a for a in _settings['small'].values()],
        p_f=p_frames,
        prefix=_settings['const']['prefix'],
        suffix=_settings['const']['suffix'],
        f_m=f_music,
    )
