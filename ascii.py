from blessed import Terminal
import random
import string
import json
import time

# Initialize the blessed Terminal
term = Terminal()

# Constants
GRID_SIZE = 8
PLAYER_SPRITE = '@'
BOULDER_SPRITE = '#'
PLAYER_COLOR = term.red
BOULDER_COLOR = term.brown
MOVE_DELAY = 0.05  # Delay in seconds for smooth movement

# Load puzzle word lists
with open('word_puzzles.json', 'r') as file:
    word_puzzles = json.load(file)

with open('words_dictionary.json', 'r') as file:
    large_word_list = json.load(file)
large_word_list = set(large_word_list.keys())

def generate_random_grid():
    grid = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    player_start = (GRID_SIZE - 1, GRID_SIZE // 2)
    grid[player_start[0]][player_start[1]] = 'P'

    vowels = 'AEIOU'
    consonants = ''.join(set(string.ascii_uppercase) - set(vowels))

    letter_pool = random.sample(vowels, 5) + random.choices(consonants, k=11)
    
    # Ensure that if there's a 'Q', there's also a 'U'
    if 'Q' in letter_pool and 'U' not in letter_pool:
        letter_pool[random.randint(5, 15)] = 'U'

    random.shuffle(letter_pool)

    for letter in letter_pool:
        placed = False
        while not placed:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if grid[x][y] == '.':
                grid[x][y] = letter
                placed = True
    return grid, player_start

def draw_grid(grid, puzzle_description, player_position):
    print(term.home + term.clear)
    print(term.move_xy(term.width // 2 - len(puzzle_description) // 2, 1) + puzzle_description)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if (y, x) == player_position:
                print(term.move_xy(x * 2, y + 2) + PLAYER_COLOR(PLAYER_SPRITE))
            elif grid[y][x] != '.':
                print(term.move_xy(x * 2, y + 2) + BOULDER_COLOR(BOULDER_SPRITE) + term.white(grid[y][x]))
            else:
                print(term.move_xy(x * 2, y + 2) + '  ')
    print(term.move_xy(0, GRID_SIZE + 3))

def move_player(grid, position, direction):
    x, y = position
    dx, dy = 0, 0
    if direction == 'W': dx = -1
    elif direction == 'S': dx = 1
    elif direction == 'A': dy = -1
    elif direction == 'D': dy = 1

    new_x, new_y = x + dx, y + dy
    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
        if grid[new_x][new_y] != '.' and grid[new_x][new_y] != 'P':  # Can push a letter
            next_x, next_y = new_x + dx, new_y + dy
            if 0 <= next_x < GRID_SIZE and 0 <= next_y < GRID_SIZE and grid[next_x][next_y] == '.':
                grid[next_x][next_y] = grid[new_x][new_y]
                grid[new_x][new_y] = 'P'
                grid[x][y] = '.'
                return new_x, new_y
        elif grid[new_x][new_y] == '.':
            grid[x][y], grid[new_x][new_y] = '.', 'P'
            return new_x, new_y
    return x, y

def check_word_condition(word, condition):
    vowels = set('aeiou')
    if condition == "one_vowel":
        return sum(1 for char in word if char in vowels) == 1
    if condition == "length_six":
        return len(word) == 6
    if condition == "no_a_e":
        return 'a' not in word and 'e' not in word
    if condition == "start_t":
        return word.startswith('t')
    if condition == "end_n":
        return word.endswith('n')
    if condition == "two_vowels":
        return sum(1 for char in word if char in vowels) == 2
    if condition == "contains_z":
        return 'z' in word
    if condition == "palindrome":
        return word == word[::-1]
    if condition == "alternating_vc":
        return all((char in vowels) != (word[i - 1] in vowels) for i, char in enumerate(word[1:], 1))
    if condition == "all_consonants":
        return all(char not in vowels for char in word)
    if condition == "three_syllables":
        return sum(1 for char in word if char in vowels) >= 3
    if condition == "double_letters":
        return any(word[i] == word[i + 1] for i in range(len(word) - 1))
    if condition == "one_consonant":
        return sum(1 for char in word if char not in vowels) == 1
    if condition == "length_four":
        return len(word) == 4
    if condition == "contains_q":
        return 'q' in word
    if condition == "same_first_last":
        return word[0] == word[-1]
    return False

def check_for_words_and_update_grid(grid, puzzle_condition):
    # Check horizontally and vertically for words
    for y in range(GRID_SIZE):
        for start in range(GRID_SIZE):
            for end in range(start+1, GRID_SIZE+1):
                horizontal_word = ''.join(grid[y][start:end]).replace('.', '')
                vertical_word = ''.join([grid[x][y] for x in range(start, end)]).replace('.', '')
                if (horizontal_word in large_word_list and check_word_condition(horizontal_word, puzzle_condition)) or \
                   (vertical_word in large_word_list and check_word_condition(vertical_word, puzzle_condition)):
                    for x in range(start, end):
                        if horizontal_word in large_word_list and check_word_condition(horizontal_word, puzzle_condition):
                            grid[y][x] = '.'  # Clear the row
                        if vertical_word in large_word_list and check_word_condition(vertical_word, puzzle_condition):
                            grid[x][y] = '.'  # Clear the column
                    return True
    return False

def show_popup(message):
    print(term.home + term.clear)
    print(term.move_xy(term.width // 2 - len(message) // 2, term.height // 2) + message)
    term.inkey()

def select_random_puzzle():
    puzzle_key = random.choice(list(word_puzzles.keys()))
    puzzle_data = word_puzzles[puzzle_key]
    return puzzle_data['description'], puzzle_data['condition']

def main():
    grid, player_position = generate_random_grid()
    current_puzzle_description, current_puzzle_condition = select_random_puzzle()
    draw_grid(grid, current_puzzle_description, player_position)

    while True:
        key = term.inkey()
        if key in ('q', 'Q'):
            break
        elif key in ('w', 'a', 's', 'd'):
            direction = None
            if key == 'w':
                direction = 'W'
            elif key == 's':
                direction = 'S'
            elif key == 'a':
                direction = 'A'
            elif key == 'd':
                direction = 'D'
            
            if direction:
                old_position = player_position
                player_position = move_player(grid, player_position, direction)
                draw_grid(grid, current_puzzle_description, old_position)
                time.sleep(MOVE_DELAY)
                draw_grid(grid, current_puzzle_description, player_position)
                if check_for_words_and_update_grid(grid, current_puzzle_condition):
                    current_puzzle_description = "CHAMBER CLEAR, PRESS ENTER TO CONTINUE"
                    draw_grid(grid, current_puzzle_description, player_position)

if __name__ == "__main__":
    with term.cbreak(), term.hidden_cursor():
        main()

