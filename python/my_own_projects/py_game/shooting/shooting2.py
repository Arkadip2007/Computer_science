from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# গেম ইঞ্জিন চালু
app = Ursina()

# --- পরিবেশ (Environment) ---
Sky(texture='sky_sunset')

floor = Entity(
    name='floor',
    model='plane', 
    scale=(100, 1, 100), 
    color=color.white, 
    texture='grass',          
    texture_scale=(20, 20),   
    collider='box'
)

wall_props = {'name': 'wall', 'model': 'cube', 'color': color.clear, 'collider': 'box'}
Entity(position=(0, 5, 50), scale=(100, 10, 1), **wall_props)
Entity(position=(0, 5, -50), scale=(100, 10, 1), **wall_props)
Entity(position=(50, 5, 0), scale=(1, 10, 100), **wall_props)
Entity(position=(-50, 5, 0), scale=(1, 10, 100), **wall_props)

for i in range(25):
    Entity(
        name='wall',
        model='cube',
        position=(random.uniform(-40, 40), 2, random.uniform(-40, 40)),
        scale=(random.uniform(2, 6), random.uniform(3, 8), random.uniform(2, 6)),
        color=color.gray,
        texture='brick',
        texture_scale=(2, 2),
        collider='box'
    )

# --- প্লেয়ার এবং হেলথ (Player & Health) ---
player = FirstPersonController()
player.y = 5  
player.cursor.visible = True 
player_health = 100

gun = Entity(
    model='cube', parent=camera.ui, scale=(0.1, 0.1, 0.4), 
    position=(0.4, -0.3, 1), rotation=(5, -5, 0), color=color.dark_gray, texture='white_cube'
)

# --- UI (স্কোর এবং হেলথ বার) ---
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2, color=color.yellow, font='VeraMono.ttf')
health_text = Text(text=f"Health: {player_health}%", position=(-0.85, 0.38), scale=2, color=color.green, font='VeraMono.ttf')

# ড্যামেজ খেলে স্ক্রিন লাল হওয়ার জন্য পর্দা
damage_flash = Entity(parent=camera.ui, model='quad', color=color.clear, scale=(10, 10), z=1)

# --- Game Over Menu ---
game_over_menu = Entity(parent=camera.ui, enabled=False)
Entity(parent=game_over_menu, model='quad', color=color.black90, scale=(10, 10), z=1)
Text(parent=game_over_menu, text="GAME OVER", origin=(0, 0), y=0.1, scale=4, color=color.red)
Text(parent=game_over_menu, text="Press 'R' to Restart or 'Q' to Quit", origin=(0, 0), y=-0.1, scale=1.5, color=color.white)

# প্লেয়ার গুলি খেলে যা হবে
def take_damage():
    global player_health
    if player_health <= 0: return
    
    player_health -= 15
    health_text.text = f"Health: {max(0, player_health)}%"
    
    if player_health <= 40:
        health_text.color = color.red  # হেলথ কমলে লেখা লাল হয়ে যাবে

    # স্ক্রিন লাল হয়ে কাঁপবে
    damage_flash.color = color.rgba(255, 0, 0, 100)
    damage_flash.animate_color(color.clear, duration=0.3)

    # হেলথ জিরো হলে গেম ওভার
    if player_health <= 0:
        game_over_menu.enabled = True
        player.enabled = False
        mouse.locked = False

# --- Exit Menu (গেম বন্ধ করার মেনু) ---
exit_menu = Entity(parent=camera.ui, enabled=False)
Entity(parent=exit_menu, model='quad', color=color.black66, scale=(10, 10), z=1)
Text(parent=exit_menu, text="Are you sure you want to quit?", origin=(0, 0), y=0.1, scale=2, color=color.white)

def quit_game(): application.quit()
def resume_game():
    exit_menu.enabled = False
    mouse.locked = True    
    player.enabled = True   

Button(parent=exit_menu, text='Yes (Y)', color=color.red, scale=(0.2, 0.08), y=-0.1, x=-0.15, on_click=quit_game)
Button(parent=exit_menu, text='No (N)', color=color.green, scale=(0.2, 0.08), y=-0.1, x=0.15, on_click=resume_game)

# --- স্মার্ট এনিমি তৈরি (Smart Enemies) ---
enemies = []

