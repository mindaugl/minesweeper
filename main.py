import asyncio
import sys
from random import sample

import pygame

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WIDTH_SEPARATOR = 2
CELL_LENGTH = 50
FIELD_OFFSET = 100

ROW_COUNT = 10
COL_COUNT = 20
MINES_COUNT = 40

cell_values = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
# cell states: 0 - closed, 1 - flag, 2 - open
cell_states = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]


def get_files_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        return "."


def set_mines():
    mines_indices = sample(range(ROW_COUNT * COL_COUNT), MINES_COUNT)
    for ind in mines_indices:
        cell_values[ind // COL_COUNT][ind % COL_COUNT] = -1


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
    text_rect = text_surface.get_rect(center=(300, 50))
    rect_background = text_rect.scale_by(1.2)
    pygame.draw.rect(screen, "white", rect_background, 0)
    screen.blit(text_surface, text_rect)
    return hours != 99


show_timer.time_ms = 0


def set_numbers():
    for i in range(ROW_COUNT):
        for j in range(COL_COUNT):
            value = 0
            if cell_values[i][j] == -1:
                continue
            if i > 0:
                value += 1 if cell_values[i - 1][j] == -1 else 0
            if j > 0:
                value += 1 if cell_values[i][j - 1] == -1 else 0
            if i < ROW_COUNT - 1:
                value += 1 if cell_values[i + 1][j] == -1 else 0
            if j < COL_COUNT - 1:
                value += 1 if cell_values[i][j + 1] == -1 else 0
            if i > 0 and j > 0:
                value += 1 if cell_values[i - 1][j - 1] == -1 else 0
            if i < ROW_COUNT - 1 and j < COL_COUNT - 1:
                value += 1 if cell_values[i + 1][j + 1] == -1 else 0
            if i > 0 and j < COL_COUNT - 1:
                value += 1 if cell_values[i - 1][j + 1] == -1 else 0
            if i < ROW_COUNT - 1 and j > 0:
                value += 1 if cell_values[i + 1][j - 1] == -1 else 0
            cell_values[i][j] = value


def draw_get_reset_button(img, screen):
    rect_position = (130, 20)
    screen.blit(img, rect_position)
    rect_img = img.get_rect()
    rect_img.move_ip(rect_position)
    return rect_img


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


def game_over(cells_array, screen, images, i_expl, j_expl):
    mine_img = images["mine"]
    number_imgs = images["numbers"]
    explode_img = images["explode"]
    main_path = get_files_path()
    explosion_sound_file = f"{main_path}/audio/dragon-studio-explosion-fx-425453.mp3"
    for i in range(ROW_COUNT):
        for j in range(COL_COUNT):
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


def reveal_cells(screen, cells_array, images, i, j):
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
        reveal_cells(screen, cells_array, images, i - 1, j)
    if j > 0:
        reveal_cells(screen, cells_array, images, i, j - 1)
    if i < ROW_COUNT - 1:
        reveal_cells(screen, cells_array, images, i + 1, j)
    if j < COL_COUNT - 1:
        reveal_cells(screen, cells_array, images, i, j + 1)
    if i > 0 and j > 0:
        reveal_cells(screen, cells_array, images, i - 1, j - 1)
    if i < ROW_COUNT - 1 and j < COL_COUNT - 1:
        reveal_cells(screen, cells_array, images, i + 1, j + 1)
    if i > 0 and j < COL_COUNT - 1:
        reveal_cells(screen, cells_array, images, i - 1, j + 1)
    if i < ROW_COUNT - 1 and j > 0:
        reveal_cells(screen, cells_array, images, i + 1, j - 1)


def game_win(screen):
    font = pygame.font.SysFont(None, 56)
    text = "You Won!"
    text_surface = font.render(text, True, "green")
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text_surface, text_rect)


def new_game(screen, images, cell_values, cell_states):
    cell_values[:] = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
    cell_states[:] = [[0 for _ in range(COL_COUNT)] for _ in range(ROW_COUNT)]
    reveal_cells.empty_remaining = ROW_COUNT * COL_COUNT - MINES_COUNT

    set_mines()
    set_numbers()

    screen.fill("white")
    cells_array = draw_and_get_all_closed(
        screen, ROW_COUNT, COL_COUNT, images["closed"]
    )
    draw_frame(screen, ROW_COUNT, COL_COUNT)
    reset_cell = draw_get_reset_button(images["reset"], screen)
    return cells_array, reset_cell


def play_music():
    main_path = get_files_path()
    music_file = f"{main_path}/audio/mirostar-study-lofi-music-560307.mp3"
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1, 0.0)


async def main():

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
        "reset": load_image("reset"),
    }

    main_path = get_files_path()
    sound_click = pygame.mixer.Sound(f"{main_path}/audio/click3.mp3")
    sound_click.set_volume(0.2)

    cells_array, reset_cell = new_game(screen, cell_images, cell_values, cell_states)

    play_music()

    while running:
        if reveal_cells.empty_remaining == 0:
            game_win(screen)
            game_limbo = True
        if not game_limbo:
            running = show_timer(clock, screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and reset_cell.collidepoint(
                pygame.mouse.get_pos()
            ):  # reset
                game_limbo = False
                cells_array, reset_cell = new_game(
                    screen, cell_images, cell_values, cell_states
                )
                show_timer.time_ms = 0
            if not game_limbo and event.type == pygame.MOUSEBUTTONDOWN:  # main cells
                for i in range(ROW_COUNT):
                    for j in range(COL_COUNT):
                        cell = cells_array[i][j]
                        value = cell_values[i][j]
                        if cell.collidepoint(pygame.mouse.get_pos()):
                            if event.button == 1:  # Left mouse button
                                if cell_states[i][j] == 1:  # flag
                                    continue
                                if value == -1:
                                    game_over(cells_array, screen, cell_images, i, j)
                                    game_limbo = True
                                else:
                                    if cell_states[i][j] == 0:
                                        sound_click.play()
                                    reveal_cells(screen, cells_array, cell_images, i, j)
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
