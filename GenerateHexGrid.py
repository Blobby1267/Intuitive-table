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


def generate_hexagons(start_x, start_y, hex_size, rows, cols, screen_size=(640, 480)):
    """
    Generate a hexagonal grid with the specified number of rows and columns, centered on the screen.
    Track unique corners of each hexagon.
    
    :param start_x: X-coordinate of the first hexagon's center
    :param start_y: Y-coordinate of the first hexagon's center
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
    corner_index = 0
    dx = 3/2 * hex_size  # Horizontal distance between centers
    dy = math.sqrt(3) * hex_size  # Vertical distance between rows

    # Calculate offsets to center the grid
    grid_width = (cols - 1) * dx + hex_size
    grid_height = (rows - 1) * dy + hex_size
    offset_x = (screen_size[0] - grid_width) / 2
    offset_y = (screen_size[1] - grid_height) / 2

    def is_close(corner1, corner2, margin=1):
        """
        Check if two corners are within a given margin of each other.
        
        :param corner1: First corner (x, y)
        :param corner2: Second corner (x, y)
        :param margin: Error margin
        :return: True if the corners are within the margin, False otherwise
        """
        return abs(corner1[0] - corner2[0]) <= margin and abs(corner1[1] - corner2[1]) <= margin

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * dx + offset_x
            y = start_y + row * dy + offset_y
            # Offset every other row to create the staggered hexagonal grid
            if col % 2 == 1:
                y += dy / 2
            hex_positions.append((x, y))
            hex_map[len(hex_positions) - 1] = (x, y)

            # Calculate corners and track unique ones
            corners = [
                (x + hex_size * math.cos(math.radians(angle)), 
                 y + hex_size * math.sin(math.radians(angle)))
                for angle in range(0, 360, 60)
            ]
            for corner in corners:
                if not any(is_close(corner, existing_corner) for existing_corner in corner_map.values()):
                    corner_map[corner_index] = corner
                    corner_index += 1

    return hex_positions, hex_map, corner_map

"""
# Update the function call to include corner tracking
iterative_hex_positions, hexagon_map, corner_map = generate_hexagons(0, 0, 20, 10, 10, screen_size=(640, 480))
display_hexagon_grid_pygame(iterative_hex_positions, 20, corner_map=corner_map)

# Debugging: Print the hexagon map and corner map to verify tracking
print("\nHexagon Map:", hexagon_map)
print("\nCorner Map:", corner_map)"
"""