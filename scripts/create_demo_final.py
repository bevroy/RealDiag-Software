#!/usr/bin/env python3
"""
RealDiag Demo Creator - Final Version
Fixed pronunciation using phonetic spelling + Real animated screen recording
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import time

WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_final")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Use phonetic spelling to fix pronunciation
# "Diag" is pronounced wrong, so use "dee ag" or spell it out
VOICEOVER_SCRIPT = """
Welcome to Real Dee Ag, an AI-powered clinical decision support system.

Real Dee Ag helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

Let me demonstrate how it works.

We start by entering a patient's chief complaint. For example, chest pain.

Real Dee Ag's AI engine analyzes the symptom and generates a comprehensive differential diagnosis.

The system ranks diagnostic possibilities from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic tests.

The system provides evidence-based treatment guidelines and criteria for specialist referral.

Real Dee Ag integrates with your existing electronic health record system through FHIR and HL7 standards.

Patient data flows automatically, eliminating duplicate entry and reducing errors.

Our platform includes medical calculators, drug interaction checking, and real-time clinical guidelines.

With Real Dee Ag, you can provide better care, reduce diagnostic errors, and save time.

Transform your clinical practice today. Visit real dee ag dot com.
"""

# Detailed step-by-step actions for REAL animation
DEMO_ACTIONS = [
    # Start: Homepage (8 seconds)
    {"type": "goto", "url": "/", "desc": "Load homepage"},
    {"type": "wait", "seconds": 3, "desc": "Show homepage"},
    {"type": "scroll", "pixels": 400, "duration": 1.5, "desc": "Scroll to features"},
    {"type": "wait", "seconds": 3, "desc": "Display features"},
    
    # Navigate to diagnostic tool (10 seconds)
    {"type": "scroll", "pixels": -800, "duration": 1, "desc": "Scroll back up"},
    {"type": "goto", "url": "/diagnose", "desc": "Open diagnostic tool"},
    {"type": "wait", "seconds": 3, "desc": "Show diagnostic interface"},
    
    # Type symptom SLOWLY and VISIBLY (8 seconds)
    {"type": "focus_input", "desc": "Click on input field"},
    {"type": "wait", "seconds": 1, "desc": "Ready to type"},
    {"type": "type_text", "text": "chest pain", "delay": 200, "desc": "Type symptom slowly"},
    {"type": "wait", "seconds": 2, "desc": "Show completed text"},
    
    # Click and wait for results (8 seconds)
    {"type": "click_button", "text": "Search,Analyze,Diagnose,Submit", "desc": "Click analyze button"},
    {"type": "wait", "seconds": 4, "desc": "Wait for AI processing"},
    
    # Scroll through results (12 seconds)
    {"type": "scroll", "pixels": 300, "duration": 2, "desc": "Scroll to results"},
    {"type": "wait", "seconds": 2, "desc": "Show differential diagnosis"},
    {"type": "scroll", "pixels": 300, "duration": 2, "desc": "Show more diagnoses"},
    {"type": "wait", "seconds": 2, "desc": "Display ranked conditions"},
    
    # Expand details (10 seconds)
    {"type": "click_first", "selector": "details,summary,.accordion,[role='button']", "desc": "Expand diagnosis"},
    {"type": "wait", "seconds": 2, "desc": "Show expanded content"},
    {"type": "scroll", "pixels": 250, "duration": 1.5, "desc": "Scroll detail"},
    {"type": "wait", "seconds": 2, "desc": "Show clinical features"},
    {"type": "scroll", "pixels": 250, "duration": 1.5, "desc": "Show more detail"},
    {"type": "wait", "seconds": 2, "desc": "Display treatment info"},
    
    # Integration page (10 seconds)
    {"type": "goto", "url": "/integration", "desc": "Go to integration"},
    {"type": "wait", "seconds": 2, "desc": "Show EHR integration"},
    {"type": "scroll", "pixels": 400, "duration": 2, "desc": "Scroll integration"},
    {"type": "wait", "seconds": 2, "desc": "Show FHIR/HL7"},
    {"type": "scroll", "pixels": 400, "duration": 2, "desc": "Scroll more"},
    {"type": "wait", "seconds": 2, "desc": "Show data flow"},
    
    # Features (10 seconds)
    {"type": "goto", "url": "/features-demo", "desc": "Features page"},
    {"type": "wait", "seconds": 2, "desc": "Show features"},
    {"type": "scroll", "pixels": 400, "duration": 2, "desc": "Scroll features"},
    {"type": "wait", "seconds": 2, "desc": "Show calculators"},
    {"type": "scroll", "pixels": 400, "duration": 2, "desc": "More features"},
    {"type": "wait", "seconds": 2, "desc": "Show guidelines"},
    
    # Pricing and end (10 seconds)
    {"type": "goto", "url": "/pricing", "desc": "Pricing page"},
    {"type": "wait", "seconds": 2, "desc": "Show pricing"},
    {"type": "scroll", "pixels": 400, "duration": 2, "desc": "Scroll pricing"},
    {"type": "wait", "seconds": 2, "desc": "Display tiers"},
    {"type": "goto", "url": "/", "desc": "Back to homepage"},
    {"type": "scroll", "pixels": -1000, "duration": 1, "desc": "Scroll to top"},
    {"type": "wait", "seconds": 3, "desc": "End on logo"},
]

class DemoRecorder:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.page = None
        
    async def execute_action(self, action):
        """Execute a single action with proper timing"""
        action_type = action["type"]
        desc = action.get("desc", "")
        
        try:
            if action_type == "goto":
                url = f"{WEBSITE_URL}{action['url']}"
                print(f"   📍 {desc}: {action['url']}")
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
                
            elif action_type == "wait":
                seconds = action["seconds"]
                print(f"   ⏸️  {desc} ({seconds}s)")
                await asyncio.sleep(seconds)
                
            elif action_type == "scroll":
                pixels = action["pixels"]
                duration = action["duration"]
                print(f"   📜 {desc}")
                
                # Smooth scroll animation
                steps = int(duration * 10)  # 10 steps per second
                step_size = pixels / steps
                for _ in range(steps):
                    await self.page.evaluate(f"window.scrollBy(0, {step_size})")
                    await asyncio.sleep(duration / steps)
                    
            elif action_type == "focus_input":
                print(f"   🖱️  {desc}")
                # Find and click input field
                selectors = [
                    "input[type='text']",
                    "textarea",
                    "input[placeholder]",
                    "[contenteditable='true']"
                ]
                for sel in selectors:
                    try:
                        await self.page.wait_for_selector(sel, timeout=2000)
                        await self.page.click(sel)
                        print(f"      ✓ Focused input")
                        break
                    except:
                        continue
                        
            elif action_type == "type_text":
                text = action["text"]
                delay = action.get("delay", 150)
                print(f"   ⌨️  {desc}: '{text}'")
                
                # Type character by character for realistic effect
                for i, char in enumerate(text):
                    await self.page.keyboard.type(char)
                    await asyncio.sleep(delay / 1000)
                    if i % 3 == 0:  # Show progress
                        print(f"      Typed: {text[:i+1]}", end="\r")
                print(f"      ✓ Typed: '{text}'")
                
            elif action_type == "click_button":
                print(f"   🖱️  {desc}")
                # Try multiple button selectors
                button_texts = action["text"].split(",")
                clicked = False
                for text in button_texts:
                    selectors = [
                        f"button:has-text('{text.strip()}')",
                        f"button[type='submit']",
                        f"input[type='submit']",
                        f"a:has-text('{text.strip()}')",
                    ]
                    for sel in selectors:
                        try:
                            await self.page.wait_for_selector(sel, timeout=2000)
                            # Hover first for visual effect
                            await self.page.hover(sel)
                            await asyncio.sleep(0.3)
                            await self.page.click(sel)
                            print(f"      ✓ Clicked button")
                            clicked = True
                            break
                        except:
                            continue
                    if clicked:
                        break
                        
            elif action_type == "click_first":
                selector = action["selector"]
                print(f"   🖱️  {desc}")
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        await elements[0].scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await elements[0].click()
                        print(f"      ✓ Clicked element")
                except Exception as e:
                    print(f"      ⚠️  Could not click: {str(e)[:40]}")
                    
        except Exception as e:
            print(f"   ❌ Error in {action_type}: {str(e)[:60]}")
            await asyncio.sleep(0.5)
    
    async def record(self):
        """Record the complete demo"""
        print("\n" + "="*80)
        print("   REALDIAG DEMO RECORDER - FINAL VERSION")
        print("   Real Animation + Fixed Pronunciation")
        print("="*80)
        print(f"\n📁 Output: {self.output_dir}")
        print(f"🌐 Website: {WEBSITE_URL}")
        print(f"📺 Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
        print(f"🎬 Recording {len(DEMO_ACTIONS)} actions (~90 seconds)\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT}
            )
            self.page = await context.new_page()
            
            start_time = time.time()
            
            # Execute all actions
            for i, action in enumerate(DEMO_ACTIONS, 1):
                elapsed = time.time() - start_time
                print(f"\n[{elapsed:.0f}s] Step {i}/{len(DEMO_ACTIONS)}")
                await self.execute_action(action)
            
            total_time = time.time() - start_time
            print(f"\n✅ Recording complete! Total time: {total_time:.0f}s")
            
            await self.page.close()
            await context.close()
            await self.browser.close()
        
        # Find generated video
        videos = list(self.output_dir.glob("*.webm"))
        if videos:
            latest = max(videos, key=lambda p: p.stat().st_mtime)
            print(f"📹 Video saved: {latest}")
            return latest
        return None

def generate_voiceover_phonetic():
    """Generate voiceover with phonetic pronunciation"""
    print("\n📢 Generating voiceover with phonetic pronunciation...")
    print("   Using 'dee ag' to fix pronunciation")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    audio_file = OUTPUT_DIR / "voiceover_phonetic.mp3"
    
    try:
        from gtts import gTTS
    except ImportError:
        subprocess.run(["pip", "install", "-q", "gtts"], check=True)
        from gtts import gTTS
    
    tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
    tts.save(str(audio_file))
    print(f"✓ Audio generated: {audio_file}")
    return audio_file

def convert_webm_to_mp4(webm_path):
    """Convert WebM to MP4"""
    print("\n🎬 Converting WebM to MP4...")
    mp4_path = webm_path.parent / "demo_animated.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y", "-i", str(webm_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-pix_fmt", "yuv420p", str(mp4_path)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ MP4 created: {mp4_path}")
        return mp4_path
    else:
        print(f"❌ Conversion failed: {result.stderr[:200]}")
        return None

def combine_video_audio(video_path, audio_path):
    """Combine video and audio"""
    print("\n🎬 Combining video and audio...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = OUTPUT_DIR / f"realdiag_demo_FIXED_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(output)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        size_mb = output.stat().st_size / 1024 / 1024
        print(f"✓ Final video: {output}")
        print(f"✓ Size: {size_mb:.1f} MB")
        return output
    else:
        print(f"❌ Combine failed: {result.stderr[:200]}")
        return None

async def main():
    print("\n🎯 Creating FIXED demo: Real Animation + Correct Pronunciation\n")
    
    # Step 1: Record actual animation
    recorder = DemoRecorder()
    webm_video = await recorder.record()
    
    if not webm_video:
        print("\n❌ Failed to record video")
        return
    
    # Step 2: Convert to MP4
    mp4_video = convert_webm_to_mp4(webm_video)
    if not mp4_video:
        print("\n❌ Failed to convert")
        return
    
    # Step 3: Generate voiceover with phonetic pronunciation
    audio = generate_voiceover_phonetic()
    
    # Step 4: Combine
    final_video = combine_video_audio(mp4_video, audio)
    
    if final_video:
        print("\n" + "="*80)
        print("✨ SUCCESS - BOTH ISSUES FIXED!")
        print("="*80)
        print(f"\n📹 Final video: {final_video}")
        print(f"📊 Size: {final_video.stat().st_size / 1024 / 1024:.1f} MB")
        print("\n✅ Fixed Issues:")
        print("   1. Pronunciation: Using 'dee ag' phonetics")
        print("   2. Animation: Real scrolling, typing, clicking")
        print(f"\n🚀 Deploy:")
        print(f"   cp {final_video} ../frontend/public/demo-video.mp4")
        print()
    else:
        print("\n❌ Failed to create final video")

if __name__ == "__main__":
    asyncio.run(main())