class Enemy(Entity):
    def __init__(self, x, z):
        super().__init__(
            name='enemy',
            position=(x, 1.25, z),
            model='cube', 
            scale=(1, 2.5, 1),
            color=color.clear,  # আসল বক্সটি অদৃশ্য থাকবে
            collider='box'
        )
        # মানুষের মতো লুক তৈরি করা
        self.body = Entity(parent=self, model='cube', color=color.red, scale=(0.8, 0.6, 0.4), position=(0, -0.2, 0)) # ইউনিফর্ম
        self.head = Entity(parent=self, model='cube', color=color.peach, scale=(0.4, 0.4, 0.4), position=(0, 0.4, 0)) # মাথা
        self.enemy_gun = Entity(parent=self, model='cube', color=color.black, scale=(0.1, 0.1, 0.6), position=(0.3, -0.2, 0.4)) # এনিমির বন্দুক
        
        self.speed = random.uniform(1.5, 2.5) # একেক জনের হাঁটার স্পিড আলাদা
        self.last_shoot_time = time.time()
        self.shoot_delay = random.uniform(2.0, 3.5) # কতক্ষণ পর পর গুলি করবে
        enemies.append(self)

    def update(self):
        if player_health <= 0 or exit_menu.enabled: return
        
        # ১. প্লেয়ারের দিকে মুখ ঘোরানো (Math ম্যাজিক!)
        dx = player.x - self.x
        dz = player.z - self.z
        self.rotation_y = math.degrees(math.atan2(dx, dz))
        
        dist = distance(self.position, player.position)
        
        # ২. প্লেয়ার দূরে থাকলে কাছে হেঁটে আসবে, কাছে আসলে গুলি করবে
        if dist > 8:
            self.position += self.forward * self.speed * time.dt
        else:
            if time.time() - self.last_shoot_time > self.shoot_delay:
                self.last_shoot_time = time.time()
                
                # এনিমি গুলি করার ফ্লাশ
                flash = Entity(model='sphere', parent=self, position=(0.3, -0.2, 0.8), scale=0.3, color=color.yellow)
                destroy(flash, delay=0.1)
                
                take_damage() # প্লেয়ার ড্যামেজ খাবে

# গেমের ব্যালেন্স ঠিক রাখার জন্য প্লেয়ার থেকে দূরে এনিমি স্পন করা
def spawn_enemy():
    x, z = 0, 0
    # এনিমি যাতে প্লেয়ারের ঘাড়ের ওপর স্পন না হয় তার চেক
    while distance_2d((x, z), (player.x, player.z)) < 20:
        x = random.uniform(-35, 35)
        z = random.uniform(-35, 35)
    Enemy(x, z)

# গেম শুরুতে ৪ জন এনিমি
for i in range(4): spawn_enemy()

# গেম রিস্টার্ট করার ফাংশন
def restart_game():
    global score, player_health
    score = 0
    player_health = 100
    score_text.text = f"Score: {score}"
    health_text.text = f"Health: 100%"
    health_text.color = color.green
    player.position = (0, 5, 0)
    player.enabled = True
    mouse.locked = True
    game_over_menu.enabled = False
    
    # পুরোনো এনিমি ডিলিট করে নতুন ৪ জন তৈরি
    for e in enemies: destroy(e)
    enemies.clear()
    for i in range(4): spawn_enemy()

# --- গেম মেকানিক্স (Game Mechanics) ---
def update():
    if exit_menu.enabled or player_health <= 0: return

    # হাঁটার সময় বন্দুকের নড়াচড়া
    if held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']:
        gun.position = Vec3(0.4, -0.3 + math.sin(time.time() * 10) * 0.01, 1)
    else:
        gun.position = Vec3(0.4, -0.3, 1)

def input(key):
    global score
    
    # গেম ওভার হলে R বা Q চাপার কাজ
    if game_over_menu.enabled:
        if key == 'r': restart_game()
        if key == 'q': quit_game()
        return

    # Q চাপলে গেম পজ হবে
    if key == 'q':
        exit_menu.enabled = True
        mouse.locked = False    
        player.enabled = False  
    
    if exit_menu.enabled:
        if key == 'y': quit_game()
        if key == 'n': resume_game()
        return  

    if key == 'left mouse down':
        gun.animate_position(Vec3(0.4, -0.25, 0.9), duration=0.05)
        gun.animate_position(Vec3(0.4, -0.3, 1), duration=0.05, delay=0.05)
        
        flash = Entity(model='quad', parent=camera.ui, scale=0.1, position=(0.4, -0.2), color=color.yellow)
        destroy(flash, delay=0.05)
        
        hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(player,))
        
        if hit_info.hit and hit_info.entity.name == 'enemy':
            impact = Entity(model='sphere', position=hit_info.point, scale=0.3, color=color.orange)
            destroy(impact, delay=0.1)
            
            # এনিমি মারার পর স্কোর বাড়ানো এবং নতুন এনিমি স্পন করা
            if hit_info.entity in enemies:
                enemies.remove(hit_info.entity)
                destroy(hit_info.entity)
                
                score += 10
                score_text.text = f"Score: {score}"
                spawn_enemy() # একজনকে মারলে দূরে আরেকজন স্পন হবে

app.run()
