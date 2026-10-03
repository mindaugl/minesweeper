import asyncio
import sys
from random import sample

import pygame

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WIDTH_SEPARATOR = 1
CELL_LENGTH = 40
FIELD_OFFSET = 100

DIFFICULTIES = {
    "easy": {"row_count": 10, "col_count": 12, "mines_count": 15},
    "medium": {"row_count": 10, "col_count": 20, "mines_count": 35},
    "hard": {"row_count": 14, "col_count": 27, "mines_count": 65},
}


difficulty = DIFFICULTIES["medium"]

cell_values = [
    [0 for _ in range(difficulty["col_count"])] for _ in range(difficulty["row_count"])
]
# cell states: 0 - closed, 1 - flag, 2 - open
cell_states = [
    [0 for _ in range(difficulty["col_count"])] for _ in range(difficulty["row_count"])
]


def get_files_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        return "."


def set_mines(difficulty):
    rows = difficulty["row_count"]
    cols = difficulty["col_count"]
    mines = difficulty["mines_count"]
    mines_indices = sample(range(rows * cols), mines)
    for ind in mines_indices:
        cell_values[ind // cols][ind % cols] = -1


def show_timer(clock, screen):
    show_timer.time_ms += clock.get_time()

    seconds = show_timer.time_ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    seconds %= 60

    if hours > 23:
        hours = 99
        minutes = 99
        seconds = 99

    sec_txt = str(seconds) if seconds > 9 else f"0{seconds}"
    min_txt = str(minutes) if minutes > 9 else f"0{minutes}"
    hour_txt = str(hours) if hours > 9 else f"0{hours}"

    font = pygame.font.SysFont(None, 40)
    text = f"{hour_txt}:{min_txt}:{sec_txt}"
    text_surface = font.render(text, True, "black")
    text_rect = text_surface.get_rect(center=(600, 50))
    rect_background = text_rect.scale_by(1.2)
    pygame.draw.rect(screen, "white", rect_background, 0)
    screen.blit(text_surface, text_rect)
    return hours != 99


show_timer.time_ms = 0


def set_numbers(difficulty):
    rows = difficulty["row_count"]
    cols = difficulty["col_count"]
    mines = difficulty["mines_count"]
    for i in range(rows):
        for j in range(cols):
            value = 0
            if cell_values[i][j] == -1:
                continue
            if i > 0:
                value += 1 if cell_values[i - 1][j] == -1 else 0
            if j > 0:
                value += 1 if cell_values[i][j - 1] == -1 else 0
            if i < rows - 1:
                value += 1 if cell_values[i + 1][j] == -1 else 0
            if j < cols - 1:
                value += 1 if cell_values[i][j + 1] == -1 else 0
            if i > 0 and j > 0:
                value += 1 if cell_values[i - 1][j - 1] == -1 else 0
            if i < rows - 1 and j < cols - 1:
                value += 1 if cell_values[i + 1][j + 1] == -1 else 0
            if i > 0 and j < cols - 1:
                value += 1 if cell_values[i - 1][j + 1] == -1 else 0
            if i < rows - 1 and j > 0:
                value += 1 if cell_values[i + 1][j - 1] == -1 else 0
            cell_values[i][j] = value


def draw_button(img, rect_position, screen):
    screen.blit(img, rect_position)
    rect_img = img.get_rect()
    rect_img.move_ip(rect_position)
    return rect_img


def draw_difficulty_buttons(easy_img, medium_img, hard_img, screen):
    difficulty_rects = {
        "easy": draw_button(easy_img, (FIELD_OFFSET, 30), screen),
        "medium": draw_button(medium_img, (FIELD_OFFSET + 130, 30), screen),
        "hard": draw_button(hard_img, (FIELD_OFFSET + 260, 30), screen),
    }
    return difficulty_rects


def load_image(name, length=CELL_LENGTH, height=CELL_LENGTH):
    main_path = get_files_path()
    image = pygame.image.load(f"{main_path}/images/{name}.jpg").convert()
    image = pygame.transform.scale(image, (length, height))
    return image


def load_number_images():
    images = []
    for i in range(10):
        image = load_image(i)
        images.append(image)
    return images


def draw_frame(screen, rows, cols):
    width = WIDTH_SEPARATOR
    length = WIDTH_SEPARATOR + CELL_LENGTH
    color = "grey"
    for i in range(rows + 1):
        rect = pygame.Rect(
            FIELD_OFFSET, FIELD_OFFSET + i * length, cols * length + width, width
        )
        pygame.draw.rect(screen, color, rect)
    for i in range(cols + 1):
        rect = pygame.Rect(
            FIELD_OFFSET + i * length, FIELD_OFFSET, width, rows * length + width
        )
        pygame.draw.rect(screen, color, rect)


def draw_and_get_all_closed(screen, rows, cols, img):
    width = WIDTH_SEPARATOR
    length = WIDTH_SEPARATOR + CELL_LENGTH
    rects = []
    for i in range(rows):
        row = []
        for j in range(cols):
            rect_position = (
                FIELD_OFFSET + width + j * length,
                FIELD_OFFSET + width + i * length,
            )
            screen.blit(img, rect_position)
            rect_img = img.get_rect()
            rect_img.move_ip(rect_position)
            row.append(rect_img)
        rects.append(row)
    return rects


def game_over(cells_array, screen, images, difficulty, i_expl, j_expl):
    mine_img = images["mine"]
    number_imgs = images["numbers"]
    explode_img = images["explode"]
    rows = difficulty["row_count"]
    cols = difficulty["col_count"]
    main_path = get_files_path()
    explosion_sound_file = f"{main_path}/audio/dragon-studio-explosion-fx-425453.mp3"
    for i in range(rows):
        for j in range(cols):
            cell = cells_array[i][j]
            value = cell_values[i][j]
            if value == -1:
                screen.blit(mine_img, (cell.x, cell.y))
            else:
                screen.blit(number_imgs[value], (cell.x, cell.y))
    cell = cells_array[i_expl][j_expl]
    screen.blit(explode_img, (cell.x, cell.y))

    font = pygame.font.SysFont(None, 56)
    text = "Game Over!"
    text_surface = font.render(text, True, "red")
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)

    explosion_sound = pygame.mixer.Sound(explosion_sound_file)
    explosion_sound.play()


