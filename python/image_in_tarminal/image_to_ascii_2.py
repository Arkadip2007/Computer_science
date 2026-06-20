from PIL import Image
import sys

# বেশি ডিটেইল পাওয়ার জন্য বড় charset
#ASCII_CHARS = "@#S%?*+;:,.' "
#ASCII_CHARS = "█■"
ASCII_CHARS = "■"
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width / 1.65  # terminal aspect ratio correction
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def map_pixels_to_ascii(image, color=True):
    pixels = image.load()
    width, height = image.size
    
    ascii_image = ""

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]

            # brightness calculation (perceived luminance formula)
            brightness = int(0.299*r + 0.587*g + 0.114*b)

            # ASCII mapping
            char = ASCII_CHARS[brightness * (len(ASCII_CHARS)-1) // 255]

            if color:
                # ANSI 24-bit color
                ascii_image += f"\033[38;2;{r};{g};{b}m{char}"
            else:
                ascii_image += char

        ascii_image += "\033[0m\n"  # reset color after each line

    return ascii_image

def main(image_path, width=100, color=True):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print("ছবি ওপেন করা যায়নি:", e)
        return

    image = resize_image(image, width)
    image = image.convert("RGB")

    ascii_art = map_pixels_to_ascii(image, color=color)
    print(ascii_art)


# এখানে আপনার ছবির পাথ দিন
if __name__ == "__main__":
    image_path = "your_image.jpg"
    main(image_path, width=120, color=True)

