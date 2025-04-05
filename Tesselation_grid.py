import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Triangle Tessellation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Triangle tessellation parameters
TRIANGLE_SIZE = 50  # Length of each triangle's side

# Bounding rectangle for tessellation (x, y, width, height)
BOUNDING_RECT = (100, 100, 600, 400)

# Dictionary to store triangles and their corners
triangles = {}
corners = {}
corner_counter = 0

def generate_tessellation():
    global corner_counter
    row_height = TRIANGLE_SIZE * math.sqrt(3) / 2  # Height of an equilateral triangle
    triangle_id = 0

    for row in range(int(BOUNDING_RECT[3] // row_height) + 1):  # Limit rows to bounding rectangle height
        for col in range(int(BOUNDING_RECT[2] // (TRIANGLE_SIZE / 2)) + 1):  # Adjust column spacing to TRIANGLE_SIZE / 2
            # Calculate the base x, y position for the triangle
            x = BOUNDING_RECT[0] + col * TRIANGLE_SIZE / 2  # Offset by bounding rectangle x
            y = BOUNDING_RECT[1] + row * row_height  # Offset by bounding rectangle y

            # Alternate between upward and downward triangles
            if (row + col) % 2 == 0:
                # Upward triangle
                p1 = (x, y)
                p2 = (x + TRIANGLE_SIZE / 2, y + row_height)
                p3 = (x - TRIANGLE_SIZE / 2, y + row_height)
            else:
                # Downward triangle
                p1 = (x, y + row_height)
                p2 = (x + TRIANGLE_SIZE / 2, y)
                p3 = (x - TRIANGLE_SIZE / 2, y)

            # Check if all points are within the bounding rectangle
            if all(
                BOUNDING_RECT[0] <= point[0] <= BOUNDING_RECT[0] + BOUNDING_RECT[2] and
                BOUNDING_RECT[1] <= point[1] <= BOUNDING_RECT[1] + BOUNDING_RECT[3]
                for point in [p1, p2, p3]
            ):
                # Assign unique numbers to corners
                for point in [p1, p2, p3]:
                    if point not in corners.values():
                        corners[corner_counter] = point
                        corner_counter += 1

                # Store the triangle with its corner IDs
                corner_ids = [key for key, value in corners.items() if value in [p1, p2, p3]]
                triangles[triangle_id] = corner_ids
                triangle_id += 1

def draw_tessellation():
    # Draw bounding rectangle
    pygame.draw.rect(screen, BLACK, BOUNDING_RECT, 1)

    # Draw all triangles
    for triangle_id, corner_ids in triangles.items():
        points = [corners[corner_id] for corner_id in corner_ids]
        pygame.draw.polygon(screen, BLUE, points, 1)

    # Draw corner points
    for corner_id, position in corners.items():
        pygame.draw.circle(screen, BLACK, (int(position[0]), int(position[1])), 3)

def main():
    generate_tessellation()

    # Print the dictionary holding all the triangles
    print("Triangles Dictionary:", triangles)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill(WHITE)

        # Draw the tessellation
        draw_tessellation()

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()