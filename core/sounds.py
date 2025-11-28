"""
Sound manager for notification sounds using pygame.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Try to import pygame for sound
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Also try Windows-native sound
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


class SoundManager:
    """Manages alarm sounds for timer notifications."""
    
    def __init__(self, sounds_dir: Optional[str] = None):
        self._sounds_dir = sounds_dir or self._get_default_sounds_dir()
        self._current_sound = "chime"
        self._volume = 0.7
        self._sounds = {}
        
        if PYGAME_AVAILABLE:
            self._load_sounds()
    
    def _get_default_sounds_dir(self) -> str:
        """Get the default sounds directory."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_path, 'static', 'sounds')
    
    def _load_sounds(self):
        """Load available sound files."""
        if not os.path.exists(self._sounds_dir):
            return
        
        sound_files = {
            'chime': 'chime.wav',
            'bell': 'bell.wav',
            'digital': 'digital.wav',
            'gentle': 'gentle.wav'
        }
        
        for name, filename in sound_files.items():
            filepath = os.path.join(self._sounds_dir, filename)
            if os.path.exists(filepath):
                try:
                    self._sounds[name] = pygame.mixer.Sound(filepath)
                except Exception as e:
                    print(f"Failed to load sound {filename}: {e}")
    
    def set_sound(self, sound_name: str):
        """Set the current alarm sound."""
        self._current_sound = sound_name.lower()
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))
    
    def play_alarm(self):
        """Play the current alarm sound."""
        if PYGAME_AVAILABLE and self._current_sound in self._sounds:
            try:
                sound = self._sounds[self._current_sound]
                sound.set_volume(self._volume)
                sound.play()
                return
            except Exception as e:
                print(f"Failed to play sound: {e}")
        
        # Fallback to Windows beep
        if WINSOUND_AVAILABLE:
            try:
                # Play a pleasant ascending tone
                winsound.Beep(800, 200)
                winsound.Beep(1000, 200)
                winsound.Beep(1200, 300)
            except Exception:
                pass
    
    def play_break_end(self):
        """Play break end sound (gentler)."""
        if PYGAME_AVAILABLE and 'gentle' in self._sounds:
            try:
                sound = self._sounds['gentle']
                sound.set_volume(self._volume * 0.7)
                sound.play()
                return
            except Exception:
                pass
        
        # Fallback
        if WINSOUND_AVAILABLE:
            try:
                winsound.Beep(600, 150)
                winsound.Beep(800, 200)
            except Exception:
                pass
    
    def stop(self):
        """Stop any playing sounds."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.stop()
            except Exception:
                pass
