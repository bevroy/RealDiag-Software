#!/usr/bin/env python3
"""
RealDiag Demo - Working Version
Fixes: 1) Correct input field targeting, 2) Better pronunciation
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_working")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Split into two words and spell out D-I-A-G to fix pronunciation
VOICEOVER_SCRIPT = """
Welcome to Real D I A G, an AI-powered clinical decision support system.

Real D I A G helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

Let me demonstrate how it works.

We start by entering a patient's chief complaint. For example, chest pain.

Real D I A G's AI engine analyzes the symptom and generates a comprehensive differential diagnosis.

The system ranks diagnostic possibilities from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic tests.

The system provides evidence-based treatment guidelines and criteria for specialist referral.

Real D I A G integrates with your existing electronic health record system.

Patient data flows automatically, eliminating duplicate entry and reducing errors.

Our platform includes medical calculators, drug interaction checking, and real-time clinical guidelines.

With Real D I A G, you can provide better care, reduce diagnostic errors, and save time.

Transform your clinical practice today.
"""

# Step-by-step demo focusing on the diagnostic tool
DEMO_STEPS = [
    # Homepage intro (6s)
    {"action": "goto", "url": "/", "wait": 3},
    {"action": "scroll", "pixels": 400, "speed": 1.5, "wait": 2.5},
    
    # Go directly to diagnostic tool (not login!)
    {"action": "goto", "url": "/diagnose", "wait": 3},
    {"action": "wait", "duration": 2},
    
    # Find the DIAGNOSTIC input (not email/login input!)
    {"action": "type_in_diagnostic", "text": "chest pain", "wait": 2},
    
    # Submit the diagnostic query
    {"action": "click_diagnostic_submit", "wait": 4},
    
    # Scroll through results
    {"action": "scroll", "pixels": 350, "speed": 2, "wait": 2},
    {"action": "scroll", "pixels": 350, "speed": 2, "wait": 2},
    
    # Try to expand details
    {"action": "expand_first_detail", "wait": 2},
    {"action": "scroll", "pixels": 300, "speed": 1.5, "wait": 2},
    {"action": "scroll", "pixels": 300, "speed": 1.5, "wait": 2},
    
    # Show integration
    {"action": "goto", "url": "/integration", "wait": 2},
    {"action": "scroll", "pixels": 400, "speed": 2, "wait": 2},
    {"action": "scroll", "pixels": 400, "speed": 2, "wait": 2},
    
    # Show features
    {"action": "goto", "url": "/features-demo", "wait": 2},
    {"action": "scroll", "pixels": 400, "speed": 2, "wait": 2},
    {"action": "scroll", "pixels": 400, "speed": 2, "wait": 2},
    
    # Show pricing
    {"action": "goto", "url": "/pricing", "wait": 2},
    {"action": "scroll", "pixels": 400, "speed": 2, "wait": 2},
    
    # End on homepage
    {"action": "goto", "url": "/", "wait": 2},
    {"action": "scroll", "pixels": -1000, "speed": 1, "wait": 2},
]

async def execute_step(page, step):
    """Execute a demo step"""
    action = step["action"]
    
    try:
        if action == "goto":
            url = f"{WEBSITE_URL}{step['url']}"
            print(f"   → Navigate to {step['url']}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(step.get("wait", 1))
            
        elif action == "wait":
            duration = step["duration"]
            print(f"   → Wait {duration}s")
            await asyncio.sleep(duration)
            
        elif action == "scroll":
            pixels = step["pixels"]
            speed = step.get("speed", 1)
            print(f"   → Scroll {pixels}px")
            
            # Smooth animated scroll
            steps = int(abs(pixels) / 50)
            step_delay = speed / steps
            for _ in range(steps):
                await page.evaluate(f"window.scrollBy(0, {pixels/steps})")
                await asyncio.sleep(step_delay / steps)
            
            await asyncio.sleep(step.get("wait", 0))
            
        elif action == "type_in_diagnostic":
            text = step["text"]
            print(f"   → Type in DIAGNOSTIC tool: '{text}'")
            
            # Wait for page to be ready
            await asyncio.sleep(1)
            
            # Try to find the diagnostic input field specifically
            # Look for common patterns on /diagnose page (NOT login page)
            diagnostic_selectors = [
                # Try ID first
                "#symptom-input",
                "#symptom",
                "#diagnostic-input",
                "#search-input",
                # Try by placeholder text
                "input[placeholder*='symptom' i]",
                "input[placeholder*='Enter' i]",
                "input[placeholder*='search' i]",
                "textarea[placeholder*='symptom' i]",
                # Try by name
                "input[name='symptom']",
                "input[name='query']",
                "textarea[name='symptom']",
                # Try by parent structure (main content, not header/nav)
                "main input[type='text']",
                "main textarea",
                ".diagnostic input",
                ".search-box input",
                # Last resort: first visible input that's not in nav/header
                "input[type='text']:not(header input):not(nav input)",
            ]
            
            typed = False
            for selector in diagnostic_selectors:
                try:
                    # Check if element exists and is visible
                    element = await page.wait_for_selector(selector, timeout=1000, state="visible")
                    if element:
                        # Make sure it's not a login/email field
                        placeholder = await element.get_attribute("placeholder") or ""
                        input_type = await element.get_attribute("type") or ""
                        name = await element.get_attribute("name") or ""
                        
                        # Skip if it looks like email/password/login
                        if any(skip in placeholder.lower() + name.lower() for skip in ["email", "password", "username", "login"]):
                            print(f"      Skipping login field: {selector}")
                            continue
                        
                        # This looks good - use it!
                        print(f"      Found diagnostic input: {selector}")
                        await element.click()
                        await asyncio.sleep(0.3)
                        await element.fill("")  # Clear first
                        
                        # Type slowly for visibility
                        for char in text:
                            await element.type(char, delay=150)
                        
                        print(f"      ✓ Typed successfully")
                        typed = True
                        break
                        
                except Exception as e:
                    continue
            
            if not typed:
                print(f"      ⚠️  Could not find diagnostic input field")
            
            await asyncio.sleep(step.get("wait", 0))
            
        elif action == "click_diagnostic_submit":
            print(f"   → Click submit button")
            
            # Try to find submit button
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Search')",
                "button:has-text('Analyze')",
                "button:has-text('Diagnose')",
                "button:has-text('Submit')",
                ".search-button",
                ".diagnostic-button",
                "main button",
            ]
            
            for selector in button_selectors:
                try:
                    button = await page.wait_for_selector(selector, timeout=1000, state="visible")
                    if button:
                        await button.hover()
                        await asyncio.sleep(0.2)
                        await button.click()
                        print(f"      ✓ Clicked: {selector}")
                        break
                except:
                    continue
            
            await asyncio.sleep(step.get("wait", 0))
            
        elif action == "expand_first_detail":
            print(f"   → Expand details")
            
            selectors = ["details", "summary", ".accordion", "[role='button']"]
            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        await elements[0].click()
                        print(f"      ✓ Expanded")
                        break
                except:
                    continue
            
            await asyncio.sleep(step.get("wait", 0))
            
    except Exception as e:
        print(f"   ⚠️  Error: {str(e)[:60]}")
        await asyncio.sleep(0.5)

async def record_demo():
    """Record the demonstration"""
    print("\n" + "="*80)
    print("   REALDIAG DEMO - WORKING VERSION")
    print("   Fixed: Correct input targeting + Better pronunciation")
    print("="*80)
    print(f"\n📹 Recording {len(DEMO_STEPS)} steps...\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
            record_video_dir=str(OUTPUT_DIR),
            record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT}
        )
        page = await context.new_page()
        
        for i, step in enumerate(DEMO_STEPS, 1):
            print(f"\n[Step {i}/{len(DEMO_STEPS)}]")
            await execute_step(page, step)
        
        print(f"\n✅ Recording complete!")
        
        await page.close()
        await context.close()
        await browser.close()
    
    videos = list(OUTPUT_DIR.glob("*.webm"))
    return max(videos, key=lambda p: p.stat().st_mtime) if videos else None

def generate_voiceover():
    """Generate voiceover with spelling D-I-A-G"""
    print("\n📢 Generating voiceover (spelling D-I-A-G)...")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    audio_file = OUTPUT_DIR / "voiceover.mp3"
    
    try:
        from gtts import gTTS
    except ImportError:
        subprocess.run(["pip", "install", "-q", "gtts"], check=True)
        from gtts import gTTS
    
    tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
    tts.save(str(audio_file))
    print(f"✓ Generated: {audio_file}")
    return audio_file

def convert_and_combine(webm_path, audio_path):
    """Convert video and combine with audio"""
    print("\n🎬 Converting and combining...")
    
    # First convert webm to mp4
    mp4_temp = webm_path.parent / "temp.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(webm_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-pix_fmt", "yuv420p", str(mp4_temp)
    ], capture_output=True)
    
    if not mp4_temp.exists():
        return None
    
    # Combine with audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final = OUTPUT_DIR / f"realdiag_demo_FIXED_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(mp4_temp),
        "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(final)
    ], capture_output=True)
    
    mp4_temp.unlink()  # Clean up temp file
    
    if result.returncode == 0:
        return final
    return None

async def main():
    print("\n🎯 Creating WORKING demo with fixes...\n")
    
    # Record video
    webm = await record_demo()
    if not webm:
        print("\n❌ Recording failed")
        return
    
    # Generate audio
    audio = generate_voiceover()
    
    # Combine
    final = convert_and_combine(webm, audio)
    
    if final:
        size = final.stat().st_size / 1024 / 1024
        print("\n" + "="*80)
        print("✨ SUCCESS!")
        print("="*80)
        print(f"\n📹 {final}")
        print(f"📊 {size:.1f} MB")
        print(f"\n✅ Fixes:")
        print(f"   1. Types into DIAGNOSTIC input (not login email)")
        print(f"   2. Spells D-I-A-G for correct pronunciation")
        print(f"\n🚀 Deploy: cp {final} ../frontend/public/demo-video.mp4")
    else:
        print("\n❌ Failed")

if __name__ == "__main__":
    asyncio.run(main())
