# test_widget.py
import sys
import pygame
from PyQt5.QtCore import QTimer, Qt, QRect, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPixmap, QMovie
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QApplication, QFrame, QPushButton
)
from config_helper import load_config, save_config, debug_log
from Services.data_catcher import get_metric_names, get_metric_values, deteriorate_metrics
from Services.sprite_loader_service import generate_current_pet_gif
import os
from PIL import Image, ImageSequence
from Services.pet_data_service import get_active_pet_data, update_pet_metric
from Services.Hakatime_service import WakatimeService
import traceback


def pil_to_pixmap(pil_image):
    if pil_image.mode == "RGB":
        qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format_RGB888)
    else:
        qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimage)


class testWidget(QWidget):
    pet_updated = pyqtSignal()
    
    def __init__(self, window_width, window_height):
        super().__init__()
        self.window_width = window_width
        self.window_height = window_height
        self.init_ui()
        
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_sprite)
        self.current_frame = 0
        self.sprite_frames = []
        
        self.load_sprite()

    def init_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Egg container
        self.egg_container = QLabel()
        self.egg_container.setAlignment(Qt.AlignCenter)
        self.egg_container.setMinimumSize(256, 256)
        self.egg_container.setMaximumSize(256, 256)
        
        # Load egg frame
        egg_frame_path = os.path.join("Visuals", "Sprites", "Egg.png")
        if os.path.exists(egg_frame_path):
            self.frame_image = QImage(egg_frame_path)
            self.egg_container.setPixmap(QPixmap.fromImage(self.frame_image))
        else:
            debug_log("Egg frame not found", level="error")
            self.frame_image = None
        
        # Metrics container
        metrics_container = QWidget()
        metrics_layout = QVBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(10, 10, 10, 10)
        metrics_layout.setSpacing(5)
        
        # Create metric bars
        self.joy_bar = self.create_metric_bar("Joy")
        self.nourishment_bar = self.create_metric_bar("Nourishment")
        self.recreation_bar = self.create_metric_bar("Recreation")
        
        # Add metrics to container
        metrics_layout.addWidget(self.joy_bar)
        metrics_layout.addWidget(self.nourishment_bar)
        metrics_layout.addWidget(self.recreation_bar)
        
        # Add widgets to main layout
        layout.addWidget(self.egg_container, alignment=Qt.AlignCenter)
        layout.addWidget(metrics_container)
        
        # Add debug button if in dev mode
        config = load_config()
        if config.get("GLOBALS", {}).get("DEVMODE", False):
            debug_layout = QHBoxLayout()
            
            # Add deterioration simulation button
            deteriorate_btn = QPushButton("Simulate Deterioration")
            deteriorate_btn.clicked.connect(self.simulate_deterioration)
            debug_layout.addWidget(deteriorate_btn)
            
            layout.addLayout(debug_layout)
        
        self.setLayout(layout)

    def create_metric_bar(self, name):
        """Create a metric progress bar"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(name)
        label.setFixedWidth(100)
        
        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(100)
        bar.setValue(50)  # Default value
        
        layout.addWidget(label)
        layout.addWidget(bar)
        
        return container

    def load_sprite(self):
        """Load and layer the pet sprites"""
        try:
            debug_log("Loading pet sprites...")
            
            # Get current pet data
            config = load_config()
            pet_data = config.get("GAME", {}).get("active-pet")
            if not pet_data:
                debug_log("No active pet found", level="error")
                return
                
            debug_log(f"Loading sprites for pet: {pet_data.get('type')}")
            
            # Get pet type and normalize it
            pet_type = pet_data.get('type', '').lower()
            if pet_type == "pet rock":
                pet_type = "rock"
            
            # Define sprite paths
            base_path = os.path.join("Visuals", "Sprites", pet_type, "Patterns", "Base.gif")
            if not os.path.exists(base_path):
                debug_log(f"Base sprite not found: {base_path}", level="error")
                return
            
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
                        # Resize pattern to match base sprite
                        pattern_sprite = pattern_sprite.resize(frame.size, Image.Resampling.LANCZOS)
                        frame = Image.alpha_composite(frame, pattern_sprite)
                        debug_log(f"Applied pattern: {pattern}")
                    else:
                        debug_log(f"Pattern not found: {pattern_path}", level="warning")
                
                # Scale the frame to fit inside the egg
                egg_size = (200, 200)  # Size of the egg frame
                frame.thumbnail(egg_size, Image.Resampling.LANCZOS)
                
                # Create a new transparent image the size of the egg
                egg_frame = Image.new('RGBA', egg_size, (0, 0, 0, 0))
                
                # Calculate center position with offset
                x = (egg_size[0] - frame.width) // 2 + 28  # Move right by 28px
                y = (egg_size[1] - frame.height) // 2 + 28  # Move down by 28px
                
                # Paste the frame onto the egg frame
                egg_frame.paste(frame, (x, y), frame)
                
                # Apply accessories if any
                accessories = pet_data.get('accessories', [])
                for accessory in accessories:
                    if accessory and accessory.lower() != "none":
                        accessory_path = os.path.join("Visuals", "Sprites", pet_type, "Patterns", accessory)
                        if os.path.exists(accessory_path):
                            accessory_sprite = Image.open(accessory_path)
                            if accessory_sprite.mode != 'RGBA':
                                accessory_sprite = accessory_sprite.convert('RGBA')
                            # Resize accessory to match base sprite
                            accessory_sprite = accessory_sprite.resize(frame.size, Image.Resampling.LANCZOS)
                            # Paste accessory at the same position as the base sprite
                            egg_frame.paste(accessory_sprite, (x, y), accessory_sprite)
                            debug_log(f"Applied accessory: {accessory}")
                        else:
                            debug_log(f"Accessory not found: {accessory_path}", level="warning")
                
                # Convert to QPixmap
                pixmap = pil_to_pixmap(egg_frame)
                frames.append(pixmap)
            
            if not frames:
                debug_log("No frames found in sprite", level="error")
                return
            
            # Store frames and start animation
            self.sprite_frames = frames
            self.current_frame = 0
            self.frame_timer.start(base_sprite.info.get('duration', 100))
            
            # Update the display
            self.update_sprite()
            debug_log("Sprite loaded successfully")
            
            # Update metrics
            self.update_metrics(pet_data)
            
        except Exception as e:
            debug_log(f"Error loading sprite: {str(e)}", level="error")
            traceback.print_exc()

    def update_sprite(self):
        """Update the sprite display"""
        if not self.sprite_frames:
            return
            
        # Get current frame
        frame = self.sprite_frames[self.current_frame]
        
        # Create a new pixmap for the egg with the sprite
        egg_with_sprite = QPixmap(self.egg_container.size())
        egg_with_sprite.fill(Qt.transparent)
        
        # Draw the egg frame
        painter = QPainter(egg_with_sprite)
        if self.frame_image:
            # Scale the egg frame to match the container size
            scaled_frame = self.frame_image.scaled(
                self.egg_container.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            # Center the egg frame
            x = (self.egg_container.width() - scaled_frame.width()) // 2
            y = (self.egg_container.height() - scaled_frame.height()) // 2
            painter.drawImage(x, y, scaled_frame)
        
        # Draw the sprite frame
        painter.drawPixmap(0, 0, frame)
        painter.end()
        
        # Update the display
        self.egg_container.setPixmap(egg_with_sprite)
        
        # Move to next frame
        self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)

    def update_metrics(self, pet_data):
        """Update the metric bars based on pet data"""
        try:
            # Get metric values
            joy = pet_data.get('joy', 50)
            nourishment = pet_data.get('nourishment', 50)
            recreation = pet_data.get('recreation', 50)
            
            # Update bars
            self.joy_bar.findChild(QProgressBar).setValue(joy)
            self.nourishment_bar.findChild(QProgressBar).setValue(nourishment)
            self.recreation_bar.findChild(QProgressBar).setValue(recreation)
            
        except Exception as e:
            debug_log(f"Error updating metrics: {str(e)}", level="error")
            traceback.print_exc()

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Update sprite display when window is resized
        self.update_sprite()

    def __del__(self):
        pygame.quit()

    def simulate_deterioration(self):
        """Simulate deterioration for testing"""
        try:
            config = load_config()
            current_nourishment = config.get("GAME", {}).get("active-pet", {}).get("nourishment", 50)
            new_nourishment = max(current_nourishment - 20, 0)  # Reduce by 20%
            
            # Update config
            if "active-pet" in config.get("GAME", {}):
                config["GAME"]["active-pet"]["nourishment"] = new_nourishment
                save_config(config)
                
            debug_log(f"Simulated deterioration - Updated nourishment: {current_nourishment} -> {new_nourishment}")
            
            # Update display
            self.refresh_pet()
            
        except Exception as e:
            debug_log(f"Error simulating deterioration: {str(e)}", level="error")
            traceback.print_exc()

    def refresh_pet(self):
        """Refresh the pet display with current data"""
        try:
            # Reload sprite
            self.load_sprite()
            
            # Update metric bars
            self.update_metric_bars()
            
        except Exception as e:
            debug_log(f"Error refreshing pet: {str(e)}", level="error")
            traceback.print_exc()
            
    def update_metric_bars(self):
        """Update the metric bars with current values"""
        try:
            config = load_config()
            pet_data = config.get("GAME", {}).get("active-pet", {})
            
            # Update each metric bar
            self.joy_bar.setValue(pet_data.get("joy", 50))
            self.nourishment_bar.setValue(pet_data.get("nourishment", 50))
            self.recreation_bar.setValue(pet_data.get("recreation", 50))
            
        except Exception as e:
            debug_log(f"Error updating metric bars: {str(e)}", level="error")
            traceback.print_exc()


class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get screen dimensions
        screen = QApplication.primaryScreen().geometry()
        taskbar_height = 40  # Approximate taskbar height
        
        # Calculate window size and position
        window_width = 400
        window_height = 300
        window_x = screen.width() - window_width - 20  # 20px margin from right
        window_y = screen.height() - window_height - taskbar_height - 20  # 20px margin from bottom
        
        # Set window geometry
        self.setGeometry(window_x, window_y, window_width, window_height)
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create test widget
        self.test_widget = testWidget(window_width, window_height)
        self.layout.addWidget(self.test_widget)
        
        # Set the layout
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainPage()
    main.show()
    sys.exit(app.exec_())