import os
from PIL import Image, ImageSequence
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
            debug_log("Created placeholder sprite")
        except Exception as e:
            debug_log(f"Error creating placeholder sprite: {str(e)}", level="error")

def normalize_pet_type(pet_type):
    """Normalize pet type name to match file structure"""
    pet_type = pet_type.lower()
    if pet_type == "pet rock":
        return "rock"
    return pet_type

def find_sprite_file(base_path, filename):
    """Find a sprite file with case-insensitive matching"""
    if os.path.exists(os.path.join(base_path, filename)):
        return os.path.join(base_path, filename)
    if os.path.exists(os.path.join(base_path, filename.lower())):
        return os.path.join(base_path, filename.lower())
    if os.path.exists(os.path.join(base_path, filename.upper())):
        return os.path.join(base_path, filename.upper())
    return None

def generate_current_pet_gif():
    """Generate a GIF for the current pet based on its state"""
    try:
        # Get current pet data
        pet_data = get_active_pet_data()
        
        # Get the base sprite path
        base_sprite_path = os.path.join("Assets", "Sprites", f"{pet_data['type']}.gif")
        
        # Check if the base sprite exists
        if not os.path.exists(base_sprite_path):
            debug_log(f"Base sprite not found: {base_sprite_path}", level="error")
            return None
            
        # Load the base sprite
        base_sprite = Image.open(base_sprite_path)
        
        # Create a new GIF with the same duration and loop settings
        frames = []
        durations = []
        
        # Process each frame
        for frame in ImageSequence.Iterator(base_sprite):
            # Convert to RGBA if not already
            frame = frame.convert('RGBA')
            
            # Get frame duration
            try:
                duration = frame.info['duration']
            except KeyError:
                duration = 100  # Default duration if not specified
                
            # Apply any state-based modifications here
            # For example, you could tint the sprite based on mood
            
            # Add the frame
            frames.append(frame)
            durations.append(duration)
            
        # Save the new GIF
        output_path = os.path.join("Assets", "Sprites", "current_pet.gif")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=False
        )
        
        return output_path
        
    except Exception as e:
        debug_log(f"Error generating pet GIF: {str(e)}", level="error")
        return None

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