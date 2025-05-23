import pygame
import math
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 640, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Shooter")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
DARK_BLUE = (10, 10, 50)

# Game settings
FPS = 60
RADIUS = 20
ROWS = 10
COLS = 14
BUBBLE_DIAMETER = RADIUS * 2
MOVE_LIMIT = 30  # max moves before game over
DROP_INTERVAL = 5  # after how many shots the bubbles drop down

# Directions for aiming (clamp angle between 10 to 170 degrees)
MIN_ANGLE = 10
MAX_ANGLE = 170

# Load bubble colors
BUBBLE_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
]

# Font
FONT = pygame.font.SysFont("comicsans", 30)
BIG_FONT = pygame.font.SysFont("comicsans", 60)

clock = pygame.time.Clock()

# Helper functions


def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont("comicsans", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# Classes


class Bubble:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = RADIUS
        self.row = None
        self.col = None

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x),
                           int(self.y)), self.radius, 2)

    def get_grid_pos(self):
        return self.row, self.col

    def set_grid_pos(self, row, col):
        self.row = row
        self.col = col


class Shooter:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.radius = RADIUS
        self.angle = 90  # straight up in degrees
        self.speed = 10
        self.shooting = False
        self.bubble = self.create_bubble()
        self.next_bubble = self.create_bubble()

    def create_bubble(self):
        color = random.choice(BUBBLE_COLORS)
        return Bubble(self.x, self.y, color)

    def rotate(self, direction):
        if direction == 'left':
            self.angle += 3
        elif direction == 'right':
            self.angle -= 3
        self.angle = max(MIN_ANGLE, min(MAX_ANGLE, self.angle))

    def draw(self, surface):
        # Draw cannon base
        pygame.draw.rect(surface, BLACK, (self.x - 20, self.y, 40, 40))

        # Draw bubble on cannon
        self.bubble.x = self.x + math.cos(math.radians(self.angle)) * 30
        self.bubble.y = self.y - math.sin(math.radians(self.angle)) * 30
        self.bubble.draw(surface)

        # Draw next bubble preview
        draw_text(surface, "Next:", 24, WHITE, 80, HEIGHT - 40, center=False)
        pygame.draw.circle(surface, self.next_bubble.color,
                           (150, HEIGHT - 30), RADIUS)
        pygame.draw.circle(surface, BLACK, (150, HEIGHT - 30), RADIUS, 2)

        # Draw aiming dotted line
        length = 100
        x_end = self.x + math.cos(math.radians(self.angle)) * length
        y_end = self.y - math.sin(math.radians(self.angle)) * length
        draw_dotted_line(surface, BLACK, (self.x, self.y),
                         (x_end, y_end), 5, 10)


def draw_dotted_line(surface, color, start_pos, end_pos, width=1, dot_length=5):
    # Draw dotted line between start_pos and end_pos
    x1, y1 = start_pos
    x2, y2 = end_pos
    length = distance(start_pos, end_pos)
    dots = int(length / (dot_length * 2))
    for i in range(dots):
        start_x = x1 + (x2 - x1) * (i / dots)
        start_y = y1 + (y2 - y1) * (i / dots)
        end_x = x1 + (x2 - x1) * ((i + 0.5) / dots)
        end_y = y1 + (y2 - y1) * ((i + 0.5) / dots)
        pygame.draw.line(surface, color, (start_x, start_y),
                         (end_x, end_y), width)


