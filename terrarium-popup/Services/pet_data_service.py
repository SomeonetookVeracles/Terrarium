import json
import os
import time
from Services.debug_service import debug_log

# Define available pet types and their configurations
PET_TYPES = {
    "rock": {
        "name": "Rock",
        "base_stats": {
            "happiness": 50,
            "nourishment": 50,
            "recreation": 50
        },
        "sprite_path": "Visuals/Sprites/Rock/patterns/base.gif",
        "description": "A sturdy and reliable companion"
    },
    "slime": {
        "name": "Slime",
        "base_stats": {
            "happiness": 60,
            "nourishment": 40,
            "recreation": 60
        },
        "sprite_path": "Visuals/Sprites/Slime/patterns/base.gif",
        "description": "A bouncy and playful friend",
        "apparel": {
            "crown": {
                "name": "Royal Crown",
                "sprite_path": "Visuals/Sprites/Slime/patterns/crown.gif",
                "description": "A majestic crown for your slime"
            }
        }
    },
    "plant": {
        "name": "Plant",
        "base_stats": {
            "happiness": 40,
            "nourishment": 60,
            "recreation": 30
        },
        "sprite_path": "Visuals/Sprites/Plant/patterns/base.gif",
        "description": "A growing and nurturing friend"
    },
    "crystal": {
        "name": "Crystal",
        "base_stats": {
            "happiness": 60,
            "nourishment": 40,
            "recreation": 50
        },
        "sprite_path": "Visuals/Sprites/Crystal/patterns/base.gif",
        "description": "A sparkling and magical companion"
    }
}

def ensure_data_directory():
    """Ensure the Data directory exists"""
    if not os.path.exists('Data'):
        os.makedirs('Data')

def create_default_pet_data():
    """Create default pet data in config.json with a slime pet"""
    ensure_data_directory()
    default_pet = {
        "type": "slime",
        "name": "Slime",
        "description": "A bouncy and playful friend",
        "sprite_path": "Visuals/base.gif",
        "created_at": time.time(),
        "happiness": 60,
        "nourishment": 40,
        "recreation": 60,
        "equipped_apparel": []  # List of equipped apparel IDs
    }
    try:
        # Read existing config if it exists
        config = {}
        if os.path.exists('Data/config.json'):
            with open('Data/config.json', 'r') as f:
                config = json.load(f)
        
        # Update config with pet data
        config['active_pet'] = default_pet
        
        # Save updated config
        with open('Data/config.json', 'w') as f:
            json.dump(config, f, indent=4)
        debug_log("Created default pet data in config.json", level="info")
        return default_pet
    except Exception as e:
        debug_log(f"Error creating default pet data: {str(e)}", level="error")
        return None

def get_active_pet_data():
    """Get the data for the currently active pet from config.json"""
    try:
        # Check if the config file exists
        if not os.path.exists('Data/config.json'):
            return create_default_pet_data()

        # Read the config file
        with open('Data/config.json', 'r') as f:
            config = json.load(f)

        # Check if there's an active pet
        if not config or 'active_pet' not in config:
            debug_log("No active pet found in config, creating default", level="info")
            return create_default_pet_data()

        # Get the active pet data
        active_pet = config['active_pet']
        
        # If pet type exists, merge with base configuration
        if 'type' in active_pet and active_pet['type'] in PET_TYPES:
            base_config = PET_TYPES[active_pet['type']]
            # Merge base stats with current stats
            for stat, value in base_config['base_stats'].items():
                if stat not in active_pet:
                    active_pet[stat] = value
            # Add pet type info
            active_pet['name'] = base_config['name']
            active_pet['description'] = base_config['description']
            active_pet['sprite_path'] = base_config['sprite_path']
            # Initialize equipped_apparel if not present
            if 'equipped_apparel' not in active_pet:
                active_pet['equipped_apparel'] = []

        return active_pet
    except Exception as e:
        debug_log(f"Error reading pet data from config: {str(e)}", level="error")
        return create_default_pet_data()

def get_metric_names():
    """Get the list of metric names for the pet"""
    return ["Happiness", "Nourishment", "Recreation"]

def get_metric_values(pet_data):
    """Get the current values for all metrics"""
    if not pet_data:
        return {name: 0 for name in get_metric_names()}
    
    return {
        "Happiness": pet_data.get('happiness', 0),
        "Nourishment": pet_data.get('nourishment', 0),
        "Recreation": pet_data.get('recreation', 0)
    }

