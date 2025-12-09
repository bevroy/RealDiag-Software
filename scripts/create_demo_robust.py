#!/usr/bin/env python3
"""
RealDiag Demo - Robust Version
- Phonetic pronunciation: "Real Die Agg" 
- Actual smooth scrolling animations
- Better error handling and retries
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import sys

WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_robust")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Use phonetic spelling to get "die agg" pronunciation
VOICEOVER_SCRIPT = """
Welcome to Real Die Agg, an AI-powered clinical decision support system.

Real Die Agg helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

Let me demonstrate how it works.

We start by entering a patient's chief complaint. For example, chest pain.

Real Die Agg's AI engine analyzes the symptom and generates a comprehensive differential diagnosis.

The system ranks diagnostic possibilities from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic tests.

The system provides evidence-based treatment guidelines and criteria for specialist referral.

Real Die Agg integrates with your existing electronic health record system through standard protocols.

Patient data flows automatically, eliminating duplicate entry and reducing errors.

Our platform includes medical calculators, drug interaction checking, and real-time clinical guidelines.

With Real Die Agg, you can provide better patient care, reduce diagnostic errors, and save time.

Transform your clinical practice today at real die agg dot com.
"""

# Simplified but complete demo sequence
ANIMATION_SEQUENCE = [
    # Homepage (8s)
    {"action": "navigate", "url": "/", "pause": 3},
    {"action": "smooth_scroll", "distance": 500, "duration": 2, "pause": 3},
    
    # Diagnostic tool (12s)
    {"action": "navigate", "url": "/diagnose", "pause": 2},
    {"action": "type_symptom", "text": "chest pain", "pause": 2},
    {"action": "click_submit", "pause": 4},
    {"action": "smooth_scroll", "distance": 400, "duration": 2, "pause": 2},
    
    # Expand details (8s)
    {"action": "expand_details", "pause": 2},
    {"action": "smooth_scroll", "distance": 350, "duration": 2, "pause": 2},
    {"action": "smooth_scroll", "distance": 350, "duration": 2, "pause": 2},
    
    # Integration (8s)
    {"action": "navigate", "url": "/integration", "pause": 2},
    {"action": "smooth_scroll", "distance": 500, "duration": 2, "pause": 2},
    {"action": "smooth_scroll", "distance": 500, "duration": 2, "pause": 2},
    
    # Features (8s)
    {"action": "navigate", "url": "/features-demo", "pause": 2},
    {"action": "smooth_scroll", "distance": 500, "duration": 2, "pause": 2},
    {"action": "smooth_scroll", "distance": 500, "duration": 2, "pause": 2},
    
    # Pricing (6s)
    {"action": "navigate", "url": "/pricing", "pause": 2},
    {"action": "smooth_scroll", "distance": 500, "duration": 2, "pause": 2},
    
    # End (4s)
    {"action": "navigate", "url": "/", "pause": 2},
    {"action": "smooth_scroll", "distance": -1000, "duration": 1, "pause": 1},
]

class RobustDemoRecorder:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.page = None
        self.retries = 3
        
    async def safe_navigate(self, url, timeout=20000):
        """Navigate with retries"""
        full_url = f"{WEBSITE_URL}{url}"
        
        for attempt in range(self.retries):
            try:
                print(f"      Navigating to {url}...")
                await self.page.goto(full_url, wait_until="domcontentloaded", timeout=timeout)
                await asyncio.sleep(0.5)  # Let page settle
                return True
            except Exception as e:
                print(f"      ⚠️  Attempt {attempt+1} failed: {str(e)[:50]}")
                if attempt < self.retries - 1:
                    await asyncio.sleep(2)
                else:
                    print(f"      ❌ Could not navigate to {url}")
                    return False
        return False
    
    async def smooth_scroll(self, distance, duration):
        """Smooth animated scrolling"""
        try:
            steps = max(20, int(duration * 10))  # At least 20 steps
            step_distance = distance / steps
            step_delay = duration / steps
            
            for _ in range(steps):
                await self.page.evaluate(f"window.scrollBy(0, {step_distance})")
                await asyncio.sleep(step_delay)
            
            return True
        except Exception as e:
            print(f"      ⚠️  Scroll error: {str(e)[:40]}")
            return False
    
    async def type_into_diagnostic(self, text):
        """Type into diagnostic input field with retries"""
        print(f"      Typing: {text}")
        
        # Multiple selector strategies for finding the diagnostic input
        selectors = [
            "main input[type='text']:visible",
            "main textarea:visible",
            "input[placeholder*='symptom' i]:visible",
            "input[placeholder*='enter' i]:visible",
            ".diagnostic-form input:visible",
            ".search-form input:visible",
            "form input[type='text']:visible",
        ]
        
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=2000, state="visible")
                if element:
                    # Verify it's not email/password field
                    element_type = await element.get_attribute("type") or ""
                    placeholder = await element.get_attribute("placeholder") or ""
                    
                    if "email" in placeholder.lower() or "password" in placeholder.lower():
                        continue
                    
                    # Found the right input!
                    await element.click()
                    await asyncio.sleep(0.3)
                    await element.fill("")
                    
                    # Type with realistic speed
                    for char in text:
                        await element.type(char, delay=120)
                    
                    print(f"      ✓ Typed successfully")
                    return True
                    
            except:
                continue
        
        print(f"      ⚠️  Could not find diagnostic input")
        return False
    
    async def click_submit_button(self):
        """Click the submit/search button"""
        print(f"      Clicking submit...")
        
        selectors = [
            "button[type='submit']:visible",
            "button:has-text('Search'):visible",
            "button:has-text('Analyze'):visible",
            "button:has-text('Diagnose'):visible",
            "input[type='submit']:visible",
        ]
        
        for selector in selectors:
            try:
                button = await self.page.wait_for_selector(selector, timeout=2000, state="visible")
                if button:
                    await button.hover()
                    await asyncio.sleep(0.2)
                    await button.click()
                    print(f"      ✓ Clicked")
                    return True
            except:
                continue
        
        print(f"      ⚠️  Could not find submit button")
        return False
    
    async def expand_first_details(self):
        """Expand details/accordion"""
        print(f"      Expanding details...")
        
        selectors = ["details", "summary", ".accordion", "[role='button']"]
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    await elements[0].scroll_into_view_if_needed()
                    await asyncio.sleep(0.3)
                    await elements[0].click()
                    print(f"      ✓ Expanded")
                    return True
            except:
                continue
        
        print(f"      ⚠️  No expandable elements found")
        return False
    
    async def execute_action(self, step):
        """Execute a single animation step"""
        action = step["action"]
        pause = step.get("pause", 1)
        
        success = True
        
        if action == "navigate":
            url = step["url"]
            print(f"   → Navigate: {url}")
            success = await self.safe_navigate(url)
            
        elif action == "smooth_scroll":
            distance = step["distance"]
            duration = step["duration"]
            print(f"   → Scroll: {distance}px over {duration}s")
            success = await self.smooth_scroll(distance, duration)
            
        elif action == "type_symptom":
            text = step["text"]
            print(f"   → Type: '{text}'")
            success = await self.type_into_diagnostic(text)
            
        elif action == "click_submit":
            print(f"   → Click submit")
            success = await self.click_submit_button()
            
        elif action == "expand_details":
            print(f"   → Expand details")
            success = await self.expand_first_details()
        
        # Pause after action
        await asyncio.sleep(pause)
        
        return success
    
    async def record(self):
        """Record the complete animated demo"""
        print("\n" + "="*80)
        print("   REALDIAG ROBUST DEMO RECORDER")
        print("   Phonetic: 'Real Die Agg' + Smooth Animations")
        print("="*80)
        print(f"\n📹 Recording {len(ANIMATION_SEQUENCE)} animation steps...")
        print(f"⏱️  Estimated duration: ~60 seconds\n")
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = await browser.new_context(
                    viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                    record_video_dir=str(self.output_dir),
                    record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                
                self.page = await context.new_page()
                
                # Execute all animation steps
                success_count = 0
                for i, step in enumerate(ANIMATION_SEQUENCE, 1):
                    print(f"\n[Step {i}/{len(ANIMATION_SEQUENCE)}]")
                    success = await self.execute_action(step)
                    if success:
                        success_count += 1
                
                print(f"\n✅ Recording complete! {success_count}/{len(ANIMATION_SEQUENCE)} steps successful")
                
                await self.page.close()
                await context.close()
                await browser.close()
                
            except Exception as e:
                print(f"\n❌ Recording error: {e}")
                return None
        
        # Find generated video
        videos = list(self.output_dir.glob("*.webm"))
        if videos:
            latest = max(videos, key=lambda p: p.stat().st_mtime)
            print(f"\n📹 Video saved: {latest}")
            return latest
        
        return None

def generate_voiceover():
    """Generate voiceover with phonetic 'die agg'"""
    print("\n📢 Generating voiceover...")
    print("   Using phonetic: 'Real Die Agg'")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    audio_file = OUTPUT_DIR / "voiceover.mp3"
    
    try:
        from gtts import gTTS
    except ImportError:
        print("   Installing gTTS...")
        subprocess.run(["pip", "install", "-q", "gtts"], check=True)
        from gtts import gTTS
    
    tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
    tts.save(str(audio_file))
    print(f"✓ Audio: {audio_file}")
    return audio_file

def convert_webm_to_mp4(webm_path):
    """Convert WebM to MP4"""
    print("\n🎬 Converting to MP4...")
    
    mp4_path = webm_path.parent / "video.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y", "-i", str(webm_path),
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        str(mp4_path)
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and mp4_path.exists():
        print(f"✓ MP4: {mp4_path}")
        return mp4_path
    else:
        print(f"❌ Conversion failed")
        return None

def combine_video_audio(video_path, audio_path):
    """Combine video and audio"""
    print("\n🎬 Combining video + audio...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = OUTPUT_DIR / f"realdiag_demo_final_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(final_output)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        size_mb = final_output.stat().st_size / 1024 / 1024
        print(f"✓ Final: {final_output}")
        print(f"✓ Size: {size_mb:.1f} MB")
        return final_output
    else:
        print(f"❌ Combine failed")
        return None

async def main():
    print("\n🎯 Creating demo with correct pronunciation and animations\n")
    
    # Step 1: Record animated video
    recorder = RobustDemoRecorder()
    webm_video = await recorder.record()
    
    if not webm_video:
        print("\n❌ Failed to record video")
        sys.exit(1)
    
    # Step 2: Convert to MP4
    mp4_video = convert_webm_to_mp4(webm_video)
    if not mp4_video:
        print("\n❌ Failed to convert")
        sys.exit(1)
    
    # Step 3: Generate voiceover
    audio = generate_voiceover()
    
    # Step 4: Combine
    final_video = combine_video_audio(mp4_video, audio)
    
    if final_video:
        print("\n" + "="*80)
        print("✨ SUCCESS!")
        print("="*80)
        print(f"\n📹 {final_video}")
        print(f"📊 {final_video.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"\n✅ Pronunciation: 'Real Die Agg' (phonetic)")
        print(f"✅ Animation: Smooth scrolling throughout")
        print(f"\n🚀 Deploy:")
        print(f"   cp {final_video} ../frontend/public/demo-video.mp4")
        print(f"   git add frontend/public/demo-video.mp4")
        print(f"   git commit -m 'Update demo: correct pronunciation and smooth animations'")
        print(f"   git push")
        print()
    else:
        print("\n❌ Failed to create final video")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