def reveal_cells(screen, cells_array, images, difficulty, i, j):
    rows = difficulty["row_count"]
    cols = difficulty["col_count"]
    if cell_states[i][j] == 2 or cell_states[i][j] == 1:  # open or flag
        return
    value = cell_values[i][j]
    cell = cells_array[i][j]
    screen.blit(images["numbers"][value], (cell.x, cell.y))
    cell_states[i][j] = 2
    reveal_cells.empty_remaining -= 1
    if value != 0:
        return

    if i > 0:
        reveal_cells(screen, cells_array, images, difficulty, i - 1, j)
    if j > 0:
        reveal_cells(screen, cells_array, images, difficulty, i, j - 1)
    if i < rows - 1:
        reveal_cells(screen, cells_array, images, difficulty, i + 1, j)
    if j < cols - 1:
        reveal_cells(screen, cells_array, images, difficulty, i, j + 1)
    if i > 0 and j > 0:
        reveal_cells(screen, cells_array, images, difficulty, i - 1, j - 1)
    if i < rows - 1 and j < cols - 1:
        reveal_cells(screen, cells_array, images, difficulty, i + 1, j + 1)
    if i > 0 and j < cols - 1:
        reveal_cells(screen, cells_array, images, difficulty, i - 1, j + 1)
    if i < rows - 1 and j > 0:
        reveal_cells(screen, cells_array, images, difficulty, i + 1, j - 1)


def game_win(screen, time):
    font = pygame.font.SysFont(None, 56)
    best_time = get_best_time()
    if not best_time or time < best_time:
        text = f"You Won! New Best Time: {time / 1000}s"
        write_best_time(time)
    else:
        text = "You Won!"
    text_surface = font.render(text, True, "green")
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)


def new_game(screen, images, difficulty, cell_values, cell_states):
    rows = difficulty["row_count"]
    cols = difficulty["col_count"]
    mines = difficulty["mines_count"]
    cell_values[:] = [[0 for _ in range(cols)] for _ in range(rows)]
    cell_states[:] = [[0 for _ in range(cols)] for _ in range(rows)]
    reveal_cells.empty_remaining = rows * cols - mines

    set_mines(difficulty)
    set_numbers(difficulty)

    screen.fill("white")
    cells_array = draw_and_get_all_closed(screen, rows, cols, images["closed"])
    draw_frame(screen, rows, cols)
    difficulty_rects = draw_difficulty_buttons(
        images["easy"], images["medium"], images["hard"], screen
    )
    return cells_array, difficulty_rects


