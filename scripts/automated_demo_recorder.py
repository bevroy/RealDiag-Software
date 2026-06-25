#!/usr/bin/env python3
"""
RealDiag Automated Demo Video Generator
========================================

Uses Playwright for browser automation and edge-tts for AI voiceover
to automatically create a professional demo video.

Requirements:
    pip install playwright edge-tts opencv-python pillow
    playwright install chromium
"""

import asyncio
import time
from pathlib import Path
from datetime import datetime
import subprocess
import json

try:
    from playwright.async_api import async_playwright
    import edge_tts
except ImportError:
    print("Installing required packages...")
    subprocess.run(["pip", "install", "playwright", "edge-tts", "opencv-python", "pillow"])
    print("Installing Playwright browsers...")
    subprocess.run(["playwright", "install", "chromium"])
    from playwright.async_api import async_playwright
    import edge_tts


# Configuration
WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_output")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# AI Voice Configuration (Microsoft Edge TTS - Free)
VOICE = "en-US-JennyNeural"  # Professional female voice
# Alternative voices:
# "en-US-GuyNeural" - Professional male
# "en-US-AriaNeural" - Friendly female
# "en-GB-SoniaNeural" - British female
# "en-GB-RyanNeural" - British male

# Script segments with timing
SCRIPT = [
    {
        "time": 0,
        "text": "Welcome to RealDiag - an AI-powered, real-time diagnostic assistant designed for healthcare professionals.",
        "action": "show_homepage",
        "duration": 7
    },
    {
        "time": 7,
        "text": "RealDiag combines evidence-based clinical decision trees with intelligent symptom analysis to support accurate, efficient diagnosis at the point of care.",
        "action": "scroll_homepage",
        "duration": 8
    },
    {
        "time": 15,
        "text": "With over 400 diagnoses across 24 medical specialties, RealDiag provides comprehensive clinical decision support backed by guidelines from ACC, AHA, ADA, IDSA, KDIGO, and other leading medical organizations.",
        "action": "show_navigation",
        "duration": 10
    },
    {
        "time": 25,
        "text": "Let's start with our symptom-based diagnostic search. This is where most clinicians begin their diagnostic journey.",
        "action": "navigate_to_symptom_search",
        "duration": 5
    },
    {
        "time": 30,
        "text": "I'll demonstrate with a common emergency department presentation: a patient with chest pain.",
        "action": "type_symptom_chest_pain",
        "duration": 5
    },
    {
        "time": 35,
        "text": "The interface provides intelligent autocomplete, helping clinicians quickly enter symptoms using standardized medical terminology.",
        "action": "show_autocomplete",
        "duration": 6
    },
    {
        "time": 41,
        "text": "Let me add a few more presenting symptoms: shortness of breath, diaphoresis, and nausea.",
        "action": "add_more_symptoms",
        "duration": 8
    },
    {
        "time": 49,
        "text": "RealDiag instantly searches across all diagnostic rules and returns ranked differential diagnoses based on symptom matching.",
        "action": "click_search",
        "duration": 6
    },
    {
        "time": 55,
        "text": "Each diagnosis is scored on a 0-10 scale, combining multiple factors: symptom match, sensitivity, specificity, and prevalence.",
        "action": "show_results",
        "duration": 8
    },
    {
        "time": 63,
        "text": "The top result here is Acute Coronary Syndrome with a high match score.",
        "action": "highlight_top_result",
        "duration": 4
    },
    {
        "time": 67,
        "text": "Each diagnosis card provides comprehensive clinical information. We see the ICD-10 code, LOINC codes for relevant lab tests, and most importantly - clinical pearls for bedside decision making.",
        "action": "expand_first_result",
        "duration": 10
    },
    {
        "time": 77,
        "text": "Clinical pearls offer practical insights like 'Troponin may not elevate until 3-6 hours after symptom onset' - critical knowledge that can prevent missed diagnoses.",
        "action": "show_clinical_pearls",
        "duration": 8
    },
    {
        "time": 85,
        "text": "The management section provides evidence-based treatment protocols, including antiplatelet therapy, anticoagulation, and the need for cardiology consultation.",
        "action": "show_management",
        "duration": 8
    },
    {
        "time": 93,
        "text": "And here are the recommended diagnostic tests, including ECG, cardiac biomarkers, and imaging studies - all linked to LOINC codes for easy ordering.",
        "action": "show_tests",
        "duration": 7
    },
    {
        "time": 100,
        "text": "Notice how other life-threatening conditions are also ranked highly: Pulmonary Embolism, Aortic Dissection, Pneumothorax - ensuring critical diagnoses aren't missed.",
        "action": "show_differential",
        "duration": 8
    },
    {
        "time": 108,
        "text": "RealDiag includes advanced clinical decision support features. For time-sensitive conditions, you'll see red flag alerts with pulsing borders.",
        "action": "show_red_flags",
        "duration": 7
    },
    {
        "time": 115,
        "text": "These alerts highlight critical actions that must be taken immediately, time windows for intervention, and mortality risk data.",
        "action": "expand_red_flags",
        "duration": 7
    },
    {
        "time": 122,
        "text": "RealDiag integrates validated clinical decision calculators directly into the diagnostic workflow. For our chest pain patient, relevant calculators include the HEART score for cardiac risk stratification.",
        "action": "show_calculators",
        "duration": 9
    },
    {
        "time": 131,
        "text": "The system also checks for potential drug interactions when multiple medications are recommended in the treatment plan.",
        "action": "show_drug_interactions",
        "duration": 6
    },
    {
        "time": 137,
        "text": "For clinicians on the go, RealDiag includes mobile-optimized features including voice input for hands-free symptom entry and full offline functionality.",
        "action": "show_mobile_features",
        "duration": 8
    },
    {
        "time": 145,
        "text": "RealDiag integrates seamlessly with Epic and other EHR systems using SMART on FHIR standards.",
        "action": "navigate_to_integration",
        "duration": 6
    },
    {
        "time": 151,
        "text": "When launched from within Epic, RealDiag automatically pulls patient demographics, active conditions, current medications, allergies, and recent lab results. This eliminates manual data entry and reduces the risk of errors.",
        "action": "show_integration_diagram",
        "duration": 11
    },
    {
        "time": 162,
        "text": "RealDiag fits naturally into clinical workflow. From the patient chart, clinicians can launch RealDiag with a single click, enter symptoms, review differential diagnoses, and return to the EHR to place orders. The entire process takes 60 to 90 seconds.",
        "action": "show_workflow",
        "duration": 12
    },
    {
        "time": 174,
        "text": "RealDiag offers flexible subscription options for individual clinicians, medical groups, and healthcare organizations.",
        "action": "show_pricing",
        "duration": 6
    },
    {
        "time": 180,
        "text": "RealDiag - AI-Powered Real-Time Diagnostic Assistant. Evidence-based clinical decision support at the point of care. Visit realdiag.netlify.app to start your free trial. Thank you for watching.",
        "action": "show_closing",
        "duration": 12
    }
]


