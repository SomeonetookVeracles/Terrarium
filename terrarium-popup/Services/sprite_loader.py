from PIL import Image, ImageSequence
import os
from config_helper import load_config, debug_log

def generate_current_pet_gif(pet=None):
    """
    Generates currentPet.gif by layering:
    - Base sprite (base.gif)
    - Pattern overlay (if any)
    - Addons (png overlays)
    Applies base color tint to the base sprite.

    pet: dict with keys 'type', 'base_color', 'pattern', 'addons'.
         If None, load from config.
    """
    if pet is None:
        config = load_config()
        pet = config.get("GAME", {}).get("active-pet")
        if not pet:
            debug_log("No active pet found in config.")
            return

    pet_type = pet.get("type")
    base_color = pet.get("base_color", "#FFFFFF")  # Hex color string
    pattern_name = pet.get("pattern")  # Filename or None
    addons = pet.get("addons", [])

    # Load pet types from config (to get sprite_path)
    config = load_config()
    pettypes = config.get("GAME", {}).get("pettypes", [])
    pet_meta = next((p for p in pettypes if p.get("name") == pet_type), None)
    if not pet_meta:
        debug_log(f"Pet type '{pet_type}' not found in pettypes.")
        return

    sprite_folder = pet_meta.get("sprite_path")
    if not sprite_folder:
        debug_log(f"No sprite_path set for pet type '{pet_type}'.")
        return

    base_path = os.path.join(sprite_folder, "patterns", "base.gif")
    if not os.path.exists(base_path):
        debug_log(f"Base sprite not found: {base_path}")
        return

    pattern_path = None
    if pattern_name and pattern_name.lower() != "none":
        pattern_path = os.path.join(sprite_folder, "patterns", pattern_name)
        if not os.path.exists(pattern_path):
            debug_log(f"Pattern file not found: {pattern_path}")
            pattern_path = None

    try:
        base = Image.open(base_path)
        frames = []

        # Convert base_color hex to RGB tuple
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        base_rgb = hex_to_rgb(base_color)

        for frame in ImageSequence.Iterator(base):
            frame = frame.convert("RGBA")

            # Apply base color tint: multiply pixel RGB by base color
            pixels = frame.load()
            r, g, b = base_rgb
            for y in range(frame.height):
                for x in range(frame.width):
                    pr, pg, pb, pa = pixels[x, y]
                    nr = int(pr * r / 255)
                    ng = int(pg * g / 255)
                    nb = int(pb * b / 255)
                    pixels[x, y] = (nr, ng, nb, pa)

            # Composite pattern if present
            if pattern_path:
                pattern_img = Image.open(pattern_path).convert("RGBA").resize(frame.size)
                frame.alpha_composite(pattern_img)

            # Composite addons
            for addon in addons:
                addon_path = os.path.join(sprite_folder, f"{addon}.png")
                if os.path.exists(addon_path):
                    overlay = Image.open(addon_path).convert("RGBA").resize(frame.size)
                    frame.alpha_composite(overlay)
                else:
                    debug_log(f"Addon missing: {addon_path}")

            frames.append(frame.copy())

        output_path = os.path.join("Visuals", "currentPet.gif")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=base.info.get("duration", 100),
            disposal=2
        )

        debug_log(f"Generated: {output_path}")

    except Exception as e:
        debug_log("Error during sprite generation:", str(e))


if __name__ == "__main__":
    generate_current_pet_gif()