def play_music():
    main_path = get_files_path()
    music_file = f"{main_path}/audio/mirostar-study-lofi-music-560307.mp3"
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0)


def get_sound_click():
    main_path = get_files_path()
    sound_click = pygame.mixer.Sound(f"{main_path}/audio/click3.mp3")
    sound_click.set_volume(0.2)
    return sound_click


def get_best_time():
    main_path = get_files_path()
    with open(f"{main_path}/best_time.txt", "r") as f:
        time_text = f.read()
    if len(time_text) > 0:
        return int(time_text)
    return None


def write_best_time(value):
    main_path = get_files_path()
    if not value:
        value = ""
    with open(f"{main_path}/best_time.txt", "w") as f:
        f.write(str(value))


async def main():
    global difficulty

    # Initialize
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    game_limbo = False

    cell_images = {
        "numbers": load_number_images(),
        "closed": load_image("closed"),
        "flag": load_image("flag"),
        "mine": load_image("mine"),
        "explode": load_image("explode"),
        "easy": load_image("easy", 106, 40),
        "medium": load_image("medium", 106, 40),
        "hard": load_image("hard", 106, 40),
    }

    sound_click = get_sound_click()

    cells_array, difficulty_rects = new_game(
        screen, cell_images, difficulty, cell_values, cell_states
    )

    play_music()

    while running:
        if reveal_cells.empty_remaining == 0 and not game_limbo:
            game_win(screen, show_timer.time_ms)
            game_limbo = True
        if not game_limbo:
            running = show_timer(clock, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if difficulty_rects["easy"].collidepoint(
                    pygame.mouse.get_pos()
                ):  # reset easy
                    difficulty = DIFFICULTIES["easy"]
                    game_limbo = False
                    cells_array, difficulty_rects = new_game(
                        screen, cell_images, difficulty, cell_values, cell_states
                    )
                    show_timer.time_ms = 0
                elif difficulty_rects["medium"].collidepoint(
                    pygame.mouse.get_pos()
                ):  # reset medium
                    difficulty = DIFFICULTIES["medium"]
                    game_limbo = False
                    cells_array, difficulty_rects = new_game(
                        screen, cell_images, difficulty, cell_values, cell_states
                    )
                    show_timer.time_ms = 0
                elif difficulty_rects["hard"].collidepoint(
                    pygame.mouse.get_pos()
                ):  # reset hard
                    difficulty = DIFFICULTIES["hard"]
                    game_limbo = False
                    cells_array, difficulty_rects = new_game(
                        screen, cell_images, difficulty, cell_values, cell_states
                    )
                    show_timer.time_ms = 0

            if not game_limbo and event.type == pygame.MOUSEBUTTONDOWN:  # main cells
                for i in range(difficulty["row_count"]):
                    for j in range(difficulty["col_count"]):
                        cell = cells_array[i][j]
                        value = cell_values[i][j]
                        if cell.collidepoint(pygame.mouse.get_pos()):
                            if event.button == 1:  # Left mouse button
                                if cell_states[i][j] == 1:  # flag
                                    continue
                                if value == -1:
                                    game_over(
                                        cells_array,
                                        screen,
                                        cell_images,
                                        difficulty,
                                        i,
                                        j,
                                    )
                                    game_limbo = True
                                else:
                                    if cell_states[i][j] == 0:
                                        sound_click.play()
                                    reveal_cells(
                                        screen,
                                        cells_array,
                                        cell_images,
                                        difficulty,
                                        i,
                                        j,
                                    )
                            if event.button == 3:  # Right mouse button
                                if cell_states[i][j] == 0:  # closed
                                    sound_click.play()
                                    screen.blit(cell_images["flag"], (cell.x, cell.y))
                                    cell_states[i][j] = 1
                                elif cell_states[i][j] == 1:  # flag
                                    sound_click.play()
                                    screen.blit(cell_images["closed"], (cell.x, cell.y))
                                    cell_states[i][j] = 0

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


asyncio.run(main())
