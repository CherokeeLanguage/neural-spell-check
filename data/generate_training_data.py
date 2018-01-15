
from collections import Counter
import re
import numpy as np
from numpy.random import choice as random_choice
from numpy.random import randint as random_randint
from numpy.random import shuffle as random_shuffle
from numpy.random import rand

input_filename = '/var/data/correct_en_snt.txt'
output_filename = '/tmp/mistakes_en_snt.txt'

# Parameters for the model and dataset
MAX_INPUT_LEN = 40
MIN_INPUT_LEN = 3
AMOUNT_OF_NOISE = 0.2 / MAX_INPUT_LEN
NUMBER_OF_CHARS = 100  # 75
CHARS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .")

def add_noise_to_string(a_string, amount_of_noise):
        """Add some artificial spelling mistakes to the string"""
        if rand() < amount_of_noise * len(a_string):
            # Replace a character with a random character
            random_char_position = random_randint(len(a_string))
            a_string = a_string[:random_char_position] + random_choice(CHARS[:-1]) + a_string[random_char_position + 1:]
        if rand() < amount_of_noise * len(a_string):
            # Delete a character
            random_char_position = random_randint(len(a_string))
            a_string = a_string[:random_char_position] + a_string[random_char_position + 1:]
        if len(a_string) < MAX_INPUT_LEN and rand() < amount_of_noise * len(a_string):
            # Add a random character
            random_char_position = random_randint(len(a_string))
            a_string = a_string[:random_char_position] + random_choice(CHARS[:-1]) + a_string[random_char_position:]
        if rand() < amount_of_noise * len(a_string):
            # Transpose 2 characters
            random_char_position = random_randint(len(a_string) - 1)
            a_string = (a_string[:random_char_position] +
                        a_string[random_char_position + 1] +
                        a_string[random_char_position] +
                        a_string[random_char_position + 2:])
	return a_string

with open(input_filename, 'r') as i_f:
    with open(output_filename, 'w') as o_f:
        for correct_sentence in i_f:
            print(correct_sentence)
            wrong_sentence = add_noise_to_string(correct_sentence, 0.7)
            o_f.write(wrong_sentence)
