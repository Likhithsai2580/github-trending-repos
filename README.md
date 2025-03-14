# GitHub Trending Video Generator

This project generates a video that showcases the top 3 trending GitHub repositories with a voiceover. The video features a scrolling screenshot of the GitHub repository page while the voiceover describes the repositories.

## Project Structure

```
github-trending-video
├── src
│   ├── main.py            # Entry point of the application
│   ├── video_generator.py  # Functions for creating the video
│   ├── voice_generator.py  # Functions for generating voiceovers
│   └── utils.py           # Utility functions for the project
├── requirements.txt       # List of dependencies
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd github-trending-video
   ```

2. **Create a virtual environment (optional but recommended):**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/main.py
   ```

2. The application will fetch the top 3 trending GitHub repositories, generate a voiceover, and create a video with a scrolling screenshot of the repository page.

## Dependencies

The project requires the following Python libraries:

- requests
- beautifulsoup4
- edge-tts
- moviepy
- asyncio

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the project.

## License

This project is licensed under the MIT License. See the LICENSE file for details.