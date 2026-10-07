from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# গেম ইঞ্জিন চালু
app = Ursina()

# --- পরিবেশ (Environment) ---
Sky(texture='sky_sunset')

# মাটি বা ফ্লোর (এটার নাম দিয়ে দিলাম 'floor' যাতে ডিলিট না হয়)
floor = Entity(
    name='floor',
    model='plane', 
    scale=(100, 1, 100), 
    color=color.white, 
    texture='grass',          
    texture_scale=(20, 20),   
    collider='box'
)

# ম্যাপের চারদিকে অদৃশ্য সীমানা 
wall_props = {'name': 'wall', 'model': 'cube', 'color': color.clear, 'collider': 'box'}
Entity(position=(0, 5, 50), scale=(100, 10, 1), **wall_props)
Entity(position=(0, 5, -50), scale=(100, 10, 1), **wall_props)
Entity(position=(50, 5, 0), scale=(1, 10, 100), **wall_props)
Entity(position=(-50, 5, 0), scale=(1, 10, 100), **wall_props)

# বাধা বা পিলার
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

# --- প্লেয়ার (Player) ---
player = FirstPersonController()
player.y = 5  
player.cursor.visible = True 

# --- অস্ত্র (Weapon) ---
gun = Entity(
    model='cube', 
    parent=camera.ui,       
    scale=(0.1, 0.1, 0.4), 
    position=(0.4, -0.3, 1), 
    rotation=(5, -5, 0),
    color=color.dark_gray,
    texture='white_cube'
)

# --- UI (স্কোরবোর্ড) ---
score = 0
score_text = Text(text=f"Score: {score}", position=(-0.85, 0.45), scale=2, color=color.yellow, font='VeraMono.ttf')

# --- Exit Menu (গেম বন্ধ করার মেনু) ---
exit_menu = Entity(parent=camera.ui, enabled=False)

Entity(parent=exit_menu, model='quad', color=color.black66, scale=(10, 10), z=1)
Text(parent=exit_menu, text="Are you sure you want to quit?", origin=(0, 0), y=0.1, scale=2, color=color.white)

def quit_game():
    application.quit()

def resume_game():
    exit_menu.enabled = False
    mouse.locked = True    
    player.enabled = True   

yes_btn = Button(parent=exit_menu, text='Yes (Y)', color=color.red, scale=(0.2, 0.08), y=-0.1, x=-0.15, on_click=quit_game)
no_btn = Button(parent=exit_menu, text='No (N)', color=color.green, scale=(0.2, 0.08), y=-0.1, x=0.15, on_click=resume_game)

# --- টার্গেট বা শত্রু (Enemies) ---
targets = []
def spawn_target():
    target = Entity(
        name='enemy',   # এখানে নাম দিয়ে দিলাম 'enemy', যাতে শুধু এটাই ডিলিট হয়
        model='cube',
        color=color.red,
        texture='white_cube',
        position=(random.uniform(-35, 35), 1.5, random.uniform(-35, 35)),
        scale=(1.5, 3, 1.5),
        collider='box'
    )
    targets.append(target)

for i in range(8):
    spawn_target()

# --- গেম মেকানিক্স (Game Mechanics) ---
def update():
    if exit_menu.enabled:
        return

    if held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']:
        gun.position = Vec3(0.4, -0.3 + math.sin(time.time() * 10) * 0.01, 1)
    else:
        gun.position = Vec3(0.4, -0.3, 1)

def input(key):
    global score
    
    if key == 'q':
        exit_menu.enabled = True
        mouse.locked = False    
        player.enabled = False  
    
    if exit_menu.enabled:
        if key == 'y':
            quit_game()
        if key == 'n':
            resume_game()
        return  

    if key == 'left mouse down':
        gun.animate_position(Vec3(0.4, -0.25, 0.9), duration=0.05)
        gun.animate_position(Vec3(0.4, -0.3, 1), duration=0.05, delay=0.05)
        
        flash = Entity(model='quad', parent=camera.ui, scale=0.1, position=(0.4, -0.2), color=color.yellow)
        destroy(flash, delay=0.05)
        
        # Raycasting: এখানে ignore=(player,) দিয়েছি যাতে প্লেয়ার নিজের গায়ে গুলি না করে ফেলে
        hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(player,))
        
        # এখানে চেক করছি যে, গুলি কি লেগেছে? এবং যেটাতে লেগেছে তার নাম কি 'enemy'?
        if hit_info.hit and hit_info.entity.name == 'enemy':
            impact = Entity(model='sphere', position=hit_info.point, scale=0.3, color=color.orange)
            destroy(impact, delay=0.1)
            
            if hit_info.entity in targets:
                targets.remove(hit_info.entity)
            
            destroy(hit_info.entity)
            
            score += 10
            score_text.text = f"Score: {score}"
            
            spawn_target()

# গেম ইঞ্জিন লুপ চালু
app.run()
