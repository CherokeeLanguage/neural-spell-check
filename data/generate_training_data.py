
from collections import Counter
import re
import numpy as np
from numpy.random import choice as random_choice
from numpy.random import randint as random_randint
from numpy.random import shuffle as random_shuffle
from numpy.random import rand

input_filename = '/var/data/test/correct_en_sample.x.txt'
output_correct_filename = '/tmp/en.x.txt'
output_mistake_filename = '/tmp/en.y.txt'

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
        if (rand() < amount_of_noise * len(a_string)) and len(a_string) > 3:
            # Transpose 2 characters
            random_char_position = random_randint(len(a_string) - 1)
            a_string = (a_string[:random_char_position] +
                        a_string[random_char_position + 1] +
                        a_string[random_char_position] +
                        a_string[random_char_position + 2:])
	return a_string

with open(input_filename, 'r') as i_f:
    with open(output_mistake_filename, 'w') as o_f:
        with open(output_correct_filename, 'w') as o_c_f:
            for correct_sentence in i_f:
                correct_sentence = correct_sentence[:-1]
                # print(correct_sentence)
                wrong_sentence = add_noise_to_string(correct_sentence, 0.7)
                # print(wrong_sentence)
                o_c_f.write(correct_sentence + '\n')
                o_f.write(wrong_sentence + '\n')
