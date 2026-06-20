import sys
import os
import random
import pygame


WIDTH, HEIGHT = 500,750
FPS = 100

def draw_car(surface, rect):
	# Draw a simple stylized car using rectangles, polygon and circles
	bx = int(rect.x)
	by = int(rect.y + rect.height * 0.25)
	bw = int(rect.width)
	bh = int(rect.height * 0.55)
	body = pygame.Rect(bx, by, bw, bh)
	pygame.draw.rect(surface, (0, 0, 200), body, border_radius=8)

	# Roof
	roof = [
		(int(rect.x + rect.width * 0.18), int(rect.y + rect.height * 0.25)),
		(int(rect.x + rect.width * 0.82), int(rect.y + rect.height * 0.25)),
		(int(rect.x + rect.width * 0.65), int(rect.y + rect.height * 0.05)),
		(int(rect.x + rect.width * 0.35), int(rect.y + rect.height * 0.05)),
	]
	pygame.draw.polygon(surface, (0, 0, 170), roof)

	# Window
	wx = int(rect.x + rect.width * 0.38)
	wy = int(rect.y + rect.height * 0.07)
	ww = int(rect.width * 0.24)
	wh = int(rect.height * 0.14)
	pygame.draw.rect(surface, (160, 210, 255), (wx, wy, ww, wh), border_radius=4)

	# Wheels
	wr = max(6, int(rect.width * 0.18))
	wx1 = int(rect.x + rect.width * 0.22)
	wx2 = int(rect.x + rect.width * 0.78)
	wyw = int(rect.y + rect.height * 0.95)
	pygame.draw.circle(surface, (30, 30, 30), (wx1, wyw), wr)
	pygame.draw.circle(surface, (30, 30, 30), (wx2, wyw), wr)

def main():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Simple Car Racing")
	clock = pygame.time.Clock()
	font = pygame.font.SysFont(None, 32)

	player = pygame.Rect(WIDTH//2 - 20, HEIGHT - 120, 40, 80)
	player_speed = 6

	obstacles = []
	spawn_timer = 0
	spawn_delay = 800  # milliseconds between obstacle spawns
	score = 0.0
	speed_multiplier = 1.0
	game_over = False

	# High score persistence
	hs_file = os.path.join(os.path.dirname(__file__), 'highscore.txt')
	highscore = 0
	try:
		with open(hs_file, 'r') as f:
			highscore = int(f.read().strip() or 0)
	except Exception:
		highscore = 0
	new_high = False
	high_saved = False

	running = True
	while running:
		dt = clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN and game_over:
				if event.key == pygame.K_r:
					return main()

		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			player.x -= player_speed
		if keys[pygame.K_RIGHT]:
			player.x += player_speed
		player.x = max(0, min(WIDTH - player.width, player.x))

		if not game_over:
			spawn_timer += dt
			if spawn_timer >= spawn_delay:
				spawn_timer = 0
				ox = random.randint(40, WIDTH - 100)
				obstacles.append(pygame.Rect(ox, -80, 60, 80))

			for o in obstacles:
				o.y += int(4 * speed_multiplier * (dt / 16))

			obstacles = [o for o in obstacles if o.y < HEIGHT + 200]

			for o in obstacles:
				if o.colliderect(player):
					game_over = True
					# Save high score once when game over
					if not high_saved:
						if int(score) > highscore:
							highscore = int(score)
							try:
								with open(hs_file, 'w') as f:
									f.write(str(highscore))
							except Exception:
								pass
						new_high = True if int(score) >= highscore else False
						high_saved = True

			score += (dt * 0.01) * speed_multiplier
			speed_multiplier += dt * 0.00005

		screen.fill((50, 150, 50))
		pygame.draw.rect(screen, (70, 70, 70), (40, 0, WIDTH - 80, HEIGHT))

		for y in range(0, HEIGHT, 40):
			pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2, y), (WIDTH // 2, y + 20), 4)

		# draw detailed car
		draw_car(screen, player)

		for o in obstacles:
			pygame.draw.rect(screen, (200, 0, 0), o)

		score_surf = font.render(f"Score: {int(score)}", True, (255, 255, 255))
		screen.blit(score_surf, (10, 10))

		hs_surf = font.render(f"High: {highscore}", True, (255, 255, 255))
		screen.blit(hs_surf, (WIDTH - 120, 10))

		if game_over:
			over = font.render("Game Over - Press R to restart", True, (255, 255, 0))
			screen.blit(over, (30, HEIGHT // 2 - 16))
			if new_high:
				nh = font.render("New High Score!", True, (255, 200, 0))
				screen.blit(nh, (30, HEIGHT // 2 + 20))

		pygame.display.flip()

	pygame.quit()
	sys.exit()


if __name__ == '__main__':
	main()

