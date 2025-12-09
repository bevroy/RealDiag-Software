#!/usr/bin/env python3
"""
RealDiag Animated Demo Creator with Corrected Voiceover
========================================================
Creates a fully animated demo video with proper pronunciation
"""

import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_output_animated")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Professional voiceover script with corrected pronunciation
# Using "Real Diag" instead of trying to say "RealDiag" as one word
VOICEOVER_SCRIPT = """
Welcome to Real Diag, an AI-powered clinical decision support system.

Real Diag helps healthcare providers make faster, more accurate diagnoses by analyzing patient symptoms in real-time.

Let me show you how it works.

First, we enter a patient's chief complaint. Let's say a patient presents with chest pain.

Real Diag's AI engine immediately analyzes the symptom and generates a comprehensive differential diagnosis.

As you can see, the system provides ranked diagnostic possibilities, from most to least likely, based on clinical evidence.

Each diagnosis includes key clinical features, red flags to watch for, and recommended diagnostic workup.

The system also provides evidence-based treatment guidelines and when to consider specialist referral.

Real Diag integrates seamlessly with your existing EHR system through FHIR and HL7 standards.

Patient data flows automatically, eliminating duplicate data entry and reducing errors.

Our platform includes advanced features like medical calculators, drug interaction checking, and real-time clinical guidelines.

With Real Diag, you can provide better patient care while reducing diagnostic errors and saving valuable time.

Ready to transform your clinical practice? Sign up today at real diag dot com.
"""

# Detailed animation script synchronized with voiceover
ANIMATION_SCRIPT = [
    # 0-8s: Welcome to Real Diag
    {"action": "navigate", "url": "/", "wait": 2, "description": "Show homepage with logo"},
    {"action": "wait", "wait": 3, "description": "Display homepage"},
    {"action": "scroll_smooth", "amount": 300, "wait": 3, "description": "Show hero section"},
    
    # 8-16s: Real Diag helps healthcare providers
    {"action": "scroll_smooth", "amount": 400, "wait": 2, "description": "Scroll to benefits"},
    {"action": "wait", "wait": 3, "description": "Show key benefits"},
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Show more features"},
    
    # 16-20s: Let me show you how it works
    {"action": "scroll_to_top", "wait": 1, "description": "Back to top"},
    {"action": "wait", "wait": 3, "description": "Prepare for demo"},
    
    # 20-28s: Enter patient's chief complaint - chest pain
    {"action": "navigate", "url": "/diagnose", "wait": 2, "description": "Open diagnostic tool"},
    {"action": "wait", "wait": 2, "description": "Show diagnostic interface"},
    {"action": "type_slow", "selector": "input[type='text'], textarea, input[placeholder]", "text": "chest pain", "wait": 1, "description": "Type chief complaint"},
    {"action": "wait", "wait": 3, "description": "Show entered symptom"},
    
    # 28-36s: AI engine analyzes and generates differential diagnosis
    {"action": "click", "selector": "button:has-text('Search'), button:has-text('Analyze'), button:has-text('Diagnose'), button[type='submit']", "wait": 2, "description": "Click analyze"},
    {"action": "wait", "wait": 4, "description": "AI processing animation"},
    {"action": "scroll_smooth", "amount": 200, "wait": 2, "description": "Show AI results appearing"},
    
    # 36-48s: System provides ranked diagnostic possibilities
    {"action": "scroll_smooth", "amount": 300, "wait": 3, "description": "Show differential diagnosis list"},
    {"action": "wait", "wait": 2, "description": "Display ranked conditions"},
    {"action": "scroll_smooth", "amount": 300, "wait": 3, "description": "Show more diagnoses"},
    {"action": "wait", "wait": 4, "description": "Highlight evidence-based ranking"},
    
    # 48-58s: Each diagnosis includes clinical features and red flags
    {"action": "click_if_exists", "selector": "details, summary, .expand, .accordion, [role='button']", "wait": 2, "index": 0, "description": "Expand first diagnosis"},
    {"action": "scroll_smooth", "amount": 200, "wait": 2, "description": "Show detailed information"},
    {"action": "wait", "wait": 3, "description": "Display clinical features"},
    {"action": "scroll_smooth", "amount": 200, "wait": 3, "description": "Show red flags and workup"},
    
    # 58-68s: Treatment guidelines and specialist referral
    {"action": "scroll_smooth", "amount": 300, "wait": 3, "description": "Show treatment section"},
    {"action": "wait", "wait": 3, "description": "Display guidelines"},
    {"action": "scroll_smooth", "amount": 200, "wait": 4, "description": "Show referral criteria"},
    
    # 68-78s: Real Diag integrates with EHR systems
    {"action": "navigate", "url": "/integration", "wait": 2, "description": "Integration page"},
    {"action": "wait", "wait": 2, "description": "Show EHR integration"},
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Display FHIR/HL7 info"},
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Show integration options"},
    
    # 78-88s: Patient data flows automatically
    {"action": "scroll_smooth", "amount": 300, "wait": 3, "description": "Show data flow diagram"},
    {"action": "wait", "wait": 3, "description": "Highlight automation"},
    {"action": "scroll_smooth", "amount": 200, "wait": 4, "description": "Show security features"},
    
    # 88-98s: Advanced features - calculators, drug interactions
    {"action": "navigate", "url": "/features-demo", "wait": 2, "description": "Features demo page"},
    {"action": "wait", "wait": 2, "description": "Show feature overview"},
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Display medical calculators"},
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Show drug interaction checker"},
    
    # 98-108s: Better patient care, reduced errors
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Show clinical guidelines"},
    {"action": "wait", "wait": 3, "description": "Highlight benefits"},
    {"action": "scroll_smooth", "amount": 300, "wait": 4, "description": "Display outcome metrics"},
    
    # 108-115s: Sign up today at real diag dot com
    {"action": "navigate", "url": "/pricing", "wait": 2, "description": "Pricing page"},
    {"action": "wait", "wait": 2, "description": "Show subscription options"},
    {"action": "scroll_smooth", "amount": 400, "wait": 3, "description": "Display pricing tiers"},
    {"action": "navigate", "url": "/", "wait": 1, "description": "Back to homepage"},
    {"action": "scroll_to_top", "wait": 1, "description": "End on logo"},
]

