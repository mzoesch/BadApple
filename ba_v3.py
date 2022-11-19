import cv2
import threading
from concurrent.futures import ThreadPoolExecutor


# def playV():
#     src = cv2.VideoCapture('src/BadApple.mp4')

#     while ...:
#         ret, frame = src.read()
#         cv2.imshow('frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q') or ret == False:
#             src.release()
#             cv2.destroyAllWindows()
#             break

#         cv2.imshow('frame', frame)


def main(*args, **kwargs) -> None:

    pool = ThreadPoolExecutor(max_workers=2)  # max thrads
    worker = pool.submit(playV, 10)
    worker.done()  # True or False
    worker.result()  # wait for work1 to finish


if __name__ == '__main__':
    main()
