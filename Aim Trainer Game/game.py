# -------------------- IMPORT MODULES --------------------
import math
import random
import time
import pygame

# Initialize pygame
pygame.init()

# -------------------- WINDOW SETTINGS --------------------
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AIM Trainer")

# -------------------- GAME SETTINGS --------------------
TARGET_INCREMENT = 400                  # New target every 400 ms
TARGET_EVENT = pygame.USEREVENT          # Custom pygame event
TARGET_PADDING = 30

BG_COLOR = (0, 50, 40)                   # Background color
TOP_BAR_HEIGHT = 35
LIVES = 3
GAME_TIME = 60                           # ⏱️ FIXED GAME TIME (seconds)

LABEL_FONT = pygame.font.SysFont("arial", 24)

# -------------------- TARGET CLASS --------------------
class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "blue"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        """Increase size, then shrink"""
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        """Draw layered target circles"""
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), int(self.size))
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), int(self.size * 0.8))
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), int(self.size * 0.6))
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), int(self.size * 0.4))

    def collide(self, x, y):
        """Check if mouse click hits target"""
        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= self.size


# -------------------- DRAW FUNCTIONS --------------------
def draw(win, targets):
    """Draw background and targets"""
    win.fill(BG_COLOR)
    for target in targets:
        target.draw(win)


def format_time(secs):
    """Convert seconds to MM:SS.ms"""
    milli = int((secs * 1000) % 1000) // 100
    seconds = int(secs % 60)
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"


def draw_top_bar(win, elapsed_time, hits, misses):
    """Top stats bar"""
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))

    speed = hits / elapsed_time if elapsed_time > 0 else 0

    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", True, "black")
    speed_label = LABEL_FONT.render(f"Speed: {round(speed,1)} t/s", True, "black")
    hits_label = LABEL_FONT.render(f"Hits: {hits}", True, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", True, "black")

    win.blit(time_label, (10, 8))
    win.blit(speed_label, (200, 8))
    win.blit(hits_label, (430, 8))
    win.blit(lives_label, (620, 8))


def get_middle(surface):
    """Center text horizontally"""
    return WIDTH // 2 - surface.get_width() // 2


# -------------------- END SCREEN --------------------
def end_screen(win, elapsed_time, hits, clicks):
    """Show final results"""
    win.fill(BG_COLOR)

    accuracy = (hits / clicks * 100) if clicks > 0 else 0
    speed = hits / elapsed_time if elapsed_time > 0 else 0

    labels = [
        f"Time Played: {format_time(elapsed_time)}",
        f"Hits: {hits}",
        f"Speed: {round(speed,1)} t/s",
        f"Accuracy: {round(accuracy,1)}%"
    ]

    for i, text in enumerate(labels):
        label = LABEL_FONT.render(text, True, "white")
        win.blit(label, (get_middle(label), 150 + i * 60))

    pygame.display.update()

    # Wait until user exits
    while True:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                pygame.quit()
                quit()


# -------------------- MAIN GAME LOOP --------------------
def main():
    clock = pygame.time.Clock()
    targets = []

    hits = 0
    clicks = 0
    missed = 0

    start_time = time.time()
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    run = True
    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()

        elapsed_time = time.time() - start_time

        # ⏱️ END GAME WHEN TIME IS OVER
        if elapsed_time >= GAME_TIME:
            end_screen(WIN, elapsed_time, hits, clicks)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                targets.append(Target(x, y))

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        # Update targets
        for target in targets[:]:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                missed += 1

            elif click and target.collide(*mouse_pos):
                targets.remove(target)
                hits += 1

        # End if lives lost
        if missed >= LIVES:
            end_screen(WIN, elapsed_time, hits, clicks)

        # Draw everything
        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, hits, missed)
        pygame.display.update()

    pygame.quit()


# -------------------- RUN PROGRAM --------------------
if __name__ == "__main__":
    main()
