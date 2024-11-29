import pygame
from pygame._sdl2 import Window
from pytmx import load_pygame
import os
from audio import SoundManager

# Global Variables
player_icon = None
player_icon_rect = None
uniqueID = 0
positions = {}
bulletPositions = {}
isInitialized = False
toExit=False

inGraveMode = False
blink_state = False
blink_timer = 0

# Callbacks
update_cb = None
close_cb = None

# Rendering and Game Data
tmx_data = None
screen = None
clock = None
font = None

tileWidth, tileHeight = 0, 0
mapWidth, mapHeight = 0, 0
absWidth, absHeight = 0, 0
camX, camY = 0, 0

screenWidth, screenHeight = 640, 480
player_width, player_height = 0, 0
playerXOffset, playerYOffset = 0, 0
bulletXOffset, bulletYOffset = 0, 0
camXOffset, camYOffset = 0, 0

player_icons = {}
bullet_icons = {}

explosion_queue = []

def init(uid, mapPath, update_callback, close_callback):
    global update_cb
    global close_cb
    update_cb=update_callback
    close_cb=close_callback

    global tmx_data
    global screen
    global clock
    global tileWidth, tileHeight, mapWidth, mapHeight, absWidth, absHeight, camX, camY
    global uniqueID
    global player_icons, bullet_icons
    global screenWidth, screenHeight
    global player_width, player_height, playerXOffset, playerYOffset
    global bulletXOffset, bulletYOffset
    global camXOffset, camYOffset

    global font

    uniqueID = uid
    pygame.init()
    pygame.font.init()

    font = pygame.font.Font(None, 24) 

    # Find the TMX file in the directory
    tmx_file = None
    for file in os.listdir(mapPath):
        if file.endswith(".tmx"):
            tmx_file = os.path.join(mapPath, file)
            break
    
    if not tmx_file:
        raise FileNotFoundError(f"No .tmx file found in directory: {mapPath}")

    # Load player icons
    player_base_icon = pygame.image.load("tank.png")
    player_icons = {
        0: player_base_icon,
        1: pygame.transform.rotate(player_base_icon, 270),
        2: pygame.transform.rotate(player_base_icon, 180),
        3: pygame.transform.rotate(player_base_icon, 90)
    }

    #Load audios
    global explosionAudio, hitAudio
    explosionAudio=SoundManager(SoundManager.EXPLOSION_AUDIO)
    hitAudio=SoundManager(SoundManager.HIT_AUDIO)

    player_width = player_base_icon.get_width()
    playerXOffset=player_width//2
    player_height = player_base_icon.get_height()
    playerYOffset=player_width//2

    bullet_base_icon=pygame.image.load("bullet.png");
    bullet_icons={
        0: pygame.transform.rotate(bullet_base_icon, 90),
        1: bullet_base_icon,
        2: pygame.transform.rotate(bullet_base_icon, 270),
        3: pygame.transform.rotate(bullet_base_icon, 180)
    }

    bulletXOffset=bullet_base_icon.get_width()//2
    bulletYOffset=bullet_base_icon.get_height()//2


    camXOffset, camYOffset = player_width // 2, player_height // 2

    # Initialize the screen
    screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
    screenWidth, screenHeight = screen.get_width(), screen.get_height()

    # Load TMX map data
    tmx_data = load_pygame(tmx_file)
    tileWidth, tileHeight = tmx_data.tilewidth, tmx_data.tileheight
    mapWidth, mapHeight = tmx_data.width, tmx_data.height
    absWidth, absHeight = tileWidth * mapWidth, tileHeight * mapHeight

    print(f"Map Dimensions: {mapWidth} x {mapHeight}")

    #Load explosion animation
    global explosion_frames
    global explosion_frame_width, explosion_frame_height
    explosion_frame_width, explosion_frame_height=96,96
    spritesheet = pygame.image.load("assets/explosion.png").convert_alpha()
    frame_width, frame_height = 96, 96
    explosion_frames = [
        spritesheet.subsurface((i * frame_width, 0, frame_width, frame_height))
        for i in range(spritesheet.get_width() // frame_width)
    ]

    camX, camY = 0, 0
    clock = pygame.time.Clock()

    global isInitialized
    isInitialized=True

    Window.from_display_module().maximize()

def render():
    global toExit
    global running, inGraveMode
    if toExit:
        running=False
        inGraveMode=False
        pygame.quit()
        return
        
    global positions, bulletPostions
    global screenWidth, screenHeight
    global tileWidth, tileHeight
    global absWidth, absHeight
    global camX, camY
    global player_width, player_height, playerXOffset, playerYOffset
    global font

    
    global explosion_queue
    global explosion_frames
    global explosion_frame_width, explosion_frame_height

    global explosionAudio, hitAudio

    centerX=screenWidth//2
    centerY=screenHeight//2

    startX=max(0, round(camX-centerX))
    startY=max(0, round(camY-centerY))

    baseX=centerX-camX if camX<centerX else 0
    baseY=centerY-camY if camY<centerY else 0
    
    tileStartX=startX//tileWidth
    tileStartY=startY//tileWidth
    tileXOffset=startX%tileWidth

    endX=min(absWidth, startX+screenWidth-baseX)
    endY=min(absHeight, startY+screenHeight-baseY)

    tileEndX = min(mapWidth, endX // tileWidth + 1)
    tileEndY = min(mapHeight, endY // tileHeight + 1)
    tileYOffset=startY%tileHeight

    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'data'):
            for y in range(tileStartY, tileEndY):
                for x in range(tileStartX, tileEndX):
                    tile=layer.data[y][x]
                    if tile:
                        tileX=baseX+(x-tileStartX)*tileWidth-tileXOffset
                        tileY=baseY+(y-tileStartY)*tileHeight-tileYOffset
                        screen.blit(tmx_data.get_tile_image_by_gid(tile), (tileX, tileY))

    for uid,pos in positions.items():
        dx,dy=pos["xPos"], pos["yPos"]
        if (dx + playerXOffset >= startX and dx - playerXOffset <= endX and 
            dy + playerYOffset >= startY and dy - playerYOffset <= endY):
            # Render the player icon
            player_screen_x = dx - startX + baseX - playerXOffset
            player_screen_y = dy - startY + baseY - playerYOffset
            screen.blit(player_icons[pos["direction"]], (player_screen_x, player_screen_y))

            # Display player health above the player
            maxHealth = 5
            player_health = pos["health"]
            health_bar_width = player_width
            health_bar_height = 5
            health_ratio = player_health / maxHealth
            health_bar_x = player_screen_x
            health_bar_y = player_screen_y - health_bar_height - 5  # Above the player icon

            # Draw the white border for the health bar
            pygame.draw.rect(screen, (255, 255, 255), 
                            (health_bar_x - 1, health_bar_y - 1, 
                            health_bar_width + 2, health_bar_height + 2))  # Border slightly larger
            # Draw the red background for the health bar
            pygame.draw.rect(screen, (255, 0, 0), 
                            (health_bar_x, health_bar_y, 
                            health_bar_width, health_bar_height))  # Red background
            # Draw the green foreground proportional to health
            pygame.draw.rect(screen, (0, 255, 0), 
                            (health_bar_x, health_bar_y, 
                            health_bar_width * health_ratio, health_bar_height))  # Green foreground

            # Display player name below the player
            player_name = pos["playername"]
            text_surface = font.render(player_name, True, (255, 255, 255))  # White text
            text_x = player_screen_x + player_width // 2 - text_surface.get_width() // 2  # Center text horizontally
            text_y = player_screen_y + player_height + 5  # Below the player icon
            screen.blit(text_surface, (text_x, text_y))

    for pos in bulletPostions:
        dx,dy=pos["xPos"], pos["yPos"]
        direction=pos["direction"]
        
        if "collosion" in pos:
            collosionType=pos["collosion"]
            if collosionType=="exploded":
                explosionX=pos["xPos"]
                explosionY=pos["yPos"]
                if direction==0:
                    explosionX-=explosion_frame_width//2
                    explosionY-=(bulletXOffset+explosion_frame_height//2)
                elif direction==2:
                    explosionX-=explosion_frame_width//2
                    explosionY+=(bulletXOffset-explosion_frame_height//2)
                elif direction==3:
                    explosionX-=(bulletXOffset+explosion_frame_width//2)
                    explosionY-=explosion_frame_height//2
                elif direction==1:
                    explosionX+=(bulletXOffset-explosion_frame_width//2)
                    explosionY-=explosion_frame_height//2
                explosion_queue.append({
                    "xPos": explosionX,
                    "yPos": explosionY,
                    "frame": 0,
                    "timer": 0
                })
                explosionAudio.playOnce()
            elif collosionType=="hit":
                hitAudio.playOnce()
        else:
            if direction==0 or direction==2:
                if dy+bulletXOffset >= startY and dy-bulletXOffset <=endY:
                    screen.blit(bullet_icons[direction], (dx-startX+baseX-bulletYOffset, dy-startY+baseY-bulletXOffset))
            elif direction==1 or direction==3:
                if dx+bulletXOffset >= startX and dx-bulletXOffset <= endX:
                    screen.blit(bullet_icons[direction], (dx-startX+baseX-bulletXOffset, dy-startY+baseY-bulletYOffset))

    #Draw bullet explosions
    update_explosions()
    

    for explosion in explosion_queue:
        frame = explosion_frames[explosion["frame"]]
        dx, dy=explosion["xPos"], explosion["yPos"]
        screen.blit(frame, (dx-startX+baseX, dy-startY+baseY))
            
    global blink_state
    if inGraveMode:
        if blink_state:  # Only display when in grave mode and state is visible
            # Line 1: "You have been shot by {killer}."
            line1 = f"You have been shot ."
            line1_surface = font.render(line1, True, (255, 0, 0))  # Blinking color (e.g., red)
            line1_x = (screenWidth - line1_surface.get_width()) // 2
            line1_y = screenHeight - 90  # Starting point for the first line

            # Line 2: "You can only explore but cannot play."
            line2 = "You can only explore but cannot play."
            line2_surface = font.render(line2, True, (255, 0, 0))  # Same blinking color
            line2_x = (screenWidth - line2_surface.get_width()) // 2
            line2_y = line1_y + line1_surface.get_height() + 5

            # Line 3: "Press ESC to exit."
            line3 = "Press ESC to exit."
            line3_surface = font.render(line3, True, (255, 0, 0))  # Same blinking color
            line3_x = (screenWidth - line3_surface.get_width()) // 2
            line3_y = line2_y + line2_surface.get_height() + 5

            # Blit each line to the screen
            screen.blit(line1_surface, (line1_x, line1_y))
            screen.blit(line2_surface, (line2_x, line2_y))
            screen.blit(line3_surface, (line3_x, line3_y))
        
        update_blink_timer()

def setPositions(postions):
    global camX, camY
    global uniqueID
    global positions
    global bulletPostions

    players=postions["players"]
    bulletPostions=postions["bullets"]
    positions=players

    if uniqueID in players:
        camX=players[uniqueID]["xPos"]
        camY=players[uniqueID]["yPos"]
    else:
        pass

def updateloop():
    global update_cb

    global running, camX, camY, screenWidth, screenHeight
    global playerXOffset, playerYOffset
    global inGraveMode
    running=True
    while running:
        dt=clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type==pygame.VIDEORESIZE:
                screenWidth=screen.get_width()
                screenHeight=screen.get_height()

                # Handle keydown events for one-time actions
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_KP_ENTER:
                    update_cb(5)

        keys=pygame.key.get_pressed()
        if keys[pygame.K_UP]:
                update_cb(0)
        if keys[pygame.K_DOWN]:
            if camY<absHeight:
                update_cb(2)
        if keys[pygame.K_LEFT]:
            if camX>0:
                update_cb(3)
        if keys[pygame.K_RIGHT]:
            if camX<absWidth:
                update_cb(1)
            

        screen.fill((0,0,0))

        render()
        pygame.display.flip()

    global inGraveMode
    if inGraveMode:
        graveModeloop()

def graveModeloop():
    global running, camX, camY, screenWidth, screenHeight
    global playerXOffset, playerYOffset
    global inGraveMode
    speed=15
    running=True
    while inGraveMode:
        dt=clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type==pygame.VIDEORESIZE:
                screenWidth=screen.get_width()
                screenHeight=screen.get_height()

        keys=pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            if camY>0:
                camY-=speed
        if keys[pygame.K_DOWN]:
            if camY<absHeight:
                camY+=speed
        if keys[pygame.K_LEFT]:
            if camX>0:
                camX-=speed
        if keys[pygame.K_RIGHT]:
            if camX<absWidth:
                camX+=speed
        if keys[pygame.K_ESCAPE]:
            exitApp()
            

        screen.fill((0,0,0))

        render()
        pygame.display.flip()

def exitApp():
    global toExit
    toExit=True


def enableGraveMode():
    print("Grave Mode activated")
    global inGraveMode, running
    inGraveMode=True
    running=False

def update_blink_timer():
    global blink_timer, blink_state
    blink_timer += 1
    if blink_timer > 30:  # Toggle every 30 frames (adjust for desired speed)
        blink_state = not blink_state
        blink_timer = 0

def update_explosions():
    global explosion_queue
    animation_speed = 5  # Speed of the explosion animation (number of frames before advancing)

    # Iterate over the explosions and update their animation
    for explosion in explosion_queue[:]:
        explosion["timer"] += 1
        if explosion["timer"] >= animation_speed:
            explosion["timer"] = 0
            explosion["frame"] += 1
            if explosion["frame"] >= len(explosion_frames):  # If animation finishes
                explosion_queue.remove(explosion)  # Remove explosion from the queue
