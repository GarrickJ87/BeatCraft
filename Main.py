```python
import pygame
from pygame import mixer

# Initialize Pygame and set up the environment
pygame.init()

# Define color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (170, 170, 170)
BLUE = (0, 255, 255)
GREEN = (0, 255, 0)
GOLD = (212, 175, 55)

# Set screen dimensions
WIDTH, HEIGHT = 1400, 800

# Sound configurations
mixer.init()
sound_paths = {
    "hi_hat": "sounds/hi hat.wav",
    "snare": "sounds/snare.wav",
    "kick": "sounds/kick.wav",
    "crash": "sounds/crash.wav",
    "clap": "sounds/clap.wav",
    "tom": "sounds/tom.wav"
}
sounds = {key: mixer.Sound(value) for key, value in sound_paths.items()}

# Pygame screen setup
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("The Beat Maker")

# Font setup
LABEL_FONT = pygame.font.Font("Roboto-Bold.ttf", 32)
MEDIUM_FONT = pygame.font.Font("Roboto-Bold.ttf", 24)

# Timing and beat configuration
CLOCK = pygame.time.Clock()
FPS = 60
BEATS = 8
BPM = 240
INSTRUMENTS = 6

# Application state
playing = True
clicked = [[-1 for _ in range(BEATS)] for _ in range(INSTRUMENTS)]
active_list = [1 for _ in range(INSTRUMENTS)]
pygame.mixer.set_num_channels(INSTRUMENTS * 3)
save_menu = False
load_menu = False
saved_beats = []

# Load previously saved beats
with open('saved_beats.txt', 'r') as file:
    saved_beats = [line.strip() for line in file]

beat_name = ''
typing = False
index = 100
active_length = 0
active_beat = 0
beat_changed = True

def draw_grid(clicks, beat, actives):
    """Draw the grid and instrument labels on the screen."""
    boxes = []
    pygame.draw.rect(screen, GRAY, [0, 0, 200, HEIGHT - 200], 5)
    pygame.draw.rect(screen, GRAY, [0, HEIGHT - 200, WIDTH, 200], 5)
    
    for i in range(INSTRUMENTS + 1):
        pygame.draw.line(screen, GRAY, (0, i * 100), (200, i * 100), 3)
    
    instrument_labels = ["Hi Hat", "Snare", "Bass Drum", "Crash", "Clap", "Floor Tom"]
    colors = [GRAY, WHITE, GRAY]
    
    for i, label in enumerate(instrument_labels):
        text = LABEL_FONT.render(label, True, colors[actives[i]])
        screen.blit(text, (30, 30 + i * 100))
    
    for i in range(BEATS):
        for j in range(INSTRUMENTS):
            color = GREEN if clicks[j][i] == 1 and actives[j] == 1 else GRAY
            rect = pygame.draw.rect(screen, color, [i * ((WIDTH - 200) // BEATS) + 205, (j * 100) + 5, ((WIDTH - 200) // BEATS) - 10, 90], 0, 3)
            pygame.draw.rect(screen, GOLD, [i * ((WIDTH - 200) // BEATS) + 200, j * 100, ((WIDTH - 200) // BEATS), 100], 5, 5)
            pygame.draw.rect(screen, BLACK, [i * ((WIDTH - 200) // BEATS) + 200, j * 100, ((WIDTH - 200) // BEATS), 100], 2, 5)
            boxes.append((rect, (i, j)))
    
    pygame.draw.rect(screen, BLUE, [beat * ((WIDTH - 200) // BEATS) + 200, 0, ((WIDTH - 200) // BEATS), INSTRUMENTS * 100], 5, 3)
    return boxes

def play_notes():
    """Play the notes for the active beat."""
    for i in range(len(clicked)):
        if clicked[i][active_beat] == 1 and active_list[i] == 1:
            sounds[list(sound_paths.keys())[i]].play()

def draw_save_menu(name, is_typing):
    """Render the save menu on the screen."""
    pygame.draw.rect(screen, BLACK, [0, 0, WIDTH, HEIGHT])
    menu_text = LABEL_FONT.render('SAVE MENU: Enter a Name for this beat', True, WHITE)
    screen.blit(menu_text, (400, 40))
    
    exit_btn = pygame.draw.rect(screen, GRAY, [WIDTH - 200, HEIGHT - 100, 180, 90], 0, 5)
    exit_text = LABEL_FONT.render('Close', True, WHITE)
    screen.blit(exit_text, (WIDTH - 160, HEIGHT - 70))
    
    saving_btn = pygame.draw.rect(screen, GRAY, [WIDTH // 2 - 100, HEIGHT * 0.75, 200, 100], 0, 5)
    saving_text = LABEL_FONT.render('Save Beat', True, WHITE)
    screen.blit(saving_text, (WIDTH // 2 - 70, HEIGHT * 0.75 + 30))
    
    entry_rect = pygame.draw.rect(screen, DARK_GRAY if is_typing else GRAY, [400, 200, 600, 200], 5, 5)
    entry_text = LABEL_FONT.render(f'{name}', True, WHITE)
    screen.blit(entry_text, (430, 250))
    
    return exit_btn, saving_btn, name, entry_rect

def draw_load_menu(selected_index):
    """Render the load menu on the screen."""
    loaded_clicked = []
    loaded_beats = 0
    loaded_bpm = 0
    
    pygame.draw.rect(screen, BLACK, [0, 0, WIDTH, HEIGHT])
    menu_text = LABEL_FONT.render('LOAD MENU: Select a beat to load in', True, WHITE)
    screen.blit(menu_text, (400, 40))
    
    exit_btn = pygame.draw.rect(screen, GRAY, [WIDTH - 200, HEIGHT - 100, 180, 90], 0, 5)
    exit_text = LABEL_FONT.render('Close', True, WHITE)
    screen.blit(exit_text, (WIDTH - 160, HEIGHT - 70))
    
    loading_btn = pygame.draw.rect(screen, GRAY, [WIDTH // 2 - 100, HEIGHT * 0.87, 200, 100], 0, 5)
    loading_text = LABEL_FONT.render('Load Beat', True, WHITE)
    screen.blit(loading_text, (WIDTH // 2 - 70, HEIGHT * 0.87 + 30))
    
    delete_btn = pygame.draw.rect(screen, GRAY, [WIDTH // 2 - 400, HEIGHT * 0.87, 200, 100], 0, 5)
    delete_text = LABEL_FONT.render('Delete Beat', True, WHITE)
    screen.blit(delete_text, (WIDTH // 2 - 385, HEIGHT * 0.87 + 30))
    
    if 0 <= selected_index < len(saved_beats):
        pygame.draw.rect(screen, LIGHT_GRAY, [190, 100 + selected_index * 50, 1000, 50])
    
    for idx, beat in enumerate(saved_beats):
        if idx < 10:
            row_text = MEDIUM_FONT.render(f'{idx + 1}', True, WHITE)
            screen.blit(row_text, (200, 100 + idx * 50))
            name_index_start = beat.index('name: ') + 6
            name_index_end = beat.index(', beats:')
            name_text = MEDIUM_FONT.render(beat[name_index_start:name_index_end], True, WHITE)
            screen.blit(name_text, (240, 100 + idx * 50))
        
        if 0 <= selected_index < len(saved_beats) and idx == selected_index:
            beats_index_end = beat.index(', bpm:')
            loaded_beats = int(beat[name_index_end + 8:beats_index_end])
            bpm_index_end = beat.index(', selected:')
            loaded_bpm = int(beat[beats_index_end + 6:bpm_index_end])
            loaded_clicks_string = beat[bpm_index_end + 14:-3]
            loaded_clicks_rows = loaded_clicks_string.split("], [")
            
            for row in loaded_clicks_rows:
                loaded_clicks_row = [int(item) for item in row.split(', ') if item in {'1', '-1'}]
                loaded_clicked.append(loaded_clicks_row)
    
    loaded_info = [loaded_beats, loaded_bpm, loaded_clicked]
    pygame.draw.rect(screen, GRAY, [190, 90, 1000, 600], 5, 5)
    
    return exit_btn, loading_btn, delete_btn, loaded_info

def main():
    global playing, save_menu, load_menu, beat_name, typing, active_length,