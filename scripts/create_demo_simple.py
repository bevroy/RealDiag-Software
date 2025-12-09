#!/usr/bin/env python3
"""
Simple Reliable Demo - Uses manual approach for better control
"""

import subprocess
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("demo_simple")
OUTPUT_DIR.mkdir(exist_ok=True)

# Use "Real Diagnostic" instead to avoid mispronunciation
VOICEOVER_SCRIPT = """
Welcome to Real Diagnostic, an AI-powered clinical decision support system.

Real Diagnostic helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

Enter a patient's chief complaint, such as chest pain.

The AI engine analyzes the symptom and generates a comprehensive differential diagnosis, ranked by clinical likelihood.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic tests.

The system provides evidence-based treatment guidelines and criteria for specialist referral.

Real Diagnostic integrates with your existing electronic health record system through standard protocols.

Our platform includes medical calculators, drug interaction checking, and real-time clinical guidelines.

With Real Diagnostic, you can provide better patient care, reduce diagnostic errors, and save valuable time.

Transform your clinical practice today at real diagnostic dot com.
"""

def create_demo_screenshots():
    """Take actual screenshots from the live website"""
    print("📸 Creating demo screenshots...")
    
    from playwright.sync_api import sync_playwright
    
    screenshots = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Homepage
        print("   → Homepage...")
        page.goto("https://realdiag.netlify.app/", wait_until="networkidle")
        page.wait_for_timeout(2000)
        screenshot1 = OUTPUT_DIR / "01_homepage.png"
        page.screenshot(path=str(screenshot1), full_page=False)
        screenshots.append(screenshot1)
        
        # Scroll homepage
        print("   → Homepage scrolled...")
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(1000)
        screenshot2 = OUTPUT_DIR / "02_homepage_features.png"
        page.screenshot(path=str(screenshot2), full_page=False)
        screenshots.append(screenshot2)
        
        # Diagnostic tool page
        print("   → Diagnostic tool...")
        page.goto("https://realdiag.netlify.app/diagnose", wait_until="networkidle")
        page.wait_for_timeout(2000)
        screenshot3 = OUTPUT_DIR / "03_diagnostic_tool.png"
        page.screenshot(path=str(screenshot3), full_page=False)
        screenshots.append(screenshot3)
        
        # Type in diagnostic tool
        print("   → Typing symptom...")
        try:
            # Find the input field
            input_selector = "input[type='text'], textarea, input[placeholder]"
            page.fill(input_selector, "chest pain")
            page.wait_for_timeout(1000)
            screenshot4 = OUTPUT_DIR / "04_symptom_entered.png"
            page.screenshot(path=str(screenshot4), full_page=False)
            screenshots.append(screenshot4)
            
            # Click submit
            print("   → Results...")
            page.click("button[type='submit'], button:has-text('Search'), button:has-text('Analyze')")
            page.wait_for_timeout(3000)
            screenshot5 = OUTPUT_DIR / "05_results.png"
            page.screenshot(path=str(screenshot5), full_page=False)
            screenshots.append(screenshot5)
            
            # Scroll results
            print("   → Results scrolled...")
            page.evaluate("window.scrollBy(0, 400)")
            page.wait_for_timeout(1000)
            screenshot6 = OUTPUT_DIR / "06_results_scrolled.png"
            page.screenshot(path=str(screenshot6), full_page=False)
            screenshots.append(screenshot6)
        except Exception as e:
            print(f"      ⚠️  Could not complete diagnostic flow: {e}")
        
        # Integration page
        print("   → Integration...")
        page.goto("https://realdiag.netlify.app/integration", wait_until="networkidle")
        page.wait_for_timeout(2000)
        screenshot7 = OUTPUT_DIR / "07_integration.png"
        page.screenshot(path=str(screenshot7), full_page=False)
        screenshots.append(screenshot7)
        
        # Features
        print("   → Features...")
        page.goto("https://realdiag.netlify.app/features-demo", wait_until="networkidle")
        page.wait_for_timeout(2000)
        screenshot8 = OUTPUT_DIR / "08_features.png"
        page.screenshot(path=str(screenshot8), full_page=False)
        screenshots.append(screenshot8)
        
        # Pricing
        print("   → Pricing...")
        page.goto("https://realdiag.netlify.app/pricing", wait_until="networkidle")
        page.wait_for_timeout(2000)
        screenshot9 = OUTPUT_DIR / "09_pricing.png"
        page.screenshot(path=str(screenshot9), full_page=False)
        screenshots.append(screenshot9)
        
        # Back to homepage
        print("   → Homepage final...")
        page.goto("https://realdiag.netlify.app/", wait_until="networkidle")
        page.wait_for_timeout(2000)
        screenshot10 = OUTPUT_DIR / "10_homepage_final.png"
        page.screenshot(path=str(screenshot10), full_page=False)
        screenshots.append(screenshot10)
        
        browser.close()
    
    print(f"✓ Created {len(screenshots)} screenshots")
    return screenshots

