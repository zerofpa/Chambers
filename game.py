import pygame
import random
import string
import json

# Initialize Pygame
pygame.init()

# Constants
SCREEN_SIZE = 800
GRID_SIZE = 10
CELL_SIZE = SCREEN_SIZE // GRID_SIZE
HEADER_HEIGHT = 50
FONT_SIZE = 40
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load puzzle word lists
with open('word_puzzles.json', 'r') as file:
    word_puzzles = json.load(file)

with open('words_dictionary.json', 'r') as file:
    large_word_list = json.load(file)
large_word_list = set(large_word_list.keys())

# Define the screen and font
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + HEADER_HEIGHT))
font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
puzzle_font = pygame.font.Font('freesansbold.ttf', 24)

def generate_random_grid():
    grid = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    player_start = (GRID_SIZE // 2, GRID_SIZE // 2)
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

def draw_grid(grid, puzzle_description, fade_alpha):
    screen.fill(BLACK)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell_x = x * CELL_SIZE
            cell_y = y * CELL_SIZE + HEADER_HEIGHT
            letter = grid[y][x]
            if letter == 'P':
                pygame.draw.circle(screen, RED, (cell_x + CELL_SIZE//2, cell_y + CELL_SIZE//2), CELL_SIZE//4)
            elif letter != '.':
                text = font.render(letter, True, WHITE)
                screen.blit(text, (cell_x + (CELL_SIZE - text.get_width()) // 2, cell_y + (CELL_SIZE - text.get_height()) // 2))
    
    # Display puzzle description with fade-in effect
    if fade_alpha < 255:
        fade_alpha += 5
    puzzle_surface = puzzle_font.render(puzzle_description, True, WHITE)
    puzzle_surface.set_alpha(fade_alpha)
    screen.blit(puzzle_surface, (SCREEN_SIZE // 2 - puzzle_surface.get_width() // 2, 10))
    
    pygame.display.flip()
    return fade_alpha

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
    screen.fill(BLACK)
    popup_font = pygame.font.Font('freesansbold.ttf', 24)
    text_surface = popup_font.render(message, True, WHITE)
    text_rect = text_surface.get_rect(center=(SCREEN_SIZE / 2, (SCREEN_SIZE + HEADER_HEIGHT) / 2))
    pygame.draw.rect(screen, BLACK, text_rect.inflate(20, 20))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def select_random_puzzle():
    puzzle_key = random.choice(list(word_puzzles.keys()))
    puzzle_data = word_puzzles[puzzle_key]
    return puzzle_data['description'], puzzle_data['condition']

def main():
    running = True
    grid, player_position = generate_random_grid()
    level_completed = False
    teleportations_remaining = 3
    chambers_cleared = 0
    fade_alpha = 0
    current_puzzle_description, current_puzzle_condition = select_random_puzzle()

    while running:
        fade_alpha = draw_grid(grid, current_puzzle_description, fade_alpha)
        if not level_completed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.unicode.upper() in 'WASD':
                        player_position = move_player(grid, player_position, event.unicode.upper())
                        if check_for_words_and_update_grid(grid, current_puzzle_condition):
                            current_puzzle_description = "CHAMBER CLEAR, PRESS ENTER TO CONTINUE"
                            level_completed = True
                elif event.type == pygame.MOUSEBUTTONDOWN and teleportations_remaining > 0:
                    if event.button == 1:  # Left click
                        mx, my = pygame.mouse.get_pos()
                        mx = (mx - 50) // CELL_SIZE
                        my = (my - HEADER_HEIGHT) // CELL_SIZE
                        if 0 <= mx < GRID_SIZE and 0 <= my < GRID_SIZE and grid[my][mx] != 'P':
                            grid[player_position[0]][player_position[1]], grid[my][mx] = grid[my][mx], 'P'
                            player_position = (my, mx)
                            teleportations_remaining -= 1
        else:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    chambers_cleared += 1
                    if chambers_cleared < 16:
                        grid, player_position = generate_random_grid()
                        level_completed = False
                        teleportations_remaining = 3
                        fade_alpha = 0
                        current_puzzle_description, current_puzzle_condition = select_random_puzzle()
                    else:
                        show_popup("CONGRATULATIONS, YOU WIN!")
                        pygame.time.wait(3000)
                        running = False

    pygame.quit()

if __name__ == "__main__":
    main()

