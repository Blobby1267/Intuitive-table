import GenerateHexGrid as ghg
import math
import pygame


def get_hexagon(circle_pos, hex_positions, hex_size):
    """
    Determine which hexagon the circle is currently on.
    
    :param circle_pos: (x, y) position of the circle
    :param hex_positions: List of (x, y) positions for hexagon centers
    :param hex_size: Size (radius) of each hexagon
    :return: Index of the hexagon the circle is on, or None if not on any hexagon
    """
    closest_hex = None
    min_distance = float('inf')

    for i, (hx, hy) in enumerate(hex_positions):
        distance = math.sqrt((circle_pos[0] - hx) ** 2 + (circle_pos[1] - hy) ** 2)
        if distance <= hex_size * 1.1:  # Slightly increase the radius to account for inaccuracies
            return i
        if distance < min_distance:  # Track the closest hexagon as a fallback
            min_distance = distance
            closest_hex = i

    # Fallback: Return the closest hexagon if no exact match is found
    return closest_hex


def move_circle(circle_pos, corner_pos, hex_center):
    """
    Move the circle parallel to the line passing through the corner and the hexagon center.
    
    :param circle_pos: (x, y) position of the circle
    :param corner_pos: (x, y) position of the selected corner
    :param hex_center: (x, y) position of the hexagon center
    :return: New (x, y) position of the circle
    """
    # Calculate the direction vector of the line passing through the corner and hex center
    direction = (corner_pos[0] - hex_center[0], corner_pos[1] - hex_center[1])
    magnitude = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
    
    if magnitude == 0:
        return circle_pos  # No movement if the corner and hex center are the same
    
    # Normalize the direction vector
    unit_vector = (direction[0] / magnitude, direction[1] / magnitude)
    
    # Calculate the perpendicular vector to the direction
    perpendicular_vector = (-unit_vector[1], unit_vector[0])
    
    # Move the circle parallel to the line
    step_size = 1  # Adjust step size as needed
    new_circle_pos = (circle_pos[0] + perpendicular_vector[0] * step_size,
                      circle_pos[1] + perpendicular_vector[1] * step_size)
    
    return new_circle_pos


def draw_extended_line(screen, color, start_pos, end_pos, width=1):
    """
    Draw a linear line that extends infinitely in both directions through the given points.

    :param screen: Pygame screen object
    :param color: Color of the line
    :param start_pos: (x, y) start position of the line
    :param end_pos: (x, y) end position of the line
    :param width: Width of the line
    """
    screen_width, screen_height = screen.get_size()
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]

    if dx == 0:  # Vertical line
        pygame.draw.line(screen, color, (start_pos[0], 0), (start_pos[0], screen_height), width)
    elif dy == 0:  # Horizontal line
        pygame.draw.line(screen, color, (0, start_pos[1]), (screen_width, start_pos[1]), width)
    else:
        slope = dy / dx
        intercept = start_pos[1] - slope * start_pos[0]

        x1, y1 = 0, intercept
        x2, y2 = screen_width, slope * screen_width + intercept

        pygame.draw.line(screen, color, (x1, y1), (x2, y2), width)


def select_corner_to_raise(circle_pos, destination, hex_positions, hex_size, corner_map, screen):
    """
    Select the corner to raise based on the circle's position, destination, and hexagon geometry.

    :param circle_pos: (x, y) position of the circle
    :param destination: (x, y) position of the destination
    :param hex_positions: List of (x, y) positions for hexagon centers
    :param hex_size: Size (radius) of each hexagon
    :param corner_map: Dictionary mapping corner IDs to their (x, y) positions
    :param screen: Pygame screen object for drawing
    :return: ID of the selected corner to raise
    """

    # Get the hexagon the circle is currently on
    current_hex = get_hexagon(circle_pos, hex_positions, hex_size)
    if current_hex is None:
        print("Circle is not on any hexagon.")
        return None

    # Get all corners of the current hexagon
    corners_in_hex = [corner_id for corner_id, corner_pos in corner_map.items()
                      if get_hexagon(corner_pos, hex_positions, hex_size) == current_hex]

    # Draw vector from circle to destination as an extended linear line
    draw_extended_line(screen, (255, 0, 0), circle_pos, destination, 2)  # Red line

    # Calculate perpendicular vector
    vector_to_destination = (destination[0] - circle_pos[0], destination[1] - circle_pos[1])
    perpendicular_vector = (-vector_to_destination[1], vector_to_destination[0])

    # Normalize the perpendicular vector
    magnitude = math.sqrt(perpendicular_vector[0] ** 2 + perpendicular_vector[1] ** 2)
    if magnitude != 0:
        perpendicular_vector = (perpendicular_vector[0] / magnitude, perpendicular_vector[1] / magnitude)

    # Filter corners to keep only those not on the side containing the destination
    filtered_corners = []
    for corner_id in corners_in_hex:
        corner_pos = corner_map[corner_id]
        vector_to_corner = (corner_pos[0] - circle_pos[0], corner_pos[1] - circle_pos[1])

        # Calculate the dot product to determine the side
        dot_product = (vector_to_corner[0] * vector_to_destination[0] +
                       vector_to_corner[1] * vector_to_destination[1])
        if dot_product < 0:  # Corner is on the opposite side of the destination
            filtered_corners.append(corner_id)

    # Draw extended lines from circle to each filtered corner
    closest_corner = None
    min_gradient_diff = float('inf')
    for corner_id in filtered_corners:
        corner_pos = corner_map[corner_id]
        draw_extended_line(screen, (0, 255, 0), circle_pos, corner_pos, 1)  # Green line

        # Calculate the gradient of the line to the corner
        vector_to_corner = (corner_pos[0] - circle_pos[0], corner_pos[1] - circle_pos[1])
        gradient_to_corner = math.atan2(vector_to_corner[1], vector_to_corner[0])
        gradient_to_destination = math.atan2(vector_to_destination[1], vector_to_destination[0])

        # Find the corner with the closest gradient to the destination vector
        gradient_diff = abs(gradient_to_corner - gradient_to_destination)
        if gradient_diff < min_gradient_diff:
            min_gradient_diff = gradient_diff
            closest_corner = corner_id

    print(f"Selected corner to raise: {closest_corner}")
    return closest_corner


