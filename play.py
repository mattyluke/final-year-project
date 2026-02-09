import pygame
from pygame import surface

from game_logic import Board
import math

board = Board()
board.create_board()
pieces = board.get_pieces()

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

size = 30
x_offset = 400
y_offset = 250

def axial_to_pixel(q, r):
    x = size * math.sqrt(3) * (q + r / 2)
    y = size * 1.5 * r
    return x, y

def pixel_to_axial(x, y):
    x -= x_offset
    y -= y_offset

    q = (math.sqrt(3)/3 * x - 1/3 * y) / size
    r = (2/3 * y) / size
    return (round(q), round(0 - q - r) ,round(r))

def axial_to_notation(tuple):
    # e.g. (-1, -1, 2) -> 1n1n2p
    string = ""
    for num in tuple:
        if num < 0:
            string += str(abs(num))
            string += "n"
        else:
            string += str(num)
            string += "p"
    return string

def hex_corners(x, y):
    corners = []
    for i in range(6):
        angle = math.pi / 180 * (60 * i - 30)
        corner_x = x + size * math.cos(angle)
        corner_y = y + size * math.sin(angle)
        corners.append((corner_x, corner_y))
    return corners

def draw_arrows(surface, axial_coord, arrow_length = 25, color = (0, 0, 0)):
    q, _, r = axial_coord
    x, y = axial_to_pixel(q, r)
    x += x_offset
    y += y_offset

    corners = hex_corners(x, y)

    cx = sum(c[0] for c in corners) / 6
    cy = sum(c[1] for c in corners) / 6

    for i in range(6):
        x1, y1 = corners[i]
        x2, y2 = corners[(i + 1) % 6]

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        dx = mx - cx
        dy = my - cy

        length = math.hypot(dx, dy)
        if length == 0:
            continue
        dx /= length
        dy /= length

        pygame.draw.line(surface, color, (mx, my), (mx + dx * arrow_length, my + dy * arrow_length), 5)

        angle = math.atan2(dy, dx) + math.pi
        size_head = 10
        left = (
            mx + dx * arrow_length - size_head * math.cos(angle - math.pi*3/4),
            my + dy * arrow_length - size_head * math.sin(angle - math.pi*3/4)
        )
        right = (
            mx + dx * arrow_length - size_head * math.cos(angle + math.pi*3/4),
            my + dy * arrow_length - size_head * math.sin(angle + math.pi*3/4)
        )
        pygame.draw.polygon(surface, color, [(mx + dx*arrow_length, my + dy*arrow_length), right, left])

def draw_hex_grid(surface):
    for piece in pieces:
        coords = piece.get_coords()

        q = coords[0]
        r = coords[2]

        x, y = axial_to_pixel(q, r)

        x += x_offset
        y += y_offset

        pygame.draw.polygon(surface, (0, 0, 0), hex_corners(x, y), 5)

        if piece.get_occupation() != "N":
            cx = size * math.sqrt(3) * (q + r / 2)
            cy = size * 1.5 * r

            cx += x_offset
            cy += y_offset

            if piece.get_occupation() == "b":
                pygame.draw.circle(surface, (0, 0, 0), (int(cx), int(cy)), int(size / 3))
            else:
                pygame.draw.circle(surface, (255, 0, 0), (int(cx), int(cy)), int(size / 3))

def get_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p1[1] - p2[1]

    return math.atan2(dy, dx)

show_arrows = False
arrow_origin_coords = (0, 0, 0)
first_click_pos = (0, 0)
second_click_pos = (0, 0)

first_click = True
board_phase = False

winning_message = False

font = pygame.font.SysFont(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if winning_message:
                board = Board()
                board.create_board()
                pieces = board.get_pieces()

                winning_message = False
                show_arrows = False
                first_click = True
                board_phase = False
                continue

            if board_phase:
                if first_click:
                    first_click_pos = event.pos
                    first_click = False
                else:
                    second_click_pos = event.pos
                    board.parse_move(f"mb {axial_to_notation(pixel_to_axial(first_click_pos[0], first_click_pos[1]))} {axial_to_notation(pixel_to_axial(second_click_pos[0], second_click_pos[1]))}")
                    board_phase = False
                    first_click = True
            else:
                if first_click:
                    first_click = False
                    first_click_pos = event.pos
                    arrow_origin_coords = pixel_to_axial(event.pos[0], event.pos[1])
                    show_arrows = True
                else:
                    second_click_pos = event.pos
                    angle = get_angle(first_click_pos, second_click_pos)
                    angle %= 2 * math.pi

                    sector = round(angle / (math.pi/3) % 6)
                    dirs = ["ur", "ul", "ml", "dl", "dr", "mr"]
                    state = board.parse_move(f"mp {axial_to_notation(arrow_origin_coords)} {dirs[sector - 1]}")

                    if state == "win b":
                        winning_message = True
                        text_surface = font.render(f"Black has won the game!\nClick to restart", True, (0, 0, 0))
                    elif state == "win r":
                        winning_message = True
                        text_surface = font.render(f"Red has won the game!\nClick to restart", True, (0, 0, 0))

                    show_arrows = False
                    first_click = True
                    board_phase = True

    screen.fill((255, 255, 255))
    if show_arrows:
        draw_arrows(screen, arrow_origin_coords)

    draw_hex_grid(screen)

    if winning_message:
        screen.blit(text_surface, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()