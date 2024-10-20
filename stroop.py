import pygame
import random
import time
import math
import csv
import statistics
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import ttest_ind

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 1024
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Stroop Test')

# Font settings
FONT = pygame.font.Font(None, 74)
BUTTON_FONT = pygame.font.Font(None, 50)

# Define colors
language = 1 # English: 0, Hungarian:1

color_name_lang = [['RED','PIROS'],['GREEN','ZÖLD'],['BLUE','KÉK'], ['YELLOW','SÁRGA'],
                   ['PURPLE','BORDÓ'],['ORANGE','NARANCS']]

COLORS = {
    color_name_lang[0][language]: (255, 0, 0), # RED
    color_name_lang[1][language]: (0, 255, 0), # 'GREEN'
    color_name_lang[2][language]: (0, 0, 255), # 'BLUE'
    color_name_lang[3][language]: (255, 255, 0), #'YELLOW'
    color_name_lang[4][language]: (128, 0, 128), # 'PURPLE'
    color_name_lang[5][language]: (255, 165, 0) #'ORANGE'
}

# Define word list for testing
WORD_LIST = list(COLORS.keys())

# Log file for results
script_dir = Path(__file__).parent
LOG_FILE = script_dir / 'stroop_test_results.csv'
RESULT_FIGURE = script_dir / 'result.pdf'

# Constants
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 60
LINE_SPACING, RADIUS = 10, 200

import datetime


def get_user_name():
    # Simple function to get the user's name using Pygame's text input capability
    input_active = True
    user_name = ""
    instruction_text = "Please enter your name: "
    font = pygame.font.Font(None, 50)
    clock = pygame.time.Clock()
    while input_active:
        screen.fill((255, 255, 255))
        show_instructions(instruction_text + user_name, font, (0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), wait_next=False)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to submit the name
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  # Backspace to delete last character
                    user_name = user_name[:-1]
                else:
                    user_name += event.unicode  # Add the character to the name
        clock.tick(30)
    return user_name.strip()


def generate_file_names(user_name):
    # Get the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    # Generate log file and result figure paths
    log_file = script_dir / f"{user_name} {current_time}_stroop_test_results.csv"
    result_figure = script_dir / f"{user_name} {current_time}_result.pdf"
    return log_file, result_figure


def show_instructions(text, font, color, position, line_spacing=LINE_SPACING, wait_next=True):
    screen.fill((255, 255, 255))
    x, y = position
    for line in text.split('\n'):
        text_obj = font.render(line, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        screen.blit(text_obj, text_rect)
        y += text_rect.height + line_spacing
    pygame.display.flip()
    if wait_next:
        next_trial()


def draw_text(text, font, color, position, incongruent=False):
    if incongruent:
        color = random.choice([c for name, c in COLORS.items() if name != text])
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=position)
    screen.blit(text_obj, text_rect)
    if incongruent:  # return the name of the color generated randomly, not the one written on screen
        text = [preset_color_name for preset_color_name, preset_color_code in COLORS.items() if color == preset_color_code][0]
    return text