class DemoRecorder:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.screenshots = []
        self.audio_files = []
        self.page = None
        self.browser = None
        self.context = None
        
    async def generate_voiceover(self, segment_index, text):
        """Generate AI voiceover for a segment"""
        audio_file = self.output_dir / f"audio_{segment_index:03d}.mp3"
        
        print(f"  🎤 Generating voiceover: {text[:50]}...")
        
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(audio_file))
        
        self.audio_files.append(audio_file)
        return audio_file
    
    async def take_screenshot(self, name):
        """Take a screenshot"""
        screenshot_file = self.output_dir / f"{name}.png"
        await self.page.screenshot(path=str(screenshot_file), full_page=False)
        self.screenshots.append(screenshot_file)
        return screenshot_file
    
    async def smooth_scroll(self, pixels, duration=1.0):
        """Smooth scroll animation"""
        steps = int(duration * 30)  # 30 steps per second
        step_size = pixels / steps
        
        for i in range(steps):
            await self.page.evaluate(f"window.scrollBy(0, {step_size})")
            await asyncio.sleep(duration / steps)
    
    async def type_slowly(self, selector, text, delay=0.1):
        """Type text with realistic delay"""
        await self.page.fill(selector, "")
        for char in text:
            await self.page.type(selector, char, delay=delay * 1000)
    
    async def perform_action(self, action_name, segment_index):
        """Perform the specified action"""
        print(f"  🎬 Action: {action_name}")
        
        try:
            if action_name == "show_homepage":
                await self.page.goto(WEBSITE_URL, wait_until="networkidle")
                await asyncio.sleep(2)
                await self.take_screenshot(f"frame_{segment_index:03d}_homepage")
            
            elif action_name == "scroll_homepage":
                await self.smooth_scroll(300, duration=3)
                await self.take_screenshot(f"frame_{segment_index:03d}_scrolled")
            
            elif action_name == "show_navigation":
                # Open navigation dropdown
                nav = await self.page.query_selector("details")
                if nav:
                    await nav.click()
                    await asyncio.sleep(1)
                    await self.take_screenshot(f"frame_{segment_index:03d}_navigation")
            
            elif action_name == "navigate_to_symptom_search":
                await self.page.goto(f"{WEBSITE_URL}/symptom-search", wait_until="networkidle")
                await asyncio.sleep(2)
                await self.take_screenshot(f"frame_{segment_index:03d}_symptom_search")
            
            elif action_name == "type_symptom_chest_pain":
                input_selector = "input[placeholder*='symptom' i], input[type='text']"
                await self.page.wait_for_selector(input_selector)
                await self.type_slowly(input_selector, "chest pain", delay=0.15)
                await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_chest_pain")
            
            elif action_name == "show_autocomplete":
                await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_autocomplete")
            
            elif action_name == "add_more_symptoms":
                # Press Enter to add first symptom
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(0.5)
                
                # Add more symptoms
                symptoms = ["shortness of breath", "diaphoresis", "nausea"]
                input_selector = "input[placeholder*='symptom' i], input[type='text']"
                
                for symptom in symptoms:
                    await self.type_slowly(input_selector, symptom, delay=0.1)
                    await self.page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)
                
                await self.take_screenshot(f"frame_{segment_index:03d}_symptoms_added")
            
            elif action_name == "click_search":
                search_button = await self.page.query_selector("button:has-text('Search')")
                if search_button:
                    await search_button.click()
                    await asyncio.sleep(3)  # Wait for results
                    await self.take_screenshot(f"frame_{segment_index:03d}_searching")
            
            elif action_name == "show_results":
                await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_results")
            
            elif action_name == "highlight_top_result":
                # Scroll to top result
                await self.page.evaluate("window.scrollTo(0, 400)")
                await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_top_result")
            
            elif action_name == "expand_first_result":
                # Click first diagnosis card
                result_cards = await self.page.query_selector_all("[style*='cursor: pointer']")
                if result_cards and len(result_cards) > 0:
                    await result_cards[0].click()
                    await asyncio.sleep(2)
                    await self.take_screenshot(f"frame_{segment_index:03d}_expanded")
            
            elif action_name == "show_clinical_pearls":
                await self.smooth_scroll(200, duration=2)
                await self.take_screenshot(f"frame_{segment_index:03d}_pearls")
            
            elif action_name == "show_management":
                await self.smooth_scroll(200, duration=2)
                await self.take_screenshot(f"frame_{segment_index:03d}_management")
            
            elif action_name == "show_tests":
                await self.smooth_scroll(200, duration=2)
                await self.take_screenshot(f"frame_{segment_index:03d}_tests")
            
            elif action_name == "show_differential":
                await self.page.evaluate("window.scrollTo(0, 400)")
                await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_differential")
            
            elif action_name == "show_red_flags":
                await self.smooth_scroll(300, duration=2)
                await self.take_screenshot(f"frame_{segment_index:03d}_red_flags")
            
            elif action_name == "expand_red_flags":
                # Try to find and expand red flags section
                red_flag_details = await self.page.query_selector("details:has-text('Red Flag')")
                if red_flag_details:
                    await red_flag_details.click()
                    await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_red_flags_expanded")
            
            elif action_name == "show_calculators":
                calc_details = await self.page.query_selector("details:has-text('Calculator')")
                if calc_details:
                    await calc_details.click()
                    await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_calculators")
            
            elif action_name == "show_drug_interactions":
                await self.smooth_scroll(200, duration=2)
                await self.take_screenshot(f"frame_{segment_index:03d}_drug_interactions")
            
            elif action_name == "show_mobile_features":
                mobile_toggle = await self.page.query_selector("button:has-text('Mobile')")
                if mobile_toggle:
                    await mobile_toggle.click()
                    await asyncio.sleep(1)
                await self.take_screenshot(f"frame_{segment_index:03d}_mobile")
            
            elif action_name == "navigate_to_integration":
                await self.page.goto(f"{WEBSITE_URL}/integration", wait_until="networkidle")
                await asyncio.sleep(2)
                await self.take_screenshot(f"frame_{segment_index:03d}_integration")
            
            elif action_name == "show_integration_diagram":
                await self.smooth_scroll(400, duration=3)
                await self.take_screenshot(f"frame_{segment_index:03d}_fhir")
            
            elif action_name == "show_workflow":
                await self.smooth_scroll(300, duration=2)
                await self.take_screenshot(f"frame_{segment_index:03d}_workflow")
            
            elif action_name == "show_pricing":
                await self.page.goto(f"{WEBSITE_URL}/pricing", wait_until="networkidle")
                await asyncio.sleep(2)
                await self.take_screenshot(f"frame_{segment_index:03d}_pricing")
            
            elif action_name == "show_closing":
                await self.page.goto(WEBSITE_URL, wait_until="networkidle")
                await asyncio.sleep(2)
                await self.take_screenshot(f"frame_{segment_index:03d}_closing")
            
            else:
                print(f"  ⚠️  Unknown action: {action_name}")
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"  ❌ Error in action {action_name}: {e}")
            await asyncio.sleep(1)
    
    async def record_demo(self):
        """Main recording function"""
        print("🎬 Starting RealDiag Demo Recording...")
        print(f"📁 Output directory: {self.output_dir}")
        
        # Start browser
        print("\n🌐 Launching browser...")
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)  # Headless mode for dev container
            self.context = await self.browser.new_context(
                viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT}
            )
            self.page = await self.context.new_page()
            
            # Process each segment
            total_segments = len(SCRIPT)
            for i, segment in enumerate(SCRIPT):
                print(f"\n📍 Segment {i+1}/{total_segments} (Time: {segment['time']}s)")
                print(f"   Text: {segment['text'][:60]}...")
                
                # Generate voiceover
                audio_file = await self.generate_voiceover(i, segment['text'])
                
                # Perform action
                await self.perform_action(segment['action'], i)
                
                # Wait for segment duration
                wait_time = segment.get('duration', 5)
                print(f"  ⏱️  Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            
            # Close browser
            print("\n🛑 Closing browser...")
            await self.context.close()
            await self.browser.close()
        
        print("\n✅ Recording complete!")
        print(f"📸 Screenshots: {len(self.screenshots)}")
        print(f"🎤 Audio files: {len(self.audio_files)}")
        print(f"\n📁 Output location: {self.output_dir.absolute()}")
        
        # Generate compilation script
        self.generate_compilation_script()
    
    def generate_compilation_script(self):
        """Generate FFmpeg script to compile video"""
        script_file = self.output_dir / "compile_video.sh"
        
        script_content = f"""#!/bin/bash
# RealDiag Demo Video Compilation Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🎬 Compiling RealDiag Demo Video..."

# Concatenate all audio files
echo "🔊 Merging audio files..."
cat audio_*.mp3 > combined_audio.mp3

# Use Playwright's recorded video
echo "🎥 Processing video..."
# The video is automatically saved by Playwright in the output directory

# Combine video and audio (if needed)
VIDEO_FILE=$(ls -t *.webm | head -n 1)
if [ -f "$VIDEO_FILE" ]; then
    echo "✅ Found video: $VIDEO_FILE"
    echo "🎵 Combining with audio..."
    ffmpeg -i "$VIDEO_FILE" -i combined_audio.mp3 -c:v copy -c:a aac -strict experimental \\
        RealDiag_Demo_$(date +%Y%m%d_%H%M%S).mp4
    echo "✅ Demo video created!"
else
    echo "⚠️  No video file found. Please check Playwright recording."
fi

echo ""
echo "📁 Output files:"
ls -lh *.mp4 2>/dev/null || echo "No MP4 files yet"
"""
        
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        print(f"\n📝 Compilation script created: {script_file}")
        print("   Run it with: cd demo_output && ./compile_video.sh")


async def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   RealDiag Automated Demo Video Generator                ║
║   AI-Powered Screen Recording + Text-to-Speech           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    recorder = DemoRecorder()
    await recorder.record_demo()
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║   Next Steps:                                             ║
║   1. Review screenshots in demo_output/                   ║
║   2. Check audio files (audio_*.mp3)                      ║
║   3. Run: cd demo_output && ./compile_video.sh            ║
║   4. Edit final video if needed                           ║
╚═══════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    asyncio.run(main())
