import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
import os

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pytz
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Download all required NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

def get_trending_repos():
    url = "https://github.com/trending/python?since=daily"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        repos = []
        repo_details = []
        
        # Get repositories with their descriptions
        for article in soup.find_all("article", class_="Box-row"):
            repo_h2 = article.find("h2", class_="h3 lh-condensed")
            if repo_h2:
                repo_name = repo_h2.text.strip().replace("\n", "").replace(" ", "")
                description = article.find("p", class_="col-9").text.strip() if article.find("p", class_="col-9") else ""
                repos.append(repo_name)
                repo_details.append({
                    "name": repo_name,
                    "description": description
                })
        return repo_details[:3]  # Return top 3 trending repos with descriptions
    return []

def summarize_readme(text, sentences_count=3):
    """Summarize README text using sumy."""
    try:
        # Initialize the summarizer
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        stemmer = Stemmer("english")
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")

        # Summarize
        summary = summarizer(parser.document, sentences_count)
        return " ".join([str(sentence) for sentence in summary])
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return text[:200] + "..."  # Fallback to simple truncation

def fetch_screenshot(repos):
    """Fetch screenshots and README content for repositories with improved error handling"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--force-device-scale-factor=0.85')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        for i, repo in enumerate(repos):
            print(f"Fetching screenshot for {repo['name']}...")
            url = f"https://github.com/{repo['name']}"
            
            max_page_load_retries = 3
            for load_attempt in range(max_page_load_retries):
                try:
                    driver.get(url)
                    break
                except Exception as e:
                    if load_attempt == max_page_load_retries - 1:
                        raise Exception(f"Failed to load page after {max_page_load_retries} attempts: {e}")
                    time.sleep(2 ** load_attempt)
            
            # Wait for content with timeout
            try:
                wait = WebDriverWait(driver, 20)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "markdown-body")))
            except Exception as e:
                print(f"Warning: Timeout waiting for content on {repo['name']}: {e}")
            
            # Ensure page is ready
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0)")
            
            # Take screenshot with retries
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    # Adjust viewport
                    total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
                    driver.set_window_size(1920, min(total_height, 8000))  # Cap maximum height
                    time.sleep(1)
                    
                    # Take screenshot
                    screenshot_path = f"screenshot_{i}.png"
                    driver.save_screenshot(screenshot_path)
                    
                    if not os.path.exists(screenshot_path):
                        raise Exception("Screenshot file was not created")
                        
                    print(f"Screenshot saved for {repo['name']}")
                    
                    # Get README content
                    readme = driver.find_element(By.CLASS_NAME, "markdown-body")
                    with open(f"readme_{i}.txt", "w", encoding="utf-8") as f:
                        f.write(f"Repository: {repo['name']}\n")
                        f.write(f"Description: {repo['description']}\n\n")
                        f.write("README Highlights:\n")
                        f.write(readme.text[:500])
                    break
                    
                except Exception as e:
                    wait_time = 2 ** attempt
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed for {repo['name']}: {e}")
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Final attempt failed for {repo['name']}: {e}")
                        raise
                        
    except Exception as e:
        print(f"Critical error in fetch_screenshot: {e}")
        raise
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def cleanup_files():
    """Clean up generated files after video creation"""
    files_to_remove = [
        "output.mp3",
        "output_0.mp3",
        "output_1.mp3",
        "output_2.mp3",
        "repo_video_0.mp4",
        "repo_video_1.mp4",
        "repo_video_2.mp4",
        "screenshot_0.png",
        "screenshot_1.png", 
        "screenshot_2.png",
        "readme_0.txt",
        "readme_1.txt",
        "music.mp3",
        "readme_2.txt",
        "temp_video_no_audio.mp4",
        "temp-audio.m4a.log",
        "trending_repos_video.mp4.log"
    ]
    
    # Add a small delay to ensure files are released
    time.sleep(1)
    
    for file in files_to_remove:
        print(f"Removing {file}...")
        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            try:
                if os.path.exists(file):
                    os.remove(file)
                break
            except Exception as e:
                attempt += 1
                if attempt == max_attempts:
                    print(f"Failed to remove {file} after {max_attempts} attempts: {e}")
                time.sleep(1)  # Wait before retry



def upload_to_youtube(video_path, title=None, description=None):
    """
    Upload video to YouTube and schedule for 6 PM IST daily
    
    Args:
        video_path (str): Path to the video file
        title (str): Video title (optional)
        description (str): Video description (optional)
    """
    # Get current date and next available 6 PM IST slot
    ist_time = datetime.now().astimezone(pytz.timezone('Asia/Kolkata'))
    target_time = ist_time.replace(hour=18, minute=0, second=0, microsecond=0)
    
    # If current time is past 6 PM, schedule for next day
    if ist_time >= target_time:
        target_time = target_time + timedelta(days=1)

    # Format default title and description
    if not title:
        title = f"🔥 Top Trending Python Projects on GitHub | {ist_time.strftime('%d %B %Y')}"
    
    if not description:
        description = f"""🚀 Daily GitHub Trending Python Projects Update - {ist_time.strftime('%d %B %Y')}

🔍 Discover the most exciting Python projects trending on GitHub today!
💡 Stay updated with the latest innovations in Python development
🌟 Featured projects include cutting-edge tools, frameworks, and applications

👉 Subscribe and hit the notification bell to stay updated with daily Python trends!

#GitHub #Python #Programming #TrendingProjects #CodingCommunity
"""

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    TOKEN_FILE = 'token.json'
    
    try:
        credentials = None
        # Check if token file exists and load credentials
        if os.path.exists(TOKEN_FILE):
            credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # If no valid credentials available, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', SCOPES, redirect_uri='http://localhost:8080')
                credentials = flow.run_local_server(port=8080)
            
            # Save credentials for future use
            with open(TOKEN_FILE, 'w') as token:
                token.write(credentials.to_json())
        
        youtube = build('youtube', 'v3', credentials=credentials)
        
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['GitHub', 'Python', 'Programming', 'Trending', 'Coding'],
                'categoryId': '28'  # Science & Technology category
            },
            'status': {
                'privacyStatus': 'private',
                'selfDeclaredMadeForKids': False,
                'publishAt': target_time.isoformat()
            }
        }
        
        media = MediaFileUpload(
            video_path, 
            mimetype='video/mp4',
            resumable=True
        )
        
        print(f"Starting YouTube upload, scheduled for {target_time.strftime('%Y-%m-%d %H:%M:%S')} IST...")
        upload_request = youtube.videos().insert(
            part=','.join(request_body.keys()),
            body=request_body,
            media_body=media
        )
        
        response = upload_request.execute()
        print(f"Upload successful! Video ID: {response['id']}")
        print(f"Video will be published at {target_time.strftime('%Y-%m-%d %H:%M:%S')} IST")
        return response['id']
        
    except Exception as e:
        print(f"Error uploading to YouTube: {e}")
        return None