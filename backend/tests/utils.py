import random
import string


def random_string(k: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))
