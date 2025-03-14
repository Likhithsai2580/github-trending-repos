import soundfile as sf
import numpy as np
from typing import List, Tuple
import os
import random

def find_best_audio_clips(file_path: str, segment_length: float) -> List[Tuple[float, float]]:
    """
    Analyze audio file and find the best segments based on energy.
    
    Args:
        file_path (str): Path to the audio file
        segment_length (float): Length of each segment in seconds
        
    Returns:
        List[Tuple[float, float]]: List of (start_time, end_time) tuples for best segments
    """
    try:
        # Load the audio file
        data, sr = sf.read(file_path)
        # Convert stereo to mono if necessary
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        
        # Calculate the number of samples per segment
        samples_per_segment = int(segment_length * sr)
        
        # Split audio into segments
        segments = []
        for i in range(0, len(data) - samples_per_segment, samples_per_segment):
            segment = data[i:i + samples_per_segment]
            # Calculate RMS energy of segment
            energy = np.sqrt(np.mean(segment ** 2))
            start_time = i / sr
            end_time = (i + samples_per_segment) / sr
            segments.append((start_time, end_time, energy))
        
        # Sort segments by energy
        segments.sort(key=lambda x: x[2], reverse=True)
        
        # Return top 5 clips or all if less than 5
        best_clips = [(clip[0], clip[1]) for clip in segments[:5]]
        return best_clips
    except Exception as e:
        raise Exception(f"Error processing audio: {str(e)}")

def create_random_clip(file_path: str, best_clips: List[Tuple[float, float]], output_path: str = "music.mp3"):
    """
    Select a random segment from the best clips and save it as an audio file.
    
    Args:
        file_path (str): Path to the original audio file
        best_clips (List[Tuple[float, float]]): List of best clips (start_time, end_time)
        output_path (str): Path to save the output audio file
    """
    try:
        # Load the audio file
        data, sr = sf.read(file_path)
        
        # Select random clip
        start_time, end_time = best_clips[np.random.randint(0, len(best_clips))]
        
        # Convert time to samples
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        # Extract the segment
        selected_segment = data[start_sample:end_sample]
        
        # Save the segment
        sf.write(output_path, selected_segment, sr)
    except Exception as e:
        raise Exception(f"Error creating clip: {str(e)}")

def random_songs() -> str:
    """
    Select a random music file from the music directory in the current working directory.
    
    Returns:
        str: Path to the randomly selected music file
    """
    try:
        music_dir = "music"
        # Get list of files from music directory
        music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        if not music_files:
            raise Exception("No music files found in music directory")
        
        # Select random file
        random_file = random.choice(music_files)
        return os.path.join(music_dir, random_file)
    except Exception as e:
        raise Exception(f"Error selecting random song: {str(e)}")

# Test the functions
if __name__=="__main__":
    file_path = random_songs()
    segment_length = 90
    best_clips = find_best_audio_clips(file_path, segment_length)
    print(f"Best clips: {best_clips}")
    create_random_clip(file_path, best_clips)