class Game:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.shooter = Shooter()
        self.bubbles = []  # all bubbles on board
        self.move_count = 0
        self.drop_count = 0
        self.score = 0
        self.state = "start"  # can be start, playing, gameover

        self.init_grid()

    def init_grid(self):
        # Initialize first 5 rows randomly
        for row in range(5):
            for col in range(COLS):
                if (row % 2 == 1) and (col == COLS - 1):
                    continue  # skip last col on odd rows (staggered)
                color = random.choice(BUBBLE_COLORS)
                x, y = self.get_bubble_pos(row, col)
                bubble = Bubble(x, y, color)
                bubble.set_grid_pos(row, col)
                self.grid[row][col] = bubble
                self.bubbles.append(bubble)

    def get_bubble_pos(self, row, col):
        x_offset = RADIUS if row % 2 == 1 else 0
        x = col * BUBBLE_DIAMETER + RADIUS + x_offset
        y = row * (RADIUS * 1.73) + RADIUS + 50
        return x, y

    def handle_events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.shooter.rotate('left')
        if keys[pygame.K_RIGHT]:
            self.shooter.rotate('right')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if self.state == "start" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = "playing"
            elif self.state == "playing" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.shooter.shooting:
                    self.shooter.shooting = True
                    self.current_bubble = self.shooter.bubble
                    self.shooter.bubble = self.shooter.next_bubble
                    self.shooter.next_bubble = self.shooter.create_bubble()
            elif self.state == "gameover" and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__()  # reset game

    def update(self):
        if self.state != "playing":
            return

        if self.shooter.shooting:
            # Move bubble
            angle_rad = math.radians(self.shooter.angle)
            self.current_bubble.x += math.cos(angle_rad) * self.shooter.speed
            self.current_bubble.y -= math.sin(angle_rad) * self.shooter.speed

            # Bounce on side walls
            if self.current_bubble.x <= RADIUS:
                self.current_bubble.x = RADIUS
                self.shooter.angle = 180 - self.shooter.angle
            elif self.current_bubble.x >= WIDTH - RADIUS:
                self.current_bubble.x = WIDTH - RADIUS
                self.shooter.angle = 180 - self.shooter.angle

            # Check for collision with bubbles or top
            if self.current_bubble.y <= RADIUS + 50:
                self.attach_bubble()
            else:
                for bubble in self.bubbles:
                    if distance((self.current_bubble.x, self.current_bubble.y), (bubble.x, bubble.y)) <= BUBBLE_DIAMETER - 2:
                        self.attach_bubble()
                        break

        # Check if bubbles reached bottom (game over)
        for bubble in self.bubbles:
            if bubble.y + RADIUS >= HEIGHT - 60:
                self.state = "gameover"

    def attach_bubble(self):
        # Find closest grid position
        row, col = self.get_closest_grid_pos(
            self.current_bubble.x, self.current_bubble.y)
        if row >= ROWS:
            row = ROWS - 1
        if col >= COLS:
            col = COLS - 1

        # Adjust col if odd row and col==COLS-1 (no bubble allowed)
        if row % 2 == 1 and col == COLS - 1:
            col -= 1

        x, y = self.get_bubble_pos(row, col)
        new_bubble = Bubble(x, y, self.current_bubble.color)
        new_bubble.set_grid_pos(row, col)
        self.grid[row][col] = new_bubble
        self.bubbles.append(new_bubble)

        # Remove connected bubbles of same color
        removed = self.remove_connected(new_bubble)
        if removed > 0:
            self.score += removed * 10

        self.shooter.shooting = False
        self.move_count += 1
        if self.move_count % DROP_INTERVAL == 0:
            self.drop_bubbles()

        # Check moves limit
        if self.move_count >= MOVE_LIMIT:
            self.state = "gameover"

    def get_closest_grid_pos(self, x, y):
        row = int((y - 50) / (RADIUS * 1.73))
        x_offset = RADIUS if row % 2 == 1 else 0
        col = int((x - x_offset) / BUBBLE_DIAMETER)
        return row, col

    def remove_connected(self, start_bubble):
        # BFS to find connected bubbles of the same color
        to_check = [start_bubble]
        connected = set()
        while to_check:
            bubble = to_check.pop()
            connected.add(bubble)
            neighbors = self.get_neighbors(bubble)
            for n in neighbors:
                if n.color == start_bubble.color and n not in connected:
                    to_check.append(n)
        if len(connected) >= 3:
            # Remove these bubbles
            for b in connected:
                self.grid[b.row][b.col] = None
                if b in self.bubbles:
                    self.bubbles.remove(b)
            return len(connected)
        return 0

    def get_neighbors(self, bubble):
        neighbors = []
        row, col = bubble.row, bubble.col
        directions_even = [(-1, 0), (-1, -1), (0, -1), (0, 1), (1, 0), (1, -1)]
        directions_odd = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
        directions = directions_odd if row % 2 == 1 else directions_even

        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                neighbor = self.grid[r][c]
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def drop_bubbles(self):
        # Move all bubbles down one row
        for bubble in self.bubbles:
            bubble.row += 1
            if bubble.row >= ROWS:
                self.state = "gameover"
            else:
                bubble.x, bubble.y = self.get_bubble_pos(
                    bubble.row, bubble.col)

        # Shift grid down
        self.grid.pop()
        self.grid.insert(0, [None for _ in range(COLS)])

    def draw(self):
        screen.fill(DARK_BLUE)

        # Draw bubbles on grid
        for bubble in self.bubbles:
            bubble.draw(screen)

        # Draw shooter
        self.shooter.draw(screen)

        # Draw score and moves left
        draw_text(screen, f"Score: {self.score}", 30,
                  WHITE, WIDTH - 120, HEIGHT - 40, center=False)
        draw_text(screen, f"Moves Left: {MOVE_LIMIT - self.move_count}",
                  30, WHITE, WIDTH - 260, HEIGHT - 40, center=False)

        if self.state == "start":
            draw_text(screen, "Bubble Shooter", 70,
                      WHITE, WIDTH // 2, HEIGHT // 3)
            draw_text(screen, "Press SPACE to Start",
                      40, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, "Use LEFT and RIGHT arrows to Aim",
                      30, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
            draw_text(screen, "Press SPACE to Shoot", 30,
                      WHITE, WIDTH // 2, HEIGHT // 2 + 80)

        elif self.state == "gameover":
            draw_text(screen, "Game Over", 70, WHITE, WIDTH // 2, HEIGHT // 3)
            draw_text(
                screen, f"Final Score: {self.score}", 50, WHITE, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, "Press R to Restart", 40,
                      WHITE, WIDTH // 2, HEIGHT // 2 + 60)

        pygame.display.flip()


def main():
    game = Game()
    while True:
        clock.tick(FPS)
        game.handle_events()
        game.update()
        game.draw()


if __name__ == "__main__":
    main()