def update_pet_metric(pet_data, metric_name, value):
    """Update a specific metric for the pet in config.json"""
    if not pet_data:
        return None
    
    # Convert metric name to lowercase for storage
    metric_key = metric_name.lower()
    
    # Update the metric value
    pet_data[metric_key] = max(0, min(100, value))
    
    # Save the updated data
    try:
        ensure_data_directory()
        # Read existing config
        config = {}
        if os.path.exists('Data/config.json'):
            with open('Data/config.json', 'r') as f:
                config = json.load(f)
        
        # Update pet data in config
        config['active_pet'] = pet_data
        
        # Save updated config
        with open('Data/config.json', 'w') as f:
            json.dump(config, f, indent=4)
            
        return pet_data
    except Exception as e:
        debug_log(f"Error updating pet metric in config: {str(e)}", level="error")
        return None

def create_new_pet(pet_type):
    """Create a new pet of the specified type in config.json"""
    if pet_type not in PET_TYPES:
        debug_log(f"Invalid pet type: {pet_type}", level="error")
        return None

    try:
        # Get base configuration for the pet type
        base_config = PET_TYPES[pet_type]
        
        # Create new pet data
        new_pet = {
            "type": pet_type,
            "name": base_config["name"],
            "description": base_config["description"],
            "sprite_path": base_config["sprite_path"],
            "created_at": time.time(),
            "equipped_apparel": []  # Initialize empty apparel list
        }
        
        # Add base stats
        new_pet.update(base_config["base_stats"])
        
        # Save to config.json
        ensure_data_directory()
        config = {}
        if os.path.exists('Data/config.json'):
            with open('Data/config.json', 'r') as f:
                config = json.load(f)
        
        config['active_pet'] = new_pet
        
        with open('Data/config.json', 'w') as f:
            json.dump(config, f, indent=4)
            
        return new_pet
    except Exception as e:
        debug_log(f"Error creating new pet in config: {str(e)}", level="error")
        return None

def get_available_pet_types():
    """Get list of available pet types"""
    return list(PET_TYPES.keys())

def get_pet_type_info(pet_type):
    """Get information about a specific pet type"""
    return PET_TYPES.get(pet_type)

def get_available_apparel(pet_type):
    """Get available apparel for a specific pet type"""
    if pet_type not in PET_TYPES:
        return {}
    return PET_TYPES[pet_type].get('apparel', {})

def equip_apparel(pet_data, apparel_id):
    """Equip an apparel item to the pet"""
    if not pet_data or 'type' not in pet_data:
        return None
    
    pet_type = pet_data['type']
    available_apparel = get_available_apparel(pet_type)
    
    if apparel_id not in available_apparel:
        debug_log(f"Invalid apparel ID: {apparel_id}", level="error")
        return None
    
    # Initialize equipped_apparel if not present
    if 'equipped_apparel' not in pet_data:
        pet_data['equipped_apparel'] = []
    
    # Add apparel to equipped list if not already equipped
    if apparel_id not in pet_data['equipped_apparel']:
        pet_data['equipped_apparel'].append(apparel_id)
        
        # Update config file
        try:
            ensure_data_directory()
            config = {}
            if os.path.exists('Data/config.json'):
                with open('Data/config.json', 'r') as f:
                    config = json.load(f)
            
            config['active_pet'] = pet_data
            
            with open('Data/config.json', 'w') as f:
                json.dump(config, f, indent=4)
                
            return pet_data
        except Exception as e:
            debug_log(f"Error equipping apparel: {str(e)}", level="error")
            return None
    
    return pet_data

def unequip_apparel(pet_data, apparel_id):
    """Unequip an apparel item from the pet"""
    if not pet_data or 'equipped_apparel' not in pet_data:
        return None
    
    if apparel_id in pet_data['equipped_apparel']:
        pet_data['equipped_apparel'].remove(apparel_id)
        
        # Update config file
        try:
            ensure_data_directory()
            config = {}
            if os.path.exists('Data/config.json'):
                with open('Data/config.json', 'r') as f:
                    config = json.load(f)
            
            config['active_pet'] = pet_data
            
            with open('Data/config.json', 'w') as f:
                json.dump(config, f, indent=4)
                
            return pet_data
        except Exception as e:
            debug_log(f"Error unequipping apparel: {str(e)}", level="error")
            return None
    
    return pet_data 