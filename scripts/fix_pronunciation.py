#!/usr/bin/env python3
"""
Quick Fix: Just regenerate audio with correct pronunciation
"""

import subprocess
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("demo_audio_fix")
OUTPUT_DIR.mkdir(exist_ok=True)

# Say it as "Real Diagnostic" for proper pronunciation
# Avoid "Diag" which gets mispronounced as "die agg"
VOICEOVER_TEXT = """
Welcome to Real Diagnostic, an A I powered clinical decision support system.

Real Diagnostic helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real time.

Let me show you how it works.

First, we enter a patient's chief complaint. Let's say a patient presents with chest pain.

Real Diagnostic's A I engine immediately analyzes the symptom and generates a comprehensive differential diagnosis.

As you can see, the system provides ranked diagnostic possibilities, from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic workup.

The system also provides evidence based treatment guidelines and when to consider specialist referral.

Real Diagnostic integrates seamlessly with your existing E H R system through standard protocols.

Patient data flows automatically, eliminating duplicate data entry and reducing errors.

Our platform includes advanced features like medical calculators, drug interaction checking, and real time clinical guidelines.

With Real Diagnostic, you can provide better patient care while reducing diagnostic errors and saving valuable time.

Ready to transform your clinical practice? Sign up today at real diagnostic dot com.
"""

def generate_audio():
    """Generate voiceover"""
    print("📢 Generating voiceover with 'Real Diagnostic'...")
    
    audio_file = OUTPUT_DIR / "voiceover_fixed.mp3"
    
    try:
        from gtts import gTTS
        tts = gTTS(text=VOICEOVER_TEXT, lang='en', slow=False)
        tts.save(str(audio_file))
        print(f"✓ Generated: {audio_file}")
        return audio_file
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

def combine_with_existing_video(audio_path):
    """Combine new audio with existing video"""
    print("\n🎬 Combining with existing video...")
    
    video_input = Path("frontend/public/demo-video.mp4")
    if not video_input.exists():
        print(f"❌ Video not found: {video_input}")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = OUTPUT_DIR / f"demo_pronunciation_fixed_{timestamp}.mp4"
    
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_input),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        size = output.stat().st_size / 1024 / 1024
        print(f"✓ Created: {output}")
        print(f"✓ Size: {size:.1f} MB")
        return output
    else:
        print(f"❌ Failed: {result.stderr[:300]}")
        return None

def main():
    print("\n" + "="*70)
    print("   QUICK PRONUNCIATION FIX")
    print("   Using 'Real Diagnostic' instead of 'RealDiag'")
    print("="*70 + "\n")
    
    # Generate new audio
    audio = generate_audio()
    if not audio:
        return
    
    # Combine with existing video
    final = combine_with_existing_video(audio)
    
    if final:
        print("\n" + "="*70)
        print("✨ SUCCESS!")
        print("="*70)
        print(f"\n📹 {final}")
        print(f"\n✅ Pronunciation fixed: 'Real Diagnostic'")
        print(f"\n🚀 To deploy:")
        print(f"   cp {final} frontend/public/demo-video.mp4")
        print(f"   git add frontend/public/demo-video.mp4")
        print(f"   git commit -m 'Fix pronunciation in demo video'")
        print(f"   git push")
        print()

if __name__ == "__main__":
    main()