def create_video_from_screenshots(screenshots):
    """Create video from screenshots with transitions"""
    print("\n🎬 Creating video from screenshots...")
    
    # Create a concat file for ffmpeg
    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for screenshot in screenshots:
            # Each screenshot shows for 6 seconds
            f.write(f"file '{screenshot.name}'\n")
            f.write("duration 6\n")
        # Repeat last image
        f.write(f"file '{screenshots[-1].name}'\n")
    
    video_file = OUTPUT_DIR / "demo_video.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-vf", "scale=1920:1080,fps=30",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        str(video_file)
    ], cwd=str(OUTPUT_DIR), capture_output=True, text=True)
    
    if result.returncode == 0 and video_file.exists():
        print(f"✓ Video created: {video_file}")
        return video_file
    else:
        print(f"❌ Video creation failed: {result.stderr[:200]}")
        return None

def generate_voiceover():
    """Generate voiceover using 'Real Diagnostic'"""
    print("\n📢 Generating voiceover...")
    print("   Using 'Real Diagnostic' for clarity")
    
    audio_file = OUTPUT_DIR / "voiceover.mp3"
    
    try:
        from gtts import gTTS
    except ImportError:
        subprocess.run(["pip", "install", "-q", "gtts"], check=True)
        from gtts import gTTS
    
    tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
    tts.save(str(audio_file))
    print(f"✓ Audio generated: {audio_file}")
    return audio_file

def combine_video_audio(video_path, audio_path):
    """Combine video and audio"""
    print("\n🎬 Combining video and audio...")
    
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
        print(f"✓ Final video: {final_output}")
        print(f"✓ Size: {size_mb:.1f} MB")
        return final_output
    else:
        print(f"❌ Combine failed: {result.stderr[:200]}")
        return None

def main():
    print("\n" + "="*80)
    print("   REALDIAG SIMPLE DEMO CREATOR")
    print("   Screenshot-based with proper pronunciation")
    print("="*80)
    
    # Step 1: Create screenshots
    screenshots = create_demo_screenshots()
    
    if not screenshots:
        print("\n❌ Failed to create screenshots")
        return
    
    # Step 2: Create video from screenshots
    video = create_video_from_screenshots(screenshots)
    
    if not video:
        print("\n❌ Failed to create video")
        return
    
    # Step 3: Generate voiceover
    audio = generate_voiceover()
    
    # Step 4: Combine
    final_video = combine_video_audio(video, audio)
    
    if final_video:
        print("\n" + "="*80)
        print("✨ SUCCESS!")
        print("="*80)
        print(f"\n📹 {final_video}")
        print(f"📊 {final_video.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"\n✅ Using 'Real Diagnostic' for clear pronunciation")
        print(f"✅ Shows actual website pages and diagnostic tool")
        print(f"\n🚀 Deploy: cp {final_video} ../frontend/public/demo-video.mp4")
    else:
        print("\n❌ Failed to create final video")

if __name__ == "__main__":
    main()