def draw_button(text, position, width, height, color, text_color, show_text=True):
    button_rect = pygame.Rect(position[0] - width // 2, position[1] - height // 2, width, height)
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
    if show_text:
        draw_text(text, BUTTON_FONT, text_color, button_rect.center)
    return button_rect

def handle_events(next_button_rect=None):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if next_button_rect and next_button_rect.collidepoint(mouse_pos):
                return True
            return mouse_pos
    return None


def draw_buttons_around_center(options, use_color=True, use_text=False):
    button_positions = []

    # Hard-coded positions around a circle (assuming CENTER_POSITION is the center of the screen)
    hard_coded_positions = [
        (CENTER_POSITION[0] + 200, CENTER_POSITION[1]),  # Right
        (CENTER_POSITION[0] + 100, CENTER_POSITION[1] - 103),  # Top-right
        (CENTER_POSITION[0] - 100, CENTER_POSITION[1] - 103),  # Top-left
        (CENTER_POSITION[0] - 200, CENTER_POSITION[1]),  # Left
        (CENTER_POSITION[0] - 100, CENTER_POSITION[1] + 103),  # Bottom-left
        (CENTER_POSITION[0] + 100, CENTER_POSITION[1] + 103)  # Bottom-right
    ]

    for i, option in enumerate(options):
        # Use the hard-coded positions for button centers
        x, y = hard_coded_positions[i]

        color = COLORS[option] if use_color else (200, 200, 200)
        text_color = (255, 255, 255) if use_color else (0, 0, 0)

        # Draw the button and add to the list
        button_rect = draw_button(option, (x, y), BUTTON_WIDTH, BUTTON_HEIGHT, color, text_color, show_text=use_text)
        button_positions.append((option, button_rect))

    return button_positions

def check_button_click(button_positions, mouse_pos):
    return next((option for option, rect in button_positions if rect.collidepoint(mouse_pos)), None)

def clear_center_area(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, background_color=(255, 255, 255)):
    clear_rect = pygame.Rect(CENTER_POSITION[0] - width // 2, CENTER_POSITION[1] - height // 2, width, height)
    pygame.draw.rect(screen, background_color, clear_rect)

def next_trial():
    # Draw the "?" button in the center before allowing the next trial
    clear_center_area(BUTTON_WIDTH * 1.63, BUTTON_HEIGHT * 2)
    question_button_rect = draw_button("?", CENTER_POSITION, 150, 60, (0, 0, 0), (255, 255, 255))
    pygame.display.flip()

    # Wait for the user to click the "?" button before proceeding
    while True:
        mouse_pos = handle_events()
        if isinstance(mouse_pos, tuple) and question_button_rect.collidepoint(mouse_pos):
            break


def run_trial(trials, trial_type, prompt, draw_stimulus, check_answer):
    show_instructions(prompt, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, 100))
    pygame.display.flip()
    time.sleep(2)

    results = []
    trial_count = 0  # Track the number of actual trials

    while trial_count < trials:
        word_to_be_recognized = random.choice(WORD_LIST)
        screen.fill((255, 255, 255))
        name_of_color_to_be_recognized = draw_stimulus(word_to_be_recognized)
        button_positions = draw_buttons_around_center(WORD_LIST, use_color=("First Set" in trial_type), use_text=("Second Set" in trial_type))
        pygame.display.flip()
        start_time = time.time()
        response = None

        while response is None:
            mouse_pos = handle_events()
            if isinstance(mouse_pos, tuple):
                response = check_button_click(button_positions, mouse_pos)

        reaction_time = time.time() - start_time
        # Check if the response is correct, accounting for trial type
        if "Incongruent" in trial_type:
            is_correct = check_answer(name_of_color_to_be_recognized, response)
        else:
            is_correct = check_answer(word_to_be_recognized, response)
        results.append({'trial_type': trial_type, 'word_or_color': word_to_be_recognized, 'response': response, 'correct': is_correct, 'reaction_time': reaction_time})

        # If the answer was incorrect, increment trials to give an extra chance
        if not is_correct:
            trials += 1

        if trial_count < trials:
            next_trial()
        # Increment the trial count only after handling events
        trial_count += 1
    return results

def save_results(results, LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['trial_type', 'word_or_color', 'response', 'correct', 'reaction_time'])
        writer.writeheader()
        writer.writerows(results)

def calculate_summary_stats(results, figure_file_name):
    first_congruent = [r['reaction_time'] for r in results if r['trial_type'] == 'First Set' and r['correct']==True]
    first_incongruent = [r['reaction_time'] for r in results if r['trial_type'] == 'First Set - Incongruent' and r['correct']==True]
    second_congruent = [r['reaction_time'] for r in results if r['trial_type'] == 'Second Set' and r['correct']==True]
    second_incongruent = [r['reaction_time'] for r in results if r['trial_type'] == 'Second Set - Incongruent' and r['correct']==True]

    first_ttest = ttest_ind(first_congruent, first_incongruent, equal_var=False)
    second_ttest = ttest_ind(second_congruent, second_incongruent, equal_var=False)

    print(f"First Set Congruent Mean: {statistics.mean(first_congruent):.3f}" if first_congruent else "No data")
    print(f"First Set Incongruent Mean: {statistics.mean(first_incongruent):.3f}" if first_incongruent else "No data")
    print(f"First Set T-test p-value: {first_ttest.pvalue:.3f}")

    print(f"Second Set Congruent Mean: {statistics.mean(second_congruent):.3f}" if second_congruent else "No data")
    print(f"Second Set Incongruent Mean: {statistics.mean(second_incongruent):.3f}" if second_incongruent else "No data")
    print(f"Second Set T-test p-value: {second_ttest.pvalue:.3f}")

    plot_reaction_times(first_congruent, first_incongruent, second_congruent, second_incongruent, figure_file_name)

def plot_reaction_times(first_congruent, first_incongruent, second_congruent, second_incongruent, file_name):
    plt.boxplot([first_congruent, first_incongruent, second_congruent, second_incongruent],
                labels=['First Congruent', 'First Incongruent', 'Second Congruent', 'Second Incongruent'], showmeans=True)
    plt.ylabel('Reaction Time (s)')
    plt.title('Reaction Time Comparison')
    plt.grid(True)
    plt.savefig(file_name)

def main(trials=10):
    instruction1 = ["Click on the color written as text!",
                    'Kattints arra a színre, \n amit a középen írt szó jelent.\n Kattints a ?-re']
    first_results = run_trial(trials // 2 + 1, "First Set", instruction1[language],
                              lambda word: draw_text(word, FONT, (0, 0, 0), CENTER_POSITION),
                              lambda word, res: word == res)
    instruction2 = ["Click on the word that corresponds to the color of the word in the middle.",
                    'Kattints arra a szóra, \n amilyen a középen írt szó színe! \n Kattints a ?-re']
    first_incongruent_results = run_trial(trials // 2, "First Set - Incongruent", instruction2[language],
                                          lambda word: draw_text(word, FONT, (0, 0, 0), CENTER_POSITION, incongruent=True),
                                          lambda word, res: COLORS[word] == COLORS[res])

    instruction3 = ["Click on the word that corresponds to the color in the middle.",
                    "Kattints arra a szóra, \n amilyen színt látsz középen! \n Kattints a ?-re"]
    second_results = run_trial(trials // 2 + 1, "Second Set", instruction3[language],
                               lambda color: draw_button("", CENTER_POSITION, BUTTON_WIDTH, BUTTON_HEIGHT, COLORS[color], (0, 0, 0)),
                               lambda color, res: color == res)

    instruction4 = ["Click on the word that corresponds to the color of the word in the middle.",
                    "Kattints arra a szóra, \n amilyen a középen írt szó színe!\n Kattints a ?-re"]
    second_incongruent_results = run_trial(trials // 2, "Second Set - Incongruent", instruction4[language],
                                           lambda word: draw_text(word, FONT, (0, 0, 0), CENTER_POSITION, incongruent=True),
                                           lambda word, res: COLORS[word] == COLORS[res])

    first_results = first_results[1:]
    second_results = second_results[1:]
    all_results = first_results + first_incongruent_results + second_results + second_incongruent_results

    user_name = get_user_name()  # Get the user's name
    log_file, result_figure = generate_file_names(user_name)

    calculate_summary_stats(all_results, result_figure)
    save_results(all_results, log_file)
    pygame.quit()

if __name__ == '__main__':
    main(trials=10)