def simulate_circle_movement(start_pos, destination, hex_positions, hex_size, corner_map, screen_size=(640, 480)):
    """
    Simulate the circle's movement on the grid toward the destination.
    """
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Circle Movement Simulation")
    clock = pygame.time.Clock()

    circle_pos = start_pos
    current_hex = get_hexagon(circle_pos, hex_positions, hex_size)
    corners_to_raise = []

    print(f"Initial circle position: {circle_pos}")

    # Check the initial corner to raise before starting movement
    current_hex = get_hexagon(circle_pos, hex_positions, hex_size)
    if current_hex is not None:
        selected_corner = select_corner_to_raise(circle_pos, destination, hex_positions, hex_size, corner_map, screen)
        if selected_corner is not None:
            corners_to_raise = [selected_corner]
            print(f"Initial selected corner to raise: {selected_corner}")
        else:
            print("No initial corner selected to raise.")
    else:
        print("Circle is not on any hexagon initially.")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((245, 245, 220))  # Clear screen

        # Draw hexagons
        for x, y in hex_positions:
            points = [
                (x + hex_size * math.cos(math.radians(angle)),
                 y + hex_size * math.sin(math.radians(angle)))
                for angle in range(0, 360, 60)
            ]
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)  # Black edges, no fill

        # Draw start position
        pygame.draw.circle(screen, (0, 0, 255), (int(start_pos[0]), int(start_pos[1])), 5)  # Blue circle

        # Draw destination
        pygame.draw.circle(screen, (255, 0, 0), (int(destination[0]), int(destination[1])), 5)  # Red circle

        # Draw selected corners
        for corner_id in corners_to_raise:
            corner_pos = corner_map[corner_id]
            pygame.draw.circle(screen, (0, 255, 0), (int(corner_pos[0]), int(corner_pos[1])), 5)  # Green circle

        # Draw circle
        pygame.draw.circle(screen, (0, 0, 255), (int(circle_pos[0]), int(circle_pos[1])), 5)  # Blue circle

        # Check if the circle has entered a new hexagon
        new_hex = get_hexagon(circle_pos, hex_positions, hex_size)
        if new_hex != current_hex:
            current_hex = new_hex
            print(f"Circle entered new hexagon: {current_hex}")
            if current_hex is not None:
                # Always select a new corner when entering a new hexagon
                selected_corner = select_corner_to_raise(circle_pos, destination, hex_positions, hex_size, corner_map, screen)
                if selected_corner is not None:
                    corners_to_raise = [selected_corner]
                    print(f"Selected new corner to raise: {selected_corner}")
                else:
                    print("No corner selected to raise.")

        # Draw vectors and move circle away from the next corner or destination
        if corners_to_raise:
            next_corner = corners_to_raise[0]
            corner_pos = corner_map[next_corner]

            # Draw vector from circle to corner
            pygame.draw.line(screen, (255, 0, 255), (int(circle_pos[0]), int(circle_pos[1])),
                             (int(corner_pos[0]), int(corner_pos[1])), 2)  # Magenta line

            # Move circle
            hex_center = hex_positions[current_hex]
            circle_pos = move_circle(circle_pos, corner_pos, hex_center)
            print(f"Moving circle to: {circle_pos}")

            # Check if the circle has reached the corner
            if math.sqrt((circle_pos[0] - corner_pos[0]) ** 2 + (circle_pos[1] - corner_pos[1]) ** 2) < 1:
                print(f"Reached corner: {next_corner}")
                corners_to_raise.pop(0)
        else:
            # Move directly toward the destination if no corners are selected
            circle_pos = move_circle(circle_pos, destination, hex_positions[current_hex])
            print(f"Moving circle directly toward destination: {circle_pos}")

        # Stop simulation if the circle is close enough to the destination
        if math.sqrt((circle_pos[0] - destination[0]) ** 2 + (circle_pos[1] - destination[1]) ** 2) < hex_size / 2:
            print("Circle reached the destination.")
            running = False

        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()


# Example usage
if __name__ == "__main__":
    hex_positions, hex_map, corner_map = ghg.generate_hexagons(0, 0, 20, 10, 10, screen_size=(640, 480))
    
    # Debug: Print hex_positions and corner_map
    print(f"Hex positions: {hex_positions}")
    print(f"Corner map: {corner_map}")
    start_pos = (200, 100)
    destination = (300, 300)
    simulate_circle_movement(start_pos, destination, hex_positions, 20, corner_map)

