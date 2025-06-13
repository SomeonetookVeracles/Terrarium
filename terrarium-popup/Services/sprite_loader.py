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

        # Get pet type
        pet_type = pet_data.get('type', '').lower()
        if pet_type == "pet rock":
            pet_type = "rock"
        debug_log(f"Generating sprite for pet type: {pet_type}")

        # Define sprite paths
        base_path = os.path.join("Visuals", "Sprites", pet_type, "Patterns", "Base.gif")
        if not os.path.exists(base_path):
            debug_log(f"Base sprite not found: {base_path}", level="error")
            return False

        # Load base sprite
        base_sprite = Image.open(base_path)
        frames = []
        
        # Process each frame
        for frame in ImageSequence.Iterator(base_sprite):
            # Convert frame to RGBA
            frame = frame.convert('RGBA')
            
            # Apply base color if specified
            base_color = pet_data.get('base_color')
            if base_color:
                debug_log(f"Applying base color: {base_color}")
                # Convert hex color to RGB
                color = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
                # Create a color overlay
                overlay = Image.new('RGBA', frame.size, (*color, 128))
                frame = Image.alpha_composite(frame, overlay)

            # Apply pattern if specified
            pattern = pet_data.get('pattern')
            if pattern and pattern.lower() != "none":
                pattern_path = os.path.join("Visuals", "Sprites", pet_type, "Patterns", pattern)
                if os.path.exists(pattern_path):
                    pattern_sprite = Image.open(pattern_path)
                    if pattern_sprite.mode != 'RGBA':
                        pattern_sprite = pattern_sprite.convert('RGBA')
                    frame = Image.alpha_composite(frame, pattern_sprite)
                    debug_log(f"Applied pattern: {pattern}")
                else:
                    debug_log(f"Pattern not found: {pattern_path}", level="warning")

            frames.append(frame)

        # Save the final sprite with all frames
        output_path = os.path.join("Visuals", "currentPet.gif")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=base_sprite.info.get('duration', 100),
            loop=0,
            disposal=2
        )
        debug_log(f"Saved final sprite to: {output_path}")
        return True

    except Exception as e:
        debug_log(f"Error generating pet sprite: {str(e)}", level="error")
        import traceback
        debug_log(traceback.format_exc(), level="error")
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