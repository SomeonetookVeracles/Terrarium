import os
from PIL import Image, ImageEnhance
from Services.debug_service import debug_log
from Services.pet_data_service import get_active_pet_data, get_pet_type_info

PLACEHOLDER_SPRITE = "Visuals/sprites/placeholder.png"
FRAME_SIZE = (200, 200)  # Standard frame size for the pet display

def ensure_placeholder_exists():
    """Ensure the placeholder sprite exists"""
    if not os.path.exists(PLACEHOLDER_SPRITE):
        try:
            # Create a simple placeholder image
            placeholder = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
            # Draw a simple shape
            for x in range(64):
                for y in range(64):
                    if (x - 32) ** 2 + (y - 32) ** 2 < 900:  # Circle
                        placeholder.putpixel((x, y), (200, 200, 200, 255))
            # Ensure directory exists
            os.makedirs(os.path.dirname(PLACEHOLDER_SPRITE), exist_ok=True)
            # Save placeholder
            placeholder.save(PLACEHOLDER_SPRITE)
            debug_log("Created placeholder sprite", level="info")
        except Exception as e:
            debug_log(f"Error creating placeholder sprite: {str(e)}", level="error")

def center_sprite(sprite):
    """Center the sprite in the frame"""
    try:
        # Create a new transparent frame
        frame = Image.new('RGBA', FRAME_SIZE, (255, 255, 255, 0))
        
        # Calculate center position
        x = (FRAME_SIZE[0] - sprite.size[0]) // 2
        y = (FRAME_SIZE[1] - sprite.size[1]) // 2
        
        # Paste sprite onto centered position
        frame.paste(sprite, (x, y), sprite)
        
        return frame
    except Exception as e:
        debug_log(f"Error centering sprite: {str(e)}", level="error")
        return sprite

def generate_current_pet_gif():
    """Generate a GIF for the current pet based on its type and state"""
    try:
        # Ensure placeholder exists
        ensure_placeholder_exists()

        # Get active pet data
        pet_data = get_active_pet_data()
        if not pet_data:
            debug_log("No active pet data found", level="error")
            return False

        # Get pet type info
        pet_type = pet_data.get('type')
        pet_info = get_pet_type_info(pet_type)
        if not pet_info:
            debug_log(f"Invalid pet type: {pet_type}", level="error")
            return False

        # Determine pet state based on metrics
        happiness = pet_data.get('happiness', 50)
        nourishment = pet_data.get('nourishment', 50)
        recreation = pet_data.get('recreation', 50)

        # Calculate overall state
        if happiness < 30 or nourishment < 30 or recreation < 30:
            state = "sad"
        elif happiness > 70 and nourishment > 70 and recreation > 70:
            state = "happy"
        else:
            state = "idle"

        # Load base sprite
        base_sprite_path = os.path.join("Visuals", "Sprites", pet_type, "patterns", "base.gif")
        if not os.path.exists(base_sprite_path):
            debug_log(f"Base sprite not found: {base_sprite_path}, using placeholder", level="warning")
            base_sprite_path = PLACEHOLDER_SPRITE

        base_sprite = Image.open(base_sprite_path)

        # Apply state modifications
        if state == "sad":
            # Darken the sprite
            enhancer = ImageEnhance.Brightness(base_sprite)
            base_sprite = enhancer.enhance(0.7)
        elif state == "happy":
            # Brighten the sprite
            enhancer = ImageEnhance.Brightness(base_sprite)
            base_sprite = enhancer.enhance(1.3)

        # Apply apparel if any
        equipped_apparel = pet_data.get('equipped_apparel', [])
        for apparel_id in equipped_apparel:
            if 'apparel' in pet_info and apparel_id in pet_info['apparel']:
                apparel_path = pet_info['apparel'][apparel_id]['sprite_path']
                if os.path.exists(apparel_path):
                    try:
                        apparel_sprite = Image.open(apparel_path)
                        # Ensure apparel sprite has alpha channel
                        if apparel_sprite.mode != 'RGBA':
                            apparel_sprite = apparel_sprite.convert('RGBA')
                        # Ensure base sprite has alpha channel
                        if base_sprite.mode != 'RGBA':
                            base_sprite = base_sprite.convert('RGBA')
                        # Composite apparel over base sprite
                        base_sprite = Image.alpha_composite(base_sprite, apparel_sprite)
                    except Exception as e:
                        debug_log(f"Error applying apparel {apparel_id}: {str(e)}", level="error")

        # Center the sprite in the frame
        base_sprite = center_sprite(base_sprite)

        # Save the final sprite
        output_path = os.path.join("Visuals", "currentPet.gif")
        base_sprite.save(output_path, save_all=True, append_images=[], duration=100, loop=0)
        debug_log(f"Generated pet sprite for {pet_type} in {state} state", level="info")
        return True

    except Exception as e:
        debug_log(f"Error generating pet sprite: {str(e)}", level="error")
        return False

def get_pet_sprite_path(pet_type, state="idle"):
    """Get the sprite path for a specific pet type and state"""
    try:
        # Ensure placeholder exists
        ensure_placeholder_exists()

        pet_info = get_pet_type_info(pet_type)
        if not pet_info:
            debug_log(f"Invalid pet type: {pet_type}", level="error")
            return PLACEHOLDER_SPRITE

        sprite_path = os.path.join("Visuals", "Sprites", pet_type, "patterns", "base.gif")
        if not os.path.exists(sprite_path):
            debug_log(f"Sprite not found: {sprite_path}, using placeholder", level="warning")
            return PLACEHOLDER_SPRITE

        return sprite_path
    except Exception as e:
        debug_log(f"Error getting sprite path: {str(e)}", level="error")
        return PLACEHOLDER_SPRITE 