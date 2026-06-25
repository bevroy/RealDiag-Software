#!/usr/bin/env python3
"""
RealDiag Demo - Final Attempt with Maximum Robustness
Records from live site with extensive error handling and retries
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time

WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_final_attempt")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
MAX_RETRIES = 5

# Phonetic: "Real Die Agg"
VOICEOVER_SCRIPT = """
Welcome to Real Die Agg, an AI powered clinical decision support system.

Real Die Agg helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real time.

Let me demonstrate how it works.

We enter a patient's chief complaint, such as chest pain.

Real Die Agg's AI engine analyzes the symptom and generates a comprehensive differential diagnosis ranked by likelihood.

Each diagnosis includes key clinical features, red flags, and recommended diagnostic tests.

The system provides evidence based treatment guidelines and specialist referral criteria.

Real Die Agg integrates with your existing EHR system through standard protocols.

Our platform includes medical calculators, drug interaction checking, and real time clinical guidelines.

With Real Die Agg, you can provide better care, reduce errors, and save time.

Transform your clinical practice today.
"""

# Simplified, reliable sequence
DEMO_SEQUENCE = [
    {"action": "load", "url": "/", "wait": 3},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    
    {"action": "load", "url": "/diagnose", "wait": 2},
    {"action": "wait", "seconds": 2},
    {"action": "scroll", "pixels": 300, "duration": 1.5, "wait": 2},
    
    {"action": "load", "url": "/integration", "wait": 2},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    
    {"action": "load", "url": "/features-demo", "wait": 2},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    
    {"action": "load", "url": "/pricing", "wait": 2},
    {"action": "scroll", "pixels": 400, "duration": 2, "wait": 2},
    
    {"action": "load", "url": "/", "wait": 2},
    {"action": "scroll", "pixels": -800, "duration": 1, "wait": 2},
]

async def safe_goto(page, url, retries=MAX_RETRIES):
    """Navigate with retries and fallbacks"""
    full_url = f"{WEBSITE_URL}{url}"
    
    for attempt in range(retries):
        try:
            print(f"      Attempt {attempt + 1}/{retries}...", end=" ")
            await page.goto(full_url, wait_until="domcontentloaded", timeout=15000)
            print("✓")
            return True
        except PlaywrightTimeout:
            print("timeout")
            if attempt < retries - 1:
                await asyncio.sleep(2)
        except Exception as e:
            print(f"error: {str(e)[:30]}")
            if attempt < retries - 1:
                await asyncio.sleep(2)
    
    print(f"      ❌ Failed to load {url}")
    return False

async def smooth_scroll(page, pixels, duration):
    """Smooth scrolling animation"""
    try:
        steps = max(15, int(duration * 10))
        step_size = pixels / steps
        delay = duration / steps
        
        for _ in range(steps):
            await page.evaluate(f"window.scrollBy(0, {step_size})")
            await asyncio.sleep(delay)
        
        return True
    except Exception as e:
        print(f"      Scroll error: {str(e)[:30]}")
        return False

async def record_demo():
    """Record with maximum error handling"""
    print("\n" + "="*80)
    print("   REALDIAG DEMO - MAXIMUM ROBUSTNESS")
    print("   Pronunciation: 'Real Die Agg' + Smooth Scrolling")
    print("="*80)
    print(f"\n🎬 Recording {len(DEMO_SEQUENCE)} steps with retries enabled...\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = await browser.new_context(
                viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                record_video_dir=str(OUTPUT_DIR),
                record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            # Execute sequence
            for i, step in enumerate(DEMO_SEQUENCE, 1):
                action = step["action"]
                print(f"[{i}/{len(DEMO_SEQUENCE)}] {action.upper()}", end="")
                
                if action == "load":
                    print(f" {step['url']}")
                    success = await safe_goto(page, step["url"])
                    if not success:
                        print("      Skipping to next step...")
                    await asyncio.sleep(step.get("wait", 1))
                    
                elif action == "scroll":
                    pixels = step["pixels"]
                    duration = step["duration"]
                    print(f" {pixels}px")
                    await smooth_scroll(page, pixels, duration)
                    await asyncio.sleep(step.get("wait", 0))
                    
                elif action == "wait":
                    seconds = step["seconds"]
                    print(f" {seconds}s")
                    await asyncio.sleep(seconds)
            
            print("\n✅ Recording complete!")
            
            await page.close()
            await context.close()
            await browser.close()
            
        except Exception as e:
            print(f"\n❌ Recording error: {str(e)[:100]}")
            return None
    
    # Find video
    videos = list(OUTPUT_DIR.glob("*.webm"))
    if videos:
        latest = max(videos, key=lambda p: p.stat().st_mtime)
        print(f"📹 Video: {latest}")
        return latest
    
    return None

def generate_audio():
    """Generate voiceover"""
    print("\n📢 Generating voiceover (Real Die Agg)...")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    audio_file = OUTPUT_DIR / "voiceover.mp3"
    
    try:
        from gtts import gTTS
        tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
        tts.save(str(audio_file))
        print(f"✓ {audio_file}")
        return audio_file
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return None

def convert_to_mp4(webm_path):
    """Convert WebM to MP4"""
    print("\n🎬 Converting to MP4...")
    
    mp4_path = webm_path.parent / "demo.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y", "-i", str(webm_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-pix_fmt", "yuv420p", str(mp4_path)
    ], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0 and mp4_path.exists():
        print(f"✓ {mp4_path}")
        return mp4_path
    
    print(f"❌ Conversion failed")
    return None

def combine_av(video_path, audio_path):
    """Combine video and audio"""
    print("\n🎬 Combining video + audio...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = OUTPUT_DIR / f"realdiag_demo_smooth_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(output)
    ], capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0:
        size_mb = output.stat().st_size / 1024 / 1024
        print(f"✓ {output}")
        print(f"✓ Size: {size_mb:.1f} MB")
        return output
    
    print(f"❌ Combine failed")
    return None

async def main():
    print("\n🎯 Creating demo with Real Die Agg pronunciation + smooth scrolling\n")
    
    start_time = time.time()
    
    # Record
    webm = await record_demo()
    if not webm:
        print("\n❌ Recording failed")
        return
    
    # Convert
    mp4 = convert_to_mp4(webm)
    if not mp4:
        print("\n❌ Conversion failed")
        return
    
    # Audio
    audio = generate_audio()
    if not audio:
        print("\n❌ Audio generation failed")
        return
    
    # Combine
    final = combine_av(mp4, audio)
    
    elapsed = time.time() - start_time
    
    if final:
        print("\n" + "="*80)
        print("✨ SUCCESS!")
        print("="*80)
        print(f"\n📹 {final}")
        print(f"⏱️  Total time: {elapsed:.0f}s")
        print(f"\n✅ Pronunciation: Real Die Agg")
        print(f"✅ Animation: Smooth scrolling")
        print(f"\n🚀 Deploy:")
        print(f"   cp {final} ../frontend/public/demo-video.mp4")
        print(f"   git add frontend/public/demo-video.mp4")
        print(f"   git commit -m 'Demo with smooth animations and Real Die Agg pronunciation'")
        print(f"   git push")
    else:
        print("\n❌ Failed to create final video")

if __name__ == "__main__":
    asyncio.run(main())
