import pygame
import os

# Initialize the mixer
pygame.mixer.init()

# Use the correct path
BEEP_PATH = os.path.join(os.path.dirname(__file__), "sounds", "beep-06.wav")

# Check if file exists
if os.path.exists(BEEP_PATH):
    pygame.mixer.music.load(BEEP_PATH)
    pygame.mixer.music.play()
    input("✅ Playing sound. Press Enter to exit...")
else:
    print("❌ Beep file not found at:", BEEP_PATH)