#!/usr/bin/env python3
"""
RealDiag Professional Demo Creator with Voiceover
==================================================
Creates a complete demo video with synchronized AI voiceover
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

# Professional voiceover script
VOICEOVER_SCRIPT = """
Welcome to RealDiag, an AI-powered clinical decision support system.

RealDiag helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

Let me show you how it works.

First, we enter a patient's chief complaint. Let's say a patient presents with chest pain.

RealDiag's AI engine immediately analyzes the symptom and generates a comprehensive differential diagnosis.

As you can see, the system provides ranked diagnostic possibilities, from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic workup.

The system also provides evidence-based treatment guidelines and when to consider specialist referral.

RealDiag integrates seamlessly with your existing EHR system through FHIR and HL7 standards.

Patient data flows automatically, eliminating duplicate data entry and reducing errors.

Our platform includes advanced features like medical calculators, drug interaction checking, and real-time clinical guidelines.

With RealDiag, you can provide better patient care while reducing diagnostic errors and saving valuable time.

Ready to transform your clinical practice? Sign up today at realdiag dot com.
"""

# Timestamps for each voiceover section (in seconds)
VOICEOVER_TIMING = [
    (0, 8, "Welcome to RealDiag, an AI-powered clinical decision support system."),
    (8, 16, "RealDiag helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time."),
    (16, 20, "Let me show you how it works."),
    (20, 28, "First, we enter a patient's chief complaint. Let's say a patient presents with chest pain."),
    (28, 36, "RealDiag's AI engine immediately analyzes the symptom and generates a comprehensive differential diagnosis."),
    (36, 48, "As you can see, the system provides ranked diagnostic possibilities, from most to least likely, based on clinical evidence."),
    (48, 58, "Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic workup."),
    (58, 68, "The system also provides evidence-based treatment guidelines and when to consider specialist referral."),
    (68, 78, "RealDiag integrates seamlessly with your existing EHR system through FHIR and HL7 standards."),
    (78, 88, "Patient data flows automatically, eliminating duplicate data entry and reducing errors."),
    (88, 98, "Our platform includes advanced features like medical calculators, drug interaction checking, and real-time clinical guidelines."),
    (98, 108, "With RealDiag, you can provide better patient care while reducing diagnostic errors and saving valuable time."),
    (108, 115, "Ready to transform your clinical practice? Sign up today at realdiag dot com."),
]

def generate_voiceover_with_gtts():
    """Generate voiceover using Google Text-to-Speech (simpler, works offline)"""
    print("\n📢 Generating voiceover with gTTS...")
    
    output_dir = Path("demo_output_professional")
    output_dir.mkdir(exist_ok=True)
    
    audio_file = output_dir / "voiceover.mp3"
    
    try:
        # Try to use gTTS
        from gtts import gTTS
        tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
        tts.save(str(audio_file))
        print(f"✓ Voiceover generated: {audio_file}")
        return audio_file
    except ImportError:
        print("⚠️  gTTS not installed. Installing...")
        subprocess.run(["pip", "install", "gtts"], check=True)
        from gtts import gTTS
        tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
        tts.save(str(audio_file))
        print(f"✓ Voiceover generated: {audio_file}")
        return audio_file

def combine_video_and_audio(video_path, audio_path, output_path):
    """Combine video with voiceover audio"""
    print(f"\n🎬 Combining video and audio...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Final video created: {output_path}")
        return True
    else:
        print(f"❌ Error combining video and audio:")
        print(result.stderr)
        return False

def create_title_card(text, duration=3):
    """Create a title card using FFmpeg"""
    print(f"Creating title card: {text[:30]}...")
    
    output_dir = Path("demo_output_professional")
    output_dir.mkdir(exist_ok=True)
    
    output = output_dir / f"title_{text[:20].replace(' ', '_')}.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=#0f766e:s=1920x1080:d={duration}",
        "-vf", f"drawtext=text='{text}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        str(output)
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0:
        return output
    else:
        print(f"⚠️  Could not create title card")
        return None

def main():
    print("="*70)
    print("   RealDiag Professional Demo Creator")
    print("   Creates complete video with AI voiceover")
    print("="*70)
    
    output_dir = Path("demo_output_professional")
    output_dir.mkdir(exist_ok=True)
    
    # Use the existing video
    video_path = Path("/workspaces/RealDiag-Software/frontend/public/demo-video.mp4")
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        print("Please run the improved_demo_recorder.py first")
        return
    
    print(f"✓ Found video: {video_path}")
    
    # Generate voiceover
    try:
        audio_path = generate_voiceover_with_gtts()
    except Exception as e:
        print(f"❌ Error generating voiceover: {e}")
        print("\n💡 Alternative: You can record your own voiceover and use:")
        print(f"   ffmpeg -i {video_path} -i your_voiceover.mp3 -c:v copy -c:a aac -shortest final_demo.mp4")
        return
    
    # Combine video and audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = output_dir / f"realdiag_demo_final_{timestamp}.mp4"
    
    success = combine_video_and_audio(video_path, audio_path, final_output)
    
    if success:
        print("\n" + "="*70)
        print("✨ SUCCESS! Professional demo video created!")
        print("="*70)
        print(f"\n📹 Final video: {final_output}")
        print(f"📊 File size: {final_output.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"\n🎯 Next steps:")
        print(f"   1. Review the video")
        print(f"   2. Copy to website: cp {final_output} ../../frontend/public/demo-video.mp4")
        print(f"   3. Commit and deploy")
        print()
    else:
        print("\n❌ Failed to create final video")
        print("Check FFmpeg installation and try again")

if __name__ == "__main__":
    main()
