#!/usr/bin/env python3
"""
Quick Animated Demo with Corrected Pronunciation
Optimized version that runs faster
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_output_quick")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Shorter, focused voiceover with corrected pronunciation
VOICEOVER_SCRIPT = """
Welcome to Real Diag, an AI-powered clinical decision support system.

Real Diag helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

First, we enter a patient's chief complaint, such as chest pain.

Real Diag's AI engine immediately analyzes the symptom and generates a comprehensive differential diagnosis ranked by likelihood.

Each diagnosis includes clinical features, red flags, and recommended diagnostic workup.

Real Diag integrates seamlessly with your existing EHR system through FHIR and HL7 standards.

Our platform includes advanced features like medical calculators, drug interaction checking, and clinical guidelines.

With Real Diag, you can provide better patient care while reducing diagnostic errors and saving time.

Ready to transform your clinical practice? Sign up today at real diag dot com.
"""

# Streamlined animation (60 seconds total)
ANIMATION_SCRIPT = [
    {"action": "navigate", "url": "/", "wait": 2},
    {"action": "scroll_smooth", "amount": 300, "wait": 2},
    {"action": "scroll_smooth", "amount": 400, "wait": 2},
    
    {"action": "navigate", "url": "/diagnose", "wait": 2},
    {"action": "type_slow", "selector": "input", "text": "chest pain", "wait": 1},
    {"action": "wait", "wait": 2},
    {"action": "click", "selector": "button[type='submit'], button:has-text('Search'), button:has-text('Analyze')", "wait": 3},
    {"action": "scroll_smooth", "amount": 300, "wait": 2},
    {"action": "scroll_smooth", "amount": 300, "wait": 2},
    
    {"action": "click_if_exists", "selector": "details, summary, .accordion", "wait": 2, "index": 0},
    {"action": "scroll_smooth", "amount": 200, "wait": 2},
    {"action": "scroll_smooth", "amount": 300, "wait": 2},
    
    {"action": "navigate", "url": "/integration", "wait": 2},
    {"action": "scroll_smooth", "amount": 400, "wait": 2},
    {"action": "scroll_smooth", "amount": 400, "wait": 2},
    
    {"action": "navigate", "url": "/features-demo", "wait": 2},
    {"action": "scroll_smooth", "amount": 400, "wait": 2},
    {"action": "scroll_smooth", "amount": 400, "wait": 2},
    
    {"action": "navigate", "url": "/pricing", "wait": 2},
    {"action": "scroll_smooth", "amount": 400, "wait": 2},
    {"action": "navigate", "url": "/", "wait": 1},
    {"action": "scroll_to_top", "wait": 2},
]

async def perform_action(page, action_info):
    """Execute a single action"""
    action_type = action_info.get("action")
    
    try:
        if action_type == "navigate":
            url = f"{WEBSITE_URL}{action_info['url']}"
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
        elif action_type == "type_slow":
            try:
                selectors = ["input[type='text']", "textarea", "input", "[contenteditable='true']"]
                for sel in selectors:
                    try:
                        await page.wait_for_selector(sel, timeout=2000)
                        await page.click(sel)
                        await page.fill(sel, "")
                        for char in action_info["text"]:
                            await page.type(sel, char, delay=120)
                        break
                    except:
                        continue
            except:
                pass
            
        elif action_type == "click":
            try:
                await page.wait_for_selector(action_info["selector"], timeout=2000)
                await page.click(action_info["selector"], timeout=2000)
            except:
                pass
                
        elif action_type == "click_if_exists":
            try:
                elements = await page.query_selector_all(action_info["selector"])
                if elements:
                    await elements[0].click()
            except:
                pass
            
        elif action_type == "scroll_smooth":
            await page.evaluate(f"window.scrollBy({{top: {action_info['amount']}, behavior: 'smooth'}})")
            
        elif action_type == "scroll_to_top":
            await page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        
        await asyncio.sleep(action_info.get("wait", 1))
        
    except Exception as e:
        print(f"   ⚠️  {str(e)[:50]}")
        await asyncio.sleep(0.5)

async def record_video():
    """Record the demo video"""
    print("="*70)
    print("   Quick Animated Demo Recorder")
    print("="*70)
    print(f"📹 Recording ~60 second animation...")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT}
        )
        page = await context.new_page()
        
        for i, action in enumerate(ANIMATION_SCRIPT, 1):
            print(f"   Step {i}/{len(ANIMATION_SCRIPT)}", end="\r")
            await perform_action(page, action)
        
        print(f"\n✅ Recording complete!")
        
        await page.close()
        await context.close()
        await browser.close()
    
    video_files = list(OUTPUT_DIR.glob("*.webm"))
    return max(video_files, key=lambda p: p.stat().st_mtime) if video_files else None

def convert_to_mp4(webm_path):
    """Convert to MP4"""
    print("🎬 Converting to MP4...")
    mp4_path = webm_path.parent / "demo_video.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(webm_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-pix_fmt", "yuv420p", str(mp4_path)
    ], capture_output=True)
    return mp4_path if mp4_path.exists() else None

def generate_voiceover():
    """Generate voiceover with corrected pronunciation"""
    print("📢 Generating voiceover (Real Diag pronunciation)...")
    audio_file = OUTPUT_DIR / "voiceover.mp3"
    
    try:
        from gtts import gTTS
    except ImportError:
        subprocess.run(["pip", "install", "-q", "gtts"], check=True)
        from gtts import gTTS
    
    tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
    tts.save(str(audio_file))
    return audio_file

def combine_video_and_audio(video_path, audio_path):
    """Combine video and audio"""
    print("🎬 Combining video and audio...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = OUTPUT_DIR / f"realdiag_demo_final_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(output)
    ], capture_output=True, text=True)
    
    return output if result.returncode == 0 else None

async def main():
    print("\n🎯 Creating animated demo with corrected pronunciation...\n")
    
    # Step 1: Record video
    webm_video = await record_video()
    if not webm_video:
        print("❌ Failed to record")
        return
    
    # Step 2: Convert to MP4
    mp4_video = convert_to_mp4(webm_video)
    if not mp4_video:
        print("❌ Failed to convert")
        return
    
    # Step 3: Generate voiceover
    audio = generate_voiceover()
    
    # Step 4: Combine
    final_video = combine_video_and_audio(mp4_video, audio)
    
    if final_video:
        size_mb = final_video.stat().st_size / 1024 / 1024
        print(f"\n{'='*70}")
        print(f"✨ SUCCESS!")
        print(f"{'='*70}")
        print(f"📹 {final_video}")
        print(f"📊 {size_mb:.1f} MB")
        print(f"\n🎯 Next: cp {final_video} ../frontend/public/demo-video.mp4")
    else:
        print("\n❌ Failed to create final video")

if __name__ == "__main__":
    asyncio.run(main())
