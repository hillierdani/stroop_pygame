import pygame
import random
import time
import math
import csv

# Initialize pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
center_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
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


def draw_next_trial_button():
    """
    Draws a "Next Trial" button in the center of the screen.

    Returns:
        tuple: The (x, y, width, height) of the button for click detection.
    """
    button_width = 100
    button_height = 50

    # Create a rectangle for the white background button
    padding = 20
    white_button_rect = pygame.Rect(center_position[0] - button_width // 2 - padding // 2,
                                    center_position[1] - button_height // 2,  # Adjust Y position for padding
                                    button_width + padding,
                                    button_height)

    # Draw the white button rectangle
    pygame.draw.rect(screen, (255, 255, 255), white_button_rect)

    # Define the button rectangle
    button_rect = pygame.Rect(center_position[0] - button_width // 2, center_position[1] - button_height // 2, button_width, button_height)

    # Draw the button
    button_color = (0,0,0)  # black
    pygame.draw.rect(screen, button_color, button_rect)

    # Draw the button border
    border_color = (0, 0, 0)
    pygame.draw.rect(screen, border_color, button_rect, 2)

    # Draw the text on the button
    draw_text("Next Trial", BUTTON_FONT, (255, 255, 255), button_rect.center)

    return (button_rect.x, button_rect.y, button_width, button_height)


def wait_for_next_trial_click(next_button_position):
    """
    Waits for the user to click the "Next Trial" button.

    Args:
        next_button_position (tuple): The (x, y, width, height) of the "Next Trial" button.
    """
    next_button_rect = pygame.Rect(*next_button_position)

    # Wait for user to click the "Next Trial" button
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if next_button_rect.collidepoint(mouse_pos):
                    print("Next Trial button clicked.")
                    return

def draw_buttons_around_center(options, center_position, radius, use_color=True, use_text=False):
    """
    Draws buttons equidistantly around a center point in a circular arrangement.

    Args:
        options (list): List of color names or button labels.
        center_position (tuple): The (x, y) position of the center.
        radius (int): The radius of the circle on which to place the buttons.
        use_color (bool): Whether to use colors for the button background.

    Returns:
        list: List of tuples representing button positions for click detection.
    """
    button_positions = []
    button_width = 150
    button_height = 60
    num_options = len(options)
    center_x, center_y = center_position

    for i, option in enumerate(options):
        # Calculate angle for the current button position
        angle = (2 * math.pi / num_options) * i
        # Calculate button position based on the angle
        x_position = center_x + int(radius * math.cos(angle)) - button_width // 2
        y_position = center_y + int(radius * math.sin(angle)) - button_height // 2

        # Determine button color
        button_color = COLORS[option] if use_color else (200, 200, 200)

        # Draw the button rectangle
        button_rect = pygame.Rect(x_position, y_position, button_width, button_height)
        pygame.draw.rect(screen, button_color, button_rect)

        # Draw the button border
        border_color = (0, 0, 0)
        pygame.draw.rect(screen, border_color, button_rect, 2)

        # Draw the text on the button
        if use_text:
            text_color = (255, 255, 255) if use_color else (0, 0, 0)
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
    # Show instructions
    screen.fill((255, 255, 255))
    text = "Push the color written as text!"
    show_instructions(text, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, 100), line_spacing=10)
    pygame.display.flip()
    pygame.time.wait(4000)

    results = []
    for _ in range(trials):
        word = random.choice(WORD_LIST)
        correct_color = COLORS[word]

        # Display the word in black
        screen.fill((255, 255, 255))
        draw_text(word, FONT, (0, 0, 0), center_position)

        # Draw buttons around the word
        button_positions = draw_buttons_around_center(
            WORD_LIST,
            center_position,
            radius=200,
            use_color=True
        )
        pygame.display.flip()

        # Clear events and capture response as before...
        pygame.event.clear()
        start_time = time.time()
        response = None

        while response is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    response = check_button_click(button_positions, mouse_pos)

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

        # Display "Next Trial" button and wait for user to click it
        next_button_position = draw_next_trial_button()
        pygame.display.flip()

        # Wait for the "Next Trial" button click
        wait_for_next_trial_click(next_button_position)

    return results

# Function to run the second set of trials
def draw_colored_rectangle(color):
    """
    Draws a colored rectangle in the center of the screen.

    Args:
        color (tuple): The RGB color value for the rectangle.
    """
    rect_width = 150
    rect_height = 100
    center_x = SCREEN_WIDTH // 2 - rect_width // 2
    center_y = SCREEN_HEIGHT // 2 - rect_height // 2

    # Draw the colored rectangle
    pygame.draw.rect(screen, color, (center_x, center_y, rect_width, rect_height))


def second_set_trials(trials=5):
    # Show instructions
    screen.fill((255, 255, 255))
    text = "Push the word \n showing the name of the color"
    show_instructions(text, FONT, (0, 0, 0), (SCREEN_WIDTH // 2, 100), line_spacing=10)
    pygame.display.flip()
    pygame.time.wait(4000)

    results = []
    for _ in range(trials):
        # Randomly select a color for the rectangle
        color_name = random.choice(WORD_LIST)
        color_value = COLORS[color_name]

        # Display the colored rectangle
        screen.fill((255, 255, 255))
        draw_colored_rectangle(color_value)

        # Draw buttons around the colored rectangle
        button_positions = draw_buttons_around_center(
            WORD_LIST,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            radius=200,
            use_color=False,
            use_text = True# Use black text for button labels
        )
        pygame.display.flip()

        # Clear events and capture response
        pygame.event.clear()
        start_time = time.time()
        response = None

        while response is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
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
            'color_name': color_name,
            'response': response,
            'correct': is_correct,
            'reaction_time': reaction_time
        })

        # Display "Next Trial" button and wait for user to click it
        next_button_position = draw_next_trial_button()
        pygame.display.flip()

        # Wait for the "Next Trial" button click
        wait_for_next_trial_click(next_button_position)

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
def main(trials=10):
    # Run the trials and collect results
    first_results = first_set_trials(trials)  # Collect results from the first set
    second_results = second_set_trials(trials)  # Collect results from the second set

    # Combine results from both sets
    all_results = first_results + second_results

    # Calculate and display summary statistics
    calculate_summary_stats(all_results)

    # Write the results to a CSV file
    with open(LOG_FILE, 'w', newline='') as csvfile:
        # Define fieldnames based on expected result structure
        fieldnames = ['trial_type', 'word', 'color', 'response', 'correct', 'reaction_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in all_results:
            # Ensure that the result dictionaries have consistent keys
            if result['trial_type'] == 'First Set':
                writer.writerow({
                    'trial_type': result['trial_type'],
                    'word': result['word'],  # Word shown in the first set
                    'color': '',  # No color for the first set
                    'response': result['response'],
                    'correct': result['correct'],
                    'reaction_time': result['reaction_time']
                })
            else:  # Second Set
                writer.writerow({
                    'trial_type': result['trial_type'],
                    'word': '',  # No word for the second set
                    'color': result['color_name'],  # Color shown in the second set
                    'response': result['response'],
                    'correct': result['correct'],
                    'reaction_time': result['reaction_time']
                })

    print(f'Results saved to {LOG_FILE}')
    pygame.quit()

if __name__ == '__main__':
    main(trials=5)
