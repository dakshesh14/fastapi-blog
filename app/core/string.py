import random
import string


def slugify(text):
    return text.lower().replace(" ", "-")


def random_string(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
