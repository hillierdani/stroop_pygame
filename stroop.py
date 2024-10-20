import pygame
import random
import time
import csv

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
LOG_FILE = 'stroop_test_results.csv'

def show_instructions(text, font, color, position, line_spacing=10):
    """
    Displays multi-line text on the screen with the specified line spacing.

    Args:
        text (str): The instruction text containing line breaks (`\n`).
        font (pygame.font.Font): The font to use for rendering.
        color (tuple): The color of the text.
        position (tuple): The (x, y) position to start drawing the text.
        line_spacing (int): The number of pixels between each line.
    """
    lines = text.split('\n')
    x, y = position
    for line in lines:
        text_obj = font.render(line, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        screen.blit(text_obj, text_rect)
        y += text_rect.height + line_spacing  # Move down for the next line

# Function to draw text at a specific position
def draw_text(text, font, color, position):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=position)
    screen.blit(text_obj, text_rect)

# Function to draw buttons
def draw_buttons(options, y_position, use_color=True):
    button_positions = []
    button_width = 150
    button_height = 60
    x_step = SCREEN_WIDTH // (len(options) + 1)

    for i, option in enumerate(options):
        x_position = (i + 1) * x_step
        button_color = COLORS[option] if use_color else (200, 200, 200)  # Use light gray for background if no color

        # Draw the button rectangle
        button_rect = pygame.Rect(x_position - button_width // 2, y_position - button_height // 2, button_width,
                                  button_height)
        pygame.draw.rect(screen, button_color, button_rect)

        # Draw the button border
        border_color = (0, 0, 0)
        pygame.draw.rect(screen, border_color, button_rect, 2)

        # Draw the text on the button
        text_color = (255, 255, 255) if use_color else (
        0, 0, 0)  # White text for colored buttons, black for text buttons
        draw_text(option, BUTTON_FONT, text_color, button_rect.center)

        # Save button position for click detection
        button_positions.append((option, button_rect.x, button_rect.y, button_width, button_height))

    return button_positions

# Function to check if a button is clicked
def check_button_click(button_positions, mouse_pos):
    for option, x, y, width, height in button_positions:
        button_rect = pygame.Rect(x, y, width, height)
        if button_rect.collidepoint(mouse_pos):
            print(f"Button '{option}' was clicked.")
            return option
    return None


def first_set_trials(trials=5):
    # Function to run the first set of trials
    # Show instructions
    screen.fill((255, 255, 255))
    text = "Push the colored button \n showing the color written with text"
    show_instructions(text, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, 100), line_spacing=10)
    pygame.display.flip()
    pygame.time.wait(4000)

    results = []
    for _ in range(trials):
        word = random.choice(WORD_LIST)
        correct_color = COLORS[word]

        # Display the word in black
        screen.fill((255, 255, 255))
        draw_text(word, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        # Draw colored buttons
        button_positions = draw_buttons(WORD_LIST, SCREEN_HEIGHT // 2 + 100, use_color=True)
        pygame.display.flip()

        # Clear any previous events
        pygame.event.clear()

        # Start timing
        start_time = time.time()
        response = None

        # Wait for user input
        while response is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    response = check_button_click(button_positions, mouse_pos)
                    if response is not None:
                        print(f"Button '{response}' was clicked.")
                        break  # Exit the event loop if a valid response is captured

        # Stop timing
        reaction_time = time.time() - start_time
        is_correct = (response == word)

        # Log the results
        results.append({
            'trial_type': 'First Set',
            'word': word,
            'response': response,
            'correct': is_correct,
            'reaction_time': reaction_time
        })

        # Provide feedback (optional)
        #screen.fill((0, 255, 0) if is_correct else (255, 0, 0))  # Green for correct, red for incorrect
        #pygame.display.flip()

        # Clear the screen before the next trial
        screen.fill((255, 255, 255))
        pygame.display.flip()

        # Wait briefly before the next trial
        pygame.time.wait(500)

    return results

# Function to run the second set of trials
def second_set_trials(trials=5):
    # Show instructions
    screen.fill((255, 255, 255))
    text = "Push the button showing the name of\n the color of the rectangle"
    show_instructions(text, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, 100), line_spacing=10)

    pygame.display.flip()
    pygame.time.wait(4000)

    results = []
    for _ in range(trials):
        color_name = random.choice(WORD_LIST)
        color_value = COLORS[color_name]

        # Display the colored rectangle
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, color_value, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, 200, 200))

        # Draw text buttons
        button_positions = draw_buttons(WORD_LIST, SCREEN_HEIGHT // 2 + 150, use_color=False)
        pygame.display.flip()
        pygame.event.clear()

        # Start timing
        start_time = time.time()
        response = None

        # Wait for user input
        while response is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    response = check_button_click(button_positions, mouse_pos)

        # Stop timing
        reaction_time = time.time() - start_time
        is_correct = (response == color_name)

        # Log the results
        results.append({
            'trial_type': 'Second Set',
            'color': color_name,
            'response': response,
            'correct': is_correct,
            'reaction_time': reaction_time
        })

    return results

def calculate_summary_stats(results):
    import statistics
    # Separate the results by trial type
    first_set_times = [result['reaction_time'] for result in results if result['trial_type'] == 'First Set']
    second_set_times = [result['reaction_time'] for result in results if result['trial_type'] == 'Second Set']

    # Calculate the mean for each set, handling cases where no trials were completed
    first_set_mean = statistics.mean(first_set_times) if first_set_times else 0
    second_set_mean = statistics.mean(second_set_times) if second_set_times else 0

    # Print the summary statistics
    print("Summary of Response Times:")
    print(f"Mean Reaction Time (First Set): {first_set_mean:.3f} seconds")
    print(f"Mean Reaction Time (Second Set): {second_set_mean:.3f} seconds")


# Main function to run the Stroop test
def main(trials = 10):
    # Example usage: Assuming you have run the first and second sets of trials and stored the results
    all_results = first_set_trials(trials) + second_set_trials(trials)  # Example combining the results from two sets
    calculate_summary_stats(all_results)

    # Write the results to a CSV file
    with open(LOG_FILE, 'w', newline='') as csvfile:
        fieldnames = ['trial_type', 'word', 'color', 'response', 'correct', 'reaction_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in all_results:
            writer.writerow(result)

    print(f'Results saved to {LOG_FILE}')
    pygame.quit()

if __name__ == '__main__':
    main(trials=5)
