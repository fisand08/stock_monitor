import random
import os
"""
Container backend logic
"""


def get_random_color(username):
    # Seed random number generator with hash of the username
    random.seed(hash(username))

    # Generate random RGB values
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # Format RGB values into hexadecimal color code
    color_code = "#{:02x}{:02x}{:02x}".format(r, g, b)

    return color_code


def add_stocks(abbv, current_stocks):
    """
    description:
        - adds a new stock to stock input file
    """
    fname = 'stock_input.txt'
    f = open(os.path.join(os.getcwd(), fname), 'w')
    for s in current_stocks:
        f.write(s + '\n')
    f.write(abbv)
    f.close()
    return fname
