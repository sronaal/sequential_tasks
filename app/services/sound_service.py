import winsound
import os
import pathlib

class SoundService:
    def __init__(self):
        # Base path relative to main script execution usually, but reliable way is to find it relative to this file
        # or use a known project root. Assuming standard project structure:
        # sequential_tasks/
        #   app/services/sound.py
        #   sounds/start_play.wav
        
        # Go up two levels from app/services to get to sequential_tasks/
        current_dir = pathlib.Path(__file__).parent.resolve()
        project_root = current_dir.parent.parent
        self.sound_path = project_root / "sounds" / "start_play.wav"
        
    def play_start_sound(self):
        """Plays the start task sound if it exists."""
        if self.sound_path.exists():
            try:
                # SND_FILENAME: The sound parameter is the name of a wav file.
                # SND_ASYNC: The sound is played asynchronously and PlaySound returns immediately.
                winsound.PlaySound(str(self.sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Error playing sound: {e}")
        else:
            print(f"Sound file not found at: {self.sound_path}")

    def play_finish_sound(self):
        """Plays the finish task sound. Reuses start sound for now."""
        self.play_start_sound()
