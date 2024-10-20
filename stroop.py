import pygame
import random
import time
import math
import csv
from scipy.stats import ttest_ind


# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#, pygame.FULLSCREEN)
pygame.display.set_caption('Stroop Test')

# Font settings
FONT = pygame.font.Font(None, 74)
BUTTON_FONT = pygame.font.Font(None, 50)

# Define colors
COLORS = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'ORANGE': (255, 165, 0)
}

# Define word list for testing
WORD_LIST = list(COLORS.keys())

# Log file for results
from pathlib import Path

# Determine the directory where the script (stroop.py) is located
script_dir = Path(__file__).parent

# Define paths for the log file and result figure
LOG_FILE = script_dir / 'stroop_test_results.csv'
RESULT_FIGURE = script_dir / 'result.pdf'

# Constants
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 60
LINE_SPACING = 10
RADIUS = 200

def show_instructions(text, font, color, position, line_spacing=LINE_SPACING):
    lines = text.split('\n')
    x, y = position
    for line in lines:
        text_obj = font.render(line, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        screen.blit(text_obj, text_rect)
        y += text_rect.height + line_spacing

def draw_text(text, font, color, position, incongruent=False):
    if incongruent:
        color = incongruent_color(color)
        color_name = [preset_name for preset_name, preset_color in COLORS.items() if preset_color == color][0]
    else:
        color_name = text
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=position)
    screen.blit(text_obj, text_rect)
    return color_name

def draw_button(text, position, width, height, color, text_color, show_text=True):
    button_rect = pygame.Rect(position[0] - width // 2, position[1] - height // 2, width, height)
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)
    if show_text:
        draw_text(text, BUTTON_FONT, text_color, button_rect.center)
    return button_rect

def handle_events(next_button_rect=None):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if next_button_rect and next_button_rect.collidepoint(mouse_pos):
                    return True
                return mouse_pos

def draw_buttons_around_center(options, radius=RADIUS, use_color=True, use_text=False):
    button_positions = []
    num_options = len(options)
    for i, option in enumerate(options):
        angle = (2 * math.pi / num_options) * i
        x = CENTER_POSITION[0] + int(radius * math.cos(angle))
        y = CENTER_POSITION[1] + int(radius * math.sin(angle))
        color = COLORS[option] if use_color else (200, 200, 200)
        text_color = (255, 255, 255) if use_color else (0, 0, 0)
        button_rect = draw_button(option, (x, y), BUTTON_WIDTH, BUTTON_HEIGHT, color, text_color, show_text=use_text)
        button_positions.append((option, button_rect))  # Store color as well
    return button_positions

def check_button_click(button_positions, mouse_pos):
    for option, rect in button_positions:  # Unpack color
        if rect.collidepoint(mouse_pos):
            return option  # Return both option and color
    return None


def incongruent_color(word):
    available_colors = [color for color_name, color in COLORS.items() if color_name != word]
    random_color = random.choice(available_colors)
    return random_color


def clear_center_area(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, background_color=(255, 255, 255)):
    # Calculate the area to be cleared, centered on the screen
    clear_rect = pygame.Rect(
        CENTER_POSITION[0] - width // 2,
        CENTER_POSITION[1] - height // 2,
        width,
        height
    )
    # Draw over it with the background color
    pygame.draw.rect(screen, background_color, clear_rect)

def run_trial(trials, trial_type, prompt, draw_stimulus, check_answer):
    show_instructions(prompt, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, 100))
    pygame.display.flip()
    time.sleep(2)

    results = []
    for _ in range(trials):
        word_to_be_recognized = random.choice(WORD_LIST)
        screen.fill((255, 255, 255))
        name_of_color_to_be_recognized = draw_stimulus(word_to_be_recognized)
        button_positions = draw_buttons_around_center(WORD_LIST, use_color=("First Set" in trial_type), use_text=("Second Set" in trial_type))
        pygame.display.flip()
        pygame.event.clear()
        start_time = time.time()
        response = None

        while response is None:
            mouse_pos = handle_events()
            if isinstance(mouse_pos, tuple):
                response = check_button_click(button_positions, mouse_pos)

        reaction_time = time.time() - start_time
        is_correct = check_answer(word_to_be_recognized, response)

        results.append({
            'trial_type': trial_type,
            'word_or_color': word_to_be_recognized,
            'response': response,
            'correct': is_correct,
            'reaction_time': reaction_time
        })

        # Clear the center area before drawing the "Next Trial" button
        clear_center_area(BUTTON_WIDTH*1.6, BUTTON_HEIGHT*2)

        next_button_rect = draw_button("Next Trial", CENTER_POSITION, 180, 50, (0, 0, 0), (255, 255, 255))
        pygame.display.flip()
        handle_events(next_button_rect)
    return results

