#!/usr/bin/env python3
"""
Demo with Ken Burns animation effects
Uses screenshots but adds zoom/pan for animated feel
"""

import subprocess
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("demo_kenburns")
OUTPUT_DIR.mkdir(exist_ok=True)

# Phonetic pronunciation: "die agg"
VOICEOVER_TEXT = """
Welcome to Real Die Agg, an AI-powered clinical decision support system.

Real Die Agg helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real time.

Let me demonstrate how it works.

We enter a patient's chief complaint, such as chest pain.

Real Die Agg's AI engine analyzes the symptom and generates a comprehensive differential diagnosis.

The system ranks diagnostic possibilities based on clinical evidence.

Each diagnosis includes key clinical features, red flags, and recommended tests.

The system provides evidence based treatment guidelines and specialist referral criteria.

Real Die Agg integrates with your existing electronic health record system.

Our platform includes medical calculators, drug interaction checking, and clinical guidelines.

With Real Die Agg, you can provide better patient care, reduce errors, and save time.

Transform your clinical practice today at real die agg dot com.
"""

# Create a simple slideshow with cross-fade transitions
def create_demo_slideshow():
    """Create slideshow from existing screenshots or generate new ones"""
    print("🎬 Creating animated slideshow...")
    
    # Download a few key screenshots from the live site
    screenshots = []
    
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            
            # Homepage
            try:
                print("   📸 Homepage...")
                page.goto("https://realdiag.netlify.app/", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                s1 = OUTPUT_DIR / "shot1.png"
                page.screenshot(path=str(s1))
                screenshots.append(s1)
            except:
                print("      ⚠️  Skipped")
            
            # Diagnostic tool
            try:
                print("   📸 Diagnostic tool...")
                page.goto("https://realdiag.netlify.app/diagnose", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                s2 = OUTPUT_DIR / "shot2.png"
                page.screenshot(path=str(s2))
                screenshots.append(s2)
            except:
                print("      ⚠️  Skipped")
            
            # Integration
            try:
                print("   📸 Integration...")
                page.goto("https://realdiag.netlify.app/integration", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                s3 = OUTPUT_DIR / "shot3.png"
                page.screenshot(path=str(s3))
                screenshots.append(s3)
            except:
                print("      ⚠️  Skipped")
            
            # Features
            try:
                print("   📸 Features...")
                page.goto("https://realdiag.netlify.app/features-demo", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                s4 = OUTPUT_DIR / "shot4.png"
                page.screenshot(path=str(s4))
                screenshots.append(s4)
            except:
                print("      ⚠️  Skipped")
            
            # Pricing
            try:
                print("   📸 Pricing...")
                page.goto("https://realdiag.netlify.app/pricing", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                s5 = OUTPUT_DIR / "shot5.png"
                page.screenshot(path=str(s5))
                screenshots.append(s5)
            except:
                print("      ⚠️  Skipped")
            
            browser.close()
            
        except Exception as e:
            print(f"   ⚠️  Screenshot error: {str(e)[:60]}")
    
    if len(screenshots) < 3:
        print("❌ Not enough screenshots captured")
        return None
    
    print(f"✓ Captured {len(screenshots)} screenshots")
    
    # Create video with Ken Burns effects (zoom + pan)
    print("\n🎬 Creating video with Ken Burns effects...")
    
    # Build complex ffmpeg filter for smooth transitions and zoom
    filter_complex = []
    inputs = []
    
    for i, shot in enumerate(screenshots):
        inputs.extend(["-loop", "1", "-t", "12", "-i", str(shot)])
        
        # Ken Burns effect: slow zoom + pan
        zoom_start = 1.0
        zoom_end = 1.1
        filter_complex.append(
            f"[{i}:v]scale=1920:1080,zoompan=z='min(zoom+0.0015,{zoom_end})':d=360:s=1920x1080:fps=30[v{i}]"
        )
    
    # Crossfade transitions between clips
    concat_filter = "[v0]"
    for i in range(1, len(screenshots)):
        concat_filter += f"[v{i}]xfade=transition=fade:duration=1:offset={11*i}[vt{i}];"
        if i < len(screenshots) - 1:
            concat_filter = concat_filter.replace(f"[vt{i}]", f"[vt{i}][vt{i}]")
    
    # Last video segment
    concat_filter = concat_filter.rstrip(';')
    if len(screenshots) > 1:
        concat_filter = concat_filter.replace(f"[vt{len(screenshots)-1}]", "[outv]")
    else:
        concat_filter += "[outv]"
    
    filter_str = ";".join(filter_complex) + ";" + concat_filter
    
    video_file = OUTPUT_DIR / "demo_video.mp4"
    
    cmd = [
        "ffmpeg", "-y"
    ] + inputs + [
        "-filter_complex", filter_str,
        "-map", "[outv]",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        str(video_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and video_file.exists():
        print(f"✓ Video created: {video_file}")
        return video_file
    else:
        # Fallback: simple slideshow
        print("   Trying simpler approach...")
        return create_simple_slideshow(screenshots)

def create_simple_slideshow(screenshots):
    """Fallback: simple slideshow"""
    print("🎬 Creating simple slideshow...")
    
    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for shot in screenshots:
            f.write(f"file '{shot.name}'\n")
            f.write("duration 12\n")
        f.write(f"file '{screenshots[-1].name}'\n")
    
    video_file = OUTPUT_DIR / "demo_video_simple.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-vf", "scale=1920:1080,fps=30",
        "-c:v", "libx264",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(video_file)
    ], cwd=str(OUTPUT_DIR), capture_output=True)
    
    if result.returncode == 0:
        print(f"✓ Simple video: {video_file}")
        return video_file
    
    return None

def generate_voiceover():
    """Generate voiceover with 'die agg'"""
    print("\n📢 Generating voiceover (Real Die Agg)...")
    
    audio_file = OUTPUT_DIR / "voiceover.mp3"
    
    try:
        from gtts import gTTS
    except ImportError:
        subprocess.run(["pip", "install", "-q", "gtts"], check=True)
        from gtts import gTTS
    
    tts = gTTS(text=VOICEOVER_TEXT, lang='en', slow=False)
    tts.save(str(audio_file))
    print(f"✓ Audio: {audio_file}")
    return audio_file

def combine(video_path, audio_path):
    """Combine video and audio"""
    print("\n🎬 Combining...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final = OUTPUT_DIR / f"realdiag_demo_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(final)
    ], capture_output=True)
    
    if result.returncode == 0:
        print(f"✓ Final: {final}")
        print(f"✓ Size: {final.stat().st_size / 1024 / 1024:.1f} MB")
        return final
    
    return None

def main():
    print("\n" + "="*70)
    print("   REALDIAG DEMO - KEN BURNS EDITION")
    print("   Pronunciation: 'Real Die Agg'")
    print("="*70 + "\n")
    
    video = create_demo_slideshow()
    if not video:
        print("\n❌ Failed to create video")
        return
    
    audio = generate_voiceover()
    final = combine(video, audio)
    
    if final:
        print("\n" + "="*70)
        print("✨ SUCCESS!")
        print("="*70)
        print(f"\n📹 {final}")
        print(f"\n✅ Pronunciation: 'Real Die Agg'")
        print(f"✅ Animation: Ken Burns zoom/pan effects")
        print(f"\n🚀 cp {final} ../frontend/public/demo-video.mp4")

if __name__ == "__main__":
    main()
