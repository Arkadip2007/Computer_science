import PIL.Image

# ASCII ক্যারেক্টার সেট (উজ্জ্বলতা অনুযায়ী সাজানো)
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width / 1.65  # টার্মিনাল ফন্টের উচ্চতা ও প্রস্থের সামঞ্জস্য বজায় রাখতে
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

def main(image_path, new_width=100):
    try:
        image = PIL.Image.open(image_path)
    except Exception as e:
        print(f"ছবিটি ওপেন করা সম্ভব হয়নি: {e}")
        return

    # ইমেজ প্রসেসিং
    new_image_data = pixels_to_ascii(grayify(resize_image(image, new_width)))
    
    # আউটপুট ফরম্যাটিং
    pixel_count = len(new_image_data)
    ascii_image = "\n".join([new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)])
    
    # টার্মিনালে প্রিন্ট করা
    print(ascii_image)

# আপনার ছবির পাথ এখানে দিন
image_file_path = "your_image.jpg" 
main(image_file_path)
