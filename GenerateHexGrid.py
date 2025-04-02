import math
import pygame


def display_hexagon_grid_pygame(hex_positions, hex_size, screen_size=(640, 480), corner_map=None):
    """
    Display the hexagon grid using pygame, with numbered corners.
    
    :param hex_positions: List of (x, y) positions for hexagon centers
    :param hex_size: Size (radius) of each hexagon
    :param screen_size: Tuple for the screen size (width, height)
    :param corner_map: Dictionary mapping corner indices to their positions
    """
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Hexagon Grid")
    screen.fill((245, 245, 220))  # Light beige background for a beehive effect
    font = pygame.font.SysFont(None, 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((245, 245, 220))  # Clear screen
        for x, y in hex_positions:
            points = [
                (x + hex_size * math.cos(math.radians(angle)), 
                 y + hex_size * math.sin(math.radians(angle)))
                for angle in range(0, 360, 60)
            ]
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)  # Black edges, no fill

        # Draw corner numbers
        if corner_map:
            for corner_id, (cx, cy) in corner_map.items():
                text = font.render(str(corner_id), True, (255, 0, 0))  # Red text
                screen.blit(text, (cx - 5, cy - 5))  # Offset for better visibility

        pygame.display.flip()

    pygame.quit()


def generate_hexagons(x_start, y_start, hex_size, rows, cols, screen_size=(640, 480)):
    """
    Generate a hexagonal grid with the specified number of rows and columns, centered on the screen.
    Track unique corners of each hexagon.
    
    :param x_start: X-coordinate of the first hexagon's center
    :param y_start: Y-coordinate of the first hexagon's center
    :param hex_size: Size (radius) of each hexagon
    :param rows: Number of rows in the grid
    :param cols: Number of columns in the grid
    :param screen_size: Tuple for the screen size (width, height)
    :return: Tuple containing:
             - List of (x, y) positions for hexagon centers
             - Dictionary mapping hexagon index to its center point
             - Dictionary mapping corner index to its position
    """
    hex_positions = []
    hex_map = {}
    corner_map = {}
    corner_id_map = {}  # Maps corner positions to their assigned corner IDs
    corner_id_counter = 0

    dx = 3/2 * hex_size  # Horizontal distance between centers
    dy = math.sqrt(3) * hex_size  # Vertical distance between rows

    # Calculate offsets to center the grid
    grid_width = (cols - 1) * dx + hex_size
    grid_height = (rows - 1) * dy + hex_size
    offset_x = (screen_size[0] - grid_width) / 2
    offset_y = (screen_size[1] - grid_height) / 2

    for row in range(rows):
        for col in range(cols):
            # Calculate hexagon center position
            x = x_start + col * dx + offset_x
            y = y_start + row * dy + offset_y
            if col % 2 == 1:
                y += dy / 2  # Offset for odd columns

            hex_positions.append((x, y))
            hex_map[(row, col)] = len(hex_positions) - 1

            # Calculate corner positions
            corners = [
                (round(x + hex_size * math.cos(math.radians(angle)), 5),  # Round to avoid floating-point precision issues
                 round(y + hex_size * math.sin(math.radians(angle)), 5))
                for angle in range(0, 360, 60)
            ]

            # Assign corner IDs
            for corner in corners:
                if corner not in corner_id_map:
                    corner_id_map[corner] = corner_id_counter
                    corner_map[corner_id_counter] = corner
                    corner_id_counter += 1

    return hex_positions, hex_map, corner_map


# Update the function call to include corner tracking
#iterative_hex_positions, hexagon_map, corner_map = generate_hexagons(0, 0, 20, 10, 10, screen_size=(640, 480))
#display_hexagon_grid_pygame(iterative_hex_positions, 20, corner_map=corner_map)

# Debugging: Print the hexagon map and corner map to verify tracking
#print("\nHexagon Map:", hexagon_map)
#print("\nCorner Map:", corner_map)