class AnimatedDemoRecorder:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.browser = None
        self.page = None
        
    async def perform_action(self, action_info):
        """Execute a single demo action with smooth animations"""
        action_type = action_info.get("action")
        description = action_info.get("description", "")
        
        try:
            if action_type == "navigate":
                url = action_info["url"]
                full_url = f"{WEBSITE_URL}{url}" if url.startswith("/") else url
                print(f"   → {description or f'Navigate to {url}'}")
                await self.page.goto(full_url, wait_until="networkidle", timeout=30000)
                
            elif action_type == "type_slow":
                selector = action_info["selector"]
                text = action_info["text"]
                print(f"   → Typing: '{text}'")
                try:
                    # Try multiple selectors
                    selectors = [
                        selector,
                        "input[type='text']",
                        "textarea",
                        "input[placeholder*='symptom' i]",
                        "input[placeholder*='search' i]",
                        "input.search",
                        "[contenteditable='true']"
                    ]
                    
                    for sel in selectors:
                        try:
                            await self.page.wait_for_selector(sel, timeout=3000)
                            await self.page.click(sel)
                            await self.page.fill(sel, "")
                            # Realistic typing speed
                            for char in text:
                                await self.page.type(sel, char, delay=150)
                            print(f"   ✓ Typed successfully")
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"   ⚠️  Could not type: {str(e)[:50]}")
                
            elif action_type == "click":
                selector = action_info["selector"]
                print(f"   → Clicking button")
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    # Hover before clicking for visual effect
                    await self.page.hover(selector)
                    await asyncio.sleep(0.3)
                    await self.page.click(selector, timeout=3000)
                    print(f"   ✓ Clicked successfully")
                except Exception as e:
                    print(f"   ⚠️  Could not click: {str(e)[:50]}")
                    
            elif action_type == "click_if_exists":
                selector = action_info["selector"]
                index = action_info.get("index", 0)
                print(f"   → {description}")
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements and len(elements) > index:
                        await elements[index].scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await elements[index].click()
                        print(f"   ✓ Expanded section")
                except:
                    print(f"   ⚠️  Element not found (optional)")
                
            elif action_type == "scroll_smooth":
                amount = action_info["amount"]
                print(f"   → {description}")
                # Very smooth scroll
                await self.page.evaluate(f"""
                    window.scrollBy({{
                        top: {amount},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)
                
            elif action_type == "scroll_to_top":
                print(f"   → {description}")
                await self.page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                
            elif action_type == "wait":
                print(f"   → {description}")
                
            # Wait after action
            wait_time = action_info.get("wait", 1)
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            await asyncio.sleep(1)
    
    async def record_video(self):
        """Record the animated demo"""
        print("\n" + "="*70)
        print("   RealDiag Animated Demo Recorder")
        print("   Full Animation + Corrected Pronunciation")
        print("="*70)
        print(f"\n📁 Output: {self.output_dir}")
        print(f"🌐 Website: {WEBSITE_URL}")
        print(f"📺 Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
        print(f"⏱️  Duration: ~115 seconds")
        print(f"\n🎬 Recording {len(ANIMATION_SCRIPT)} animated actions...\n")
        
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            self.browser = await p.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT}
            )
            self.page = await self.context.new_page()
            
            # Execute animation script
            for i, action in enumerate(ANIMATION_SCRIPT, 1):
                desc = action.get("description", "Action")
                print(f"\n📍 Step {i}/{len(ANIMATION_SCRIPT)}: {desc}")
                await self.perform_action(action)
            
            print("\n✅ Recording complete! Saving video...")
            
            await self.page.close()
            await self.context.close()
            await self.browser.close()
        
        # Find the generated video
        video_files = list(self.output_dir.glob("*.webm"))
        if video_files:
            latest_video = max(video_files, key=lambda p: p.stat().st_mtime)
            print(f"\n🎉 Video recorded: {latest_video}")
            print(f"📊 Size: {latest_video.stat().st_size / 1024 / 1024:.1f} MB")
            return latest_video
        return None

def generate_corrected_voiceover():
    """Generate voiceover with corrected pronunciation"""
    print("\n📢 Generating voiceover with corrected pronunciation...")
    print("   Using 'Real Diag' instead of 'RealDiag'")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    audio_file = OUTPUT_DIR / "voiceover_corrected.mp3"
    
    try:
        from gtts import gTTS
        tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
        tts.save(str(audio_file))
        print(f"✓ Voiceover generated: {audio_file}")
        return audio_file
    except ImportError:
        print("⚠️  Installing gTTS...")
        subprocess.run(["pip", "install", "gtts"], check=True)
        from gtts import gTTS
        tts = gTTS(text=VOICEOVER_SCRIPT, lang='en', slow=False)
        tts.save(str(audio_file))
        print(f"✓ Voiceover generated: {audio_file}")
        return audio_file

def convert_to_mp4(webm_path):
    """Convert webm to MP4 with better quality"""
    print(f"\n🎬 Converting to MP4...")
    
    mp4_path = webm_path.parent / webm_path.name.replace(".webm", ".mp4")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(webm_path),
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        str(mp4_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ MP4 created: {mp4_path}")
        return mp4_path
    else:
        print(f"❌ Conversion failed")
        return None

def combine_video_and_audio(video_path, audio_path, output_path):
    """Combine animated video with corrected voiceover"""
    print(f"\n🎬 Combining animation and voiceover...")
    
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
        print(f"✓ Final video: {output_path}")
        print(f"📊 Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    else:
        print(f"❌ Error combining files")
        print(result.stderr)
        return False

async def main():
    print("="*70)
    print("   RealDiag Complete Animated Demo Creator")
    print("="*70)
    
    # Step 1: Record animated video
    recorder = AnimatedDemoRecorder()
    webm_video = await recorder.record_video()
    
    if not webm_video:
        print("\n❌ Failed to record video")
        return
    
    # Step 2: Convert to MP4
    mp4_video = convert_to_mp4(webm_video)
    
    if not mp4_video:
        print("\n❌ Failed to convert to MP4")
        return
    
    # Step 3: Generate corrected voiceover
    try:
        audio = generate_corrected_voiceover()
    except Exception as e:
        print(f"❌ Failed to generate voiceover: {e}")
        return
    
    # Step 4: Combine video and audio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = OUTPUT_DIR / f"realdiag_demo_final_{timestamp}.mp4"
    
    success = combine_video_and_audio(mp4_video, audio, final_output)
    
    if success:
        print("\n" + "="*70)
        print("✨ SUCCESS! Animated demo with corrected voiceover created!")
        print("="*70)
        print(f"\n📹 Final video: {final_output}")
        print(f"📊 File size: {final_output.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"⏱️  Duration: ~115 seconds (1:55)")
        print(f"\n✅ Improvements:")
        print(f"   • Full animation (no static screenshots)")
        print(f"   • Corrected pronunciation: 'Real Diag'")
        print(f"   • Synchronized with voiceover")
        print(f"\n🎯 Next steps:")
        print(f"   1. Review the video: {final_output}")
        print(f"   2. Deploy: cp {final_output} ../frontend/public/demo-video.mp4")
        print(f"   3. Commit and push changes")
        print()
    else:
        print("\n❌ Failed to create final video")

if __name__ == "__main__":
    asyncio.run(main())
