from PIL import Image

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]


def grayify(image: Image) -> Image:
    return image.convert("L")


# def resize_image(image: Image, width: int) -> Image:
#     w, h = image.size
#     ratio = h / w
#     height = int(width * ratio)
#     return image.resize((width, height))


def pixels_to_ascii(image: Image) -> str:
    pixels = image.getdata()
    return "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])


def main(*args, **kwargs) -> None:
    path = kwargs.get("path")
    width = kwargs.get("width")

    try:
        image = Image.open(path)
    except Exception:
        print(f"Unable to find image in {path}")
        return

    # print(f'{image.size=}')
    new_image_data = pixels_to_ascii(
        grayify(
            image
            # resize_image(image, width)
        )
    )

    pixel_count = len(new_image_data)
    # print(f'{pixel_count = }')
    ascii_image = "\n".join(new_image_data[i:(i + width)]
                            for i in range(0, pixel_count, width))

    print(ascii_image)


if __name__ == "__main__":
    main(
        path=r'C:\Users\mzoesch\Desktop\BadApple\src\frames\frame-005129.png',
        width=360
    )
