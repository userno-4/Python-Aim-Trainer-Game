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

# 🎮 GAMING THEME COLORS
BG_COLOR = (10, 10, 25)                  # Dark navy background
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (138, 43, 226)
NEON_ORANGE = (255, 140, 0)
DARK_OVERLAY = (20, 20, 40)

TOP_BAR_HEIGHT = 50
LIVES = 3
GAME_TIME = 20                           # ⏱️ FIXED GAME TIME (seconds)

# 🎮 GAMING FONTS
LABEL_FONT = pygame.font.SysFont("consolas", 26, bold=True)
TITLE_FONT = pygame.font.SysFont("consolas", 48, bold=True)
STAT_FONT = pygame.font.SysFont("consolas", 32, bold=True)

# -------------------- TARGET CLASS --------------------
class Target:
    MAX_SIZE = 35
    GROWTH_RATE = 0.25
    COLOR = (255, 20, 147)      # Neon Pink
    SECOND_COLOR = (0, 255, 255) # Neon Cyan
    GLOW_COLOR = (255, 100, 200)

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
        """Draw layered target circles with glow effect"""
        # Outer glow
        glow_surface = pygame.Surface((int(self.size * 3), int(self.size * 3)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.GLOW_COLOR, 30), 
                          (int(self.size * 1.5), int(self.size * 1.5)), int(self.size * 1.5))
        win.blit(glow_surface, (self.x - int(self.size * 1.5), self.y - int(self.size * 1.5)))
        
        # Target circles
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), int(self.size))
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), int(self.size * 0.8))
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), int(self.size * 0.6))
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), int(self.size * 0.4))
        pygame.draw.circle(win, (255, 255, 255), (self.x, self.y), int(self.size * 0.15))

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
    """Top stats bar with gaming theme"""
    # Dark overlay bar
    bar_surface = pygame.Surface((WIDTH, TOP_BAR_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(bar_surface, (*DARK_OVERLAY, 200), (0, 0, WIDTH, TOP_BAR_HEIGHT))
    win.blit(bar_surface, (0, 0))
    
    # Neon bottom border
    pygame.draw.line(win, NEON_CYAN, (0, TOP_BAR_HEIGHT), (WIDTH, TOP_BAR_HEIGHT), 3)

    speed = hits / elapsed_time if elapsed_time > 0 else 0
    remaining_time = max(0, GAME_TIME - elapsed_time)

    # Stats with neon colors
    time_label = LABEL_FONT.render(f"⏱ {format_time(remaining_time)}", True, NEON_CYAN)
    speed_label = LABEL_FONT.render(f"⚡ {round(speed,1)} t/s", True, NEON_GREEN)
    hits_label = LABEL_FONT.render(f"🎯 {hits}", True, NEON_PINK)
    lives_label = LABEL_FONT.render(f"❤ {LIVES - misses}", True, NEON_ORANGE)

    win.blit(time_label, (15, 12))
    win.blit(speed_label, (220, 12))
    win.blit(hits_label, (430, 12))
    win.blit(lives_label, (620, 12))


def get_middle(surface):
    """Center text horizontally"""
    return WIDTH // 2 - surface.get_width() // 2


# -------------------- END SCREEN --------------------
def end_screen(win, elapsed_time, hits, clicks):
    """Show final results with gaming theme"""
    win.fill(BG_COLOR)

    # Title with glow
    title = TITLE_FONT.render("GAME OVER", True, NEON_PINK)
    title_shadow = TITLE_FONT.render("GAME OVER", True, (100, 10, 50))
    win.blit(title_shadow, (get_middle(title) + 3, 53))
    win.blit(title, (get_middle(title), 50))

    accuracy = (hits / clicks * 100) if clicks > 0 else 0
    speed = hits / elapsed_time if elapsed_time > 0 else 0

    # Stats panel
    panel_rect = pygame.Rect(WIDTH//2 - 250, 160, 500, 300)
    panel_surface = pygame.Surface((500, 300), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (*DARK_OVERLAY, 180), (0, 0, 500, 300), border_radius=15)
    pygame.draw.rect(panel_surface, NEON_CYAN, (0, 0, 500, 300), 3, border_radius=15)
    win.blit(panel_surface, panel_rect)

    stats = [
        (f"⏱ Time: {format_time(elapsed_time)}", NEON_CYAN),
        (f"🎯 Hits: {hits}", NEON_PINK),
        (f"⚡ Speed: {round(speed,1)} t/s", NEON_GREEN),
        (f"🎮 Accuracy: {round(accuracy,1)}%", NEON_ORANGE)
    ]

    for i, (text, color) in enumerate(stats):
        label = STAT_FONT.render(text, True, color)
        win.blit(label, (get_middle(label), 200 + i * 60))

    # Press any key message
    exit_msg = LABEL_FONT.render("Press any key to exit...", True, (150, 150, 150))
    win.blit(exit_msg, (get_middle(exit_msg), 500))

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
        remaining_time = GAME_TIME - elapsed_time

        # ⏱️ END GAME WHEN TIME REACHES EXACTLY 0
        if remaining_time <= 0:
            end_screen(WIN, GAME_TIME, hits, clicks)

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
