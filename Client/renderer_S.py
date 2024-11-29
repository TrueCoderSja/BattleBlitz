import pygame
import pytmx
from pygame._sdl2 import Window

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
Window.from_display_module().maximize()

screen_width, screen_height=screen.get_width(), screen.get_height()

# Load your tilemap
tmx_data = pytmx.load_pygame("C:/Users/TrueC/MyProjects/CSET101_SEM1_PROJECT/extras/Tilemaps/test/test.tmx")  # Replace with your actual path

# Camera offsets
camera_x, camera_y = 0, 0

def render_tiles(tmx_data, camera_x, camera_y, screen):
    tile_width = tmx_data.tilewidth
    tile_height = tmx_data.tileheight

    # Calculate the visible area in tiles
    start_x = camera_x // tile_width
    start_y = camera_y // tile_height
    end_x = (camera_x + screen_width) // tile_width + 1
    end_y = (camera_y + screen_height) // tile_height + 1

    # Ensure we don't go out of bounds
    start_x = max(0, start_x)
    start_y = max(0, start_y)
    end_x = min(tmx_data.width, end_x)
    end_y = min(tmx_data.height, end_y)

    # Center offset to make the camera's top-left corner align with screen center
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Render the visible tiles
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'data'):
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile = layer.data[y][x]
                    if tile:  # If there is a tile at this position
                        # Calculate the position to draw the tile, adjusted by center offset
                        tile_x = x * tile_width - camera_x + center_x
                        tile_y = y * tile_height - camera_y + center_y
                        screen.blit(tmx_data.get_tile_image_by_gid(tile), (tile_x, tile_y))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Render tiles with camera centered
    render_tiles(tmx_data, camera_x, camera_y, screen)

    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()
