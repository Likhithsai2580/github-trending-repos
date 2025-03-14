import requests
import json
import edge_tts
import asyncio
from moviepy.editor import (
    VideoFileClip, ImageClip, concatenate_videoclips, 
    AudioFileClip, TextClip, CompositeVideoClip
)
from moviepy.config import change_settings
from moviepy.video.fx import all as vfx
from PIL import Image
import os
from music_algo import create_random_clip, find_best_audio_clips, random_songs

change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\WindowsApps\ImageMagick.Q16-HDRI_7.1.1.44_x64__b3hnabsze9y3j\magick.exe"})
def create_scrolling_video(image_path, audio_file, output_video):
    """Creates a scrolling video from an image with audio."""
    try:
        audio = AudioFileClip(audio_file)
        image_clip = ImageClip(image_path).set_duration(audio.duration)

        # Reduced y_speed from 50 to 30
        scrolling_clip = image_clip.fx(vfx.scroll, h=720, y_speed=30)

        scrolling_clip = scrolling_clip.set_audio(audio)
        scrolling_clip.write_videofile(output_video, fps=24)
    
    except Exception as e:
        print(f"Error creating scrolling video: {e}")

def create_video(text, audio_file, output_video, index):
    """Creates a video with images, text, and audio."""
    try:
        # Verify audio file
        audio_path = os.path.abspath(audio_file)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        audio = AudioFileClip(audio_path)
        print(f"Audio duration: {audio.duration} seconds")

        total_duration = audio.duration
        repo_duration = total_duration / 3
        target_h, target_w = 720, 1280

        clips = []
        screenshot = f"screenshot_{index}.png"
        if not os.path.exists(screenshot):
            raise FileNotFoundError(f"Screenshot not found: {screenshot}")

        image_clip = ImageClip(screenshot)
        scroll_height = max(0, image_clip.h - target_h)  # Avoid negative scroll
        
        # Reduced scroll speed by multiplying by 0.4 instead of 0.6
        scrolling_clip = image_clip.fx(
            vfx.scroll,
            h=target_h,
            w=target_w,
            y_speed=(scroll_height/repo_duration * 0.4) if scroll_height > 0 else 0
        ).set_duration(repo_duration)
        
        clips.append(scrolling_clip)

        if not clips:
            raise ValueError("No valid image clips were created.")

        print(f"Number of clips: {len(clips)}")
        for i, clip in enumerate(clips):
            print(f"Clip {i} duration: {clip.duration} seconds")

        final_clip = concatenate_videoclips(clips)
        print(f"Concatenated clip duration: {final_clip.duration} seconds")
        final_clip = final_clip.set_audio(audio)
        print(f"Audio duration set: {audio.duration} seconds")

        final_clip.write_videofile(
            output_video,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            verbose=True
        )
        print(f"Video written to {output_video}")

    except Exception as e:
        print(f"Error creating video: {e}")
        raise
    finally:
        if "final_clip" in locals():
            final_clip.close()
        if "audio" in locals():
            audio.close()
        if "clips" in locals():
            for clip in clips:
                clip.close()

def combine_videos(video_parts, output_video, total_duration):
    """Combine multiple video parts into a single video with background music."""
    try:
        # Generate and prepare background music
        music = random_songs()
        best_clips = find_best_audio_clips(music, total_duration)
        create_random_clip(music, best_clips)
        
        # Load video clips and music
        clips = [VideoFileClip(video_part) for video_part in video_parts]
        background_music = AudioFileClip("music.mp3")
        
        # Set background music duration to match video
        final_clip = concatenate_videoclips(clips)
        bg_music = background_music.subclip(0, final_clip.duration)
        
        # Add fade in/out effects (2 seconds each)
        bg_music = bg_music.audio_fadein(2).audio_fadeout(2)
        
        # Mix audio - background music at 5% volume (reduced from 10%)
        final_audio = CompositeVideoClip([
            final_clip.set_audio(final_clip.audio.volumex(1.0)),
            final_clip.set_audio(bg_music.volumex(0.05))
        ]).audio
        # Set final audio to video
        final_clip = final_clip.set_audio(final_audio)
        
        # Write final video
        final_clip.write_videofile(output_video, codec="libx264", audio_codec="aac")
        
    except Exception as e:
        print(f"Error combining videos: {e}")
        raise
    finally:
        if "final_clip" in locals():
            final_clip.close()
        if "background_music" in locals():
            background_music.close()
        for clip in clips:
            clip.close()

def get_video_duration(file_path):
    """
    Extracts the duration of a video file in seconds using moviepy.
    
    Args:
        file_path (str): Path to the video file.
    
    Returns:
        float: Duration of the video in seconds, or None if an error occurs.
    """
    try:
        # Load the video file
        video = VideoFileClip(file_path)
        # Get the duration in seconds
        duration = video.duration
        # Close the video to free resources
        video.close()
        return duration
    except Exception as e:
        print(f"Error extracting duration for {file_path}: {e}")
        return None