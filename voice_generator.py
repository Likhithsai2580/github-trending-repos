import edge_tts
import os
import asyncio

async def generate_voice(text, output_file):
    """Generate voice narration with error handling and verification"""
    try:
        # Ensure any existing audio file is removed
        if os.path.exists(output_file):
            os.remove(output_file)
            await asyncio.sleep(1)  # Increased wait time
            
        # Configure voice settings
        communicate = edge_tts.Communicate(
            text, 
            "en-US-AndrewNeural",
            rate="+0%",  # Normal speed
            volume="+50%"  # Increased volume
        )
        
        # Save audio file
        await communicate.save(output_file)
        await asyncio.sleep(1)  # Wait for file to be fully written
        
        # Verify the file was created and has content
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise Exception("Voice generation failed or produced empty file")
            
        return True
            
    except Exception as e:
        print(f"Error generating voice: {e}")
        raise