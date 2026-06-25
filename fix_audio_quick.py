#!/usr/bin/env python3
from gtts import gTTS
from pathlib import Path
import subprocess
from datetime import datetime

# Phonetic: "Real Die Agg"
text = """
Welcome to Real Die Agg, an AI powered clinical decision support system.

Real Die Agg helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real time.

Let me show you how it works.

First, we enter a patient's chief complaint. Let's say a patient presents with chest pain.

Real Die Agg's AI engine immediately analyzes the symptom and generates a comprehensive differential diagnosis.

As you can see, the system provides ranked diagnostic possibilities, from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic workup.

The system also provides evidence based treatment guidelines and when to consider specialist referral.

Real Die Agg integrates seamlessly with your existing EHR system through standard protocols.

Patient data flows automatically, eliminating duplicate data entry and reducing errors.

Our platform includes advanced features like medical calculators, drug interaction checking, and real time clinical guidelines.

With Real Die Agg, you can provide better patient care while reducing diagnostic errors and saving valuable time.

Ready to transform your clinical practice? Sign up today at real die agg dot com.
"""

print("📢 Generating 'Real Die Agg' voiceover...")
audio_file = Path("voiceover_die_agg.mp3")
tts = gTTS(text=text, lang='en', slow=False)
tts.save(str(audio_file))
print(f"✓ Generated: {audio_file}")

print("\n🎬 Replacing audio in existing video...")
output = Path(f"demo_FIXED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

result = subprocess.run([
    "ffmpeg", "-y",
    "-i", "frontend/public/demo-video.mp4",
    "-i", str(audio_file),
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "128k",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-shortest",
    str(output)
], capture_output=True)

if result.returncode == 0:
    print(f"✓ Created: {output}")
    print(f"✓ Size: {output.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\n✅ Pronunciation fixed: 'Real Die Agg'")
    print(f"\n🚀 To deploy: cp {output} frontend/public/demo-video.mp4")
else:
    print(f"❌ Failed: {result.stderr.decode()[:200]}")
