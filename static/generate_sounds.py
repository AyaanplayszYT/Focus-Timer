"""
Generate simple notification sounds using wave module.
These are basic sine wave tones as placeholders.
"""

import wave
import struct
import math
import os


def generate_tone(filename: str, frequencies: list, durations: list, 
                  sample_rate: int = 44100, amplitude: float = 0.5):
    """Generate a WAV file with multiple tones."""
    frames = []
    
    for freq, duration in zip(frequencies, durations):
        num_samples = int(sample_rate * duration)
        
        for i in range(num_samples):
            # Sine wave with envelope
            t = i / sample_rate
            envelope = min(1.0, min(i / 500, (num_samples - i) / 500))  # Fade in/out
            value = amplitude * envelope * math.sin(2 * math.pi * freq * t)
            
            # Convert to 16-bit integer
            packed = struct.pack('h', int(value * 32767))
            frames.append(packed)
    
    # Write WAV file
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))


def create_sounds(output_dir: str):
    """Create all notification sounds."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Chime - pleasant ascending tones
    generate_tone(
        os.path.join(output_dir, 'chime.wav'),
        frequencies=[523.25, 659.25, 783.99, 1046.50],  # C5, E5, G5, C6
        durations=[0.15, 0.15, 0.15, 0.4],
        amplitude=0.4
    )
    
    # Bell - single resonant tone
    generate_tone(
        os.path.join(output_dir, 'bell.wav'),
        frequencies=[880, 880, 440],
        durations=[0.3, 0.2, 0.5],
        amplitude=0.5
    )
    
    # Digital - short beeps
    generate_tone(
        os.path.join(output_dir, 'digital.wav'),
        frequencies=[1000, 0, 1000, 0, 1200],
        durations=[0.1, 0.05, 0.1, 0.05, 0.2],
        amplitude=0.4
    )
    
    # Gentle - soft low tone
    generate_tone(
        os.path.join(output_dir, 'gentle.wav'),
        frequencies=[392, 440, 523.25],  # G4, A4, C5
        durations=[0.3, 0.3, 0.5],
        amplitude=0.3
    )
    
    print(f"Created sounds in {output_dir}")


if __name__ == "__main__":
    # Get the static/sounds directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sounds_dir = os.path.join(script_dir, 'sounds')
    create_sounds(sounds_dir)
