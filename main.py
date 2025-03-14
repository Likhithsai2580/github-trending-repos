import requests
import asyncio
import os
from video_generator import create_video, combine_videos, get_video_duration
from voice_generator import generate_voice
from utils import get_trending_repos, fetch_screenshot, cleanup_files, upload_to_youtube
import time
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import cv2

def generate_script_for_repo(repo, index):
    """Generate script for a single repository."""
    summarizer = LsaSummarizer(Stemmer("english"))
    summarizer.stop_words = get_stop_words("english")
    
    script = f"Repository number {index + 1}: {repo['name']}.\n"
    script += f"This repository {repo['description']}."
    
    # Read README content
    readme_path = f"readme_{index}.txt"
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
            if len(readme_content.split()) > 30:
                parser = PlaintextParser.from_string(readme_content, Tokenizer("english"))
                summary = " ".join([str(sentence) for sentence in summarizer(parser.document, 2)])
                script += f" Here's a brief overview: {summary}"
    
    return script

if __name__ == "__main__":
    print("Fetching trending repositories...")
    trending_repos = get_trending_repos()
    print(f"Trending repositories fetched successfully!")
    if trending_repos:
        for i, repo in enumerate(trending_repos):
            print(f"{i+1}. {repo['name']} - {repo['description']}")

        try:
            print("Fetching Screenshots and README content...")
            fetch_screenshot(trending_repos)
            
            # List to store individual video paths
            video_parts = []
            total_video_length = 0
            # Generate individual videos for each repo
            for i, repo in enumerate(trending_repos):
                print(f"Processing repository {i+1}...")
                
                # Generate script for single repo
                script_text = generate_script_for_repo(repo, i)
                
                # Generate voice for single repo
                audio_file = f"output_{i}.mp3"
                asyncio.run(generate_voice(script_text, audio_file))
                
                time.sleep(2)
                
                # Create video for single repo
                video_file = f"repo_video_{i}.mp4"
                create_video(script_text, audio_file, video_file, int(i))
                video_length = get_video_duration(video_file)
                total_video_length += video_length
                video_parts.append(video_file)
            # Calculate total video length
            print(f"Total video length: {total_video_length} seconds")
            # Combine videos (implement this in create_video function)
            print("Combining videos...")
            combine_videos(video_parts, "trending_repos_video.mp4", total_duration=total_video_length)
            final_video = "trending_repos_video.mp4"
            
            # Cleanup temporary files
            cleanup_files()
            print("Cleanup complete")
            upload_to_youtube("trending_repos_video.mp4")
            
        except Exception as e:
            print(f"Error during video creation: {e}")
            cleanup_files()
    else:
        print("Failed to fetch trending repositories.")