def save_results(results):
    with open(LOG_FILE, 'w', newline='') as csvfile:
        fieldnames = ['trial_type', 'word_or_color', 'response', 'correct', 'reaction_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)


def calculate_summary_stats(results):
    import statistics
    # Filter results
    first_set_congruent_times = [r['reaction_time'] for r in results if r['trial_type'] == 'First Set']
    first_set_incongruent_times = [r['reaction_time'] for r in results if r['trial_type'] == 'First Set - Incongruent']
    second_set_congruent_times = [r['reaction_time'] for r in results if r['trial_type'] == 'Second Set']
    second_set_incongruent_times = [r['reaction_time'] for r in results if
                                    r['trial_type'] == 'Second Set - Incongruent']

    # Perform t-tests
    first_ttest = ttest_ind(first_set_congruent_times, first_set_incongruent_times, equal_var=False)
    second_ttest = ttest_ind(second_set_congruent_times, second_set_incongruent_times, equal_var=False)

    # Print summary
    print("Summary of Response Times:")
    print(
        f"Mean Reaction Time (First Set - Congruent): {statistics.mean(first_set_congruent_times):.3f} seconds" if first_set_congruent_times else "No data")
    print(
        f"Mean Reaction Time (First Set - Incongruent): {statistics.mean(first_set_incongruent_times):.3f} seconds" if first_set_incongruent_times else "No data")
    print(f"T-test p-value (First Set): {first_ttest.pvalue:.3f}\n")

    print(
        f"Mean Reaction Time (Second Set - Congruent): {statistics.mean(second_set_congruent_times):.3f} seconds" if second_set_congruent_times else "No data")
    print(
        f"Mean Reaction Time (Second Set - Incongruent): {statistics.mean(second_set_incongruent_times):.3f} seconds" if second_set_incongruent_times else "No data")
    print(f"T-test p-value (Second Set): {second_ttest.pvalue:.3f}\n")

    # Plot reaction times
    plot_reaction_times(first_set_congruent_times, first_set_incongruent_times, second_set_congruent_times,
                        second_set_incongruent_times)


def plot_reaction_times(first_congruent, first_incongruent, second_congruent, second_incongruent):
    import matplotlib.pyplot as plt
    labels = ['First Congruent', 'First Incongruent', 'Second Congruent', 'Second Incongruent']
    data = [
        first_congruent,
        first_incongruent,
        second_congruent,
        second_incongruent
    ]

    # Create a boxplot
    plt.boxplot(data, labels=labels, showmeans=True)
    plt.ylabel('Reaction Time (s)')
    plt.title('Reaction Time Comparison')
    plt.grid(True)
    plt.savefig(RESULT_FIGURE)


def main(trials=10):
    if 0:
        # First set of trials where the text is black (standard condition)
        first_results = run_trial(
            trials // 2 + 1,  # first trial starts slowly, discard
            "First Set",
            "Push the color written as text!",
            lambda word: draw_text(word, FONT, (0, 0, 0), CENTER_POSITION),
            lambda word, res: word == res
        )

        # Second set of trials where the text is shown in a random incongruent color
        first_incongruent_results = run_trial(
            trials // 2,
            "First Set - Incongruent",
            "Push the color written as text!",
            lambda word: draw_text(word, FONT, (0, 0, 0), CENTER_POSITION, incongruent=True),
            lambda word, res: COLORS[word] == COLORS[res]
        )

    # Second standard set of trials as originally defined
    second_results = run_trial(
        trials // 2 + 1, # discard 1 trial because task has changed
        "Second Set",
        "Push the word showing the name of the color",
        lambda color: draw_button("", CENTER_POSITION, 150, 100, COLORS[color], (0, 0, 0)),
        lambda color, res: color == res
    )

    # Incongruent trials for the second set
    second_incongruent_results = run_trial(
        trials // 2,
        "Second Set - Incongruent",
        "Push the word showing the name of the color",
        lambda word: draw_text(word, FONT, (0, 0, 0), CENTER_POSITION, incongruent=True),
        lambda word, res: COLORS[word] == COLORS[res]
    )

    # Combine all results and process
    first_results = first_results[1:]  # first trial upon app start has delays
    second_results = second_results[1:] # discard 1 trial because task has changed
    all_results = first_results + first_incongruent_results + second_results + second_incongruent_results
    calculate_summary_stats(all_results)
    save_results(all_results)
    pygame.quit()


if __name__ == '__main__':
    main(trials=10)