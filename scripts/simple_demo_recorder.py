#!/usr/bin/env python3
"""
RealDiag Simple Demo Video Generator
=====================================
Creates a screen recording of the demo without voiceover.
You can add voiceover later in a video editor.
"""

import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_output_simple")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Demo actions with timing
DEMO_ACTIONS = [
    {"action": "navigate", "url": "/", "wait": 3, "description": "Homepage"},
    {"action": "scroll", "amount": 500, "wait": 2, "description": "Scroll homepage"},
    {"action": "navigate", "url": "/symptom-search", "wait": 3, "description": "Symptom search"},
    {"action": "type", "selector": "input[placeholder*='symptom' i], input[type='text']", "text": "chest pain", "wait": 2},
    {"action": "click", "selector": "button:has-text('Search'), button:has-text('Analyze')", "wait": 3},
    {"action": "wait_for_results", "wait": 4, "description": "Wait for results"},
    {"action": "scroll", "amount": 300, "wait": 2, "description": "View results"},
    {"action": "click", "selector": "[class*='expand' i], [class*='accordion' i], details, summary", "wait": 2, "index": 0},
    {"action": "scroll", "amount": 400, "wait": 3, "description": "Show details"},
    {"action": "navigate", "url": "/features", "wait": 3, "description": "Features page"},
    {"action": "scroll", "amount": 600, "wait": 2},
    {"action": "scroll", "amount": 600, "wait": 2},
    {"action": "navigate", "url": "/integration", "wait": 3, "description": "Integration page"},
    {"action": "scroll", "amount": 500, "wait": 2},
    {"action": "navigate", "url": "/pricing", "wait": 3, "description": "Pricing page"},
    {"action": "scroll", "amount": 400, "wait": 2},
]

class SimpleDemoRecorder:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.browser = None
        self.page = None
        
    async def perform_action(self, action_info):
        """Execute a single demo action"""
        action_type = action_info.get("action")
        description = action_info.get("description", "")
        
        try:
            if action_type == "navigate":
                url = action_info["url"]
                full_url = f"{WEBSITE_URL}{url}" if url.startswith("/") else url
                print(f"   → Navigating to: {url}")
                await self.page.goto(full_url, wait_until="networkidle", timeout=30000)
                
            elif action_type == "type":
                selector = action_info["selector"]
                text = action_info["text"]
                print(f"   → Typing: {text}")
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.fill(selector, text)
                except Exception as e:
                    print(f"   ⚠️  Could not type (selector not found): {selector}")
                
            elif action_type == "click":
                selector = action_info["selector"]
                index = action_info.get("index", 0)
                print(f"   → Clicking: {selector}")
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements and len(elements) > index:
                        await elements[index].click()
                    else:
                        print(f"   ⚠️  Element not found: {selector}")
                except Exception as e:
                    print(f"   ⚠️  Could not click: {selector}")
                
            elif action_type == "scroll":
                amount = action_info["amount"]
                print(f"   → Scrolling: {amount}px")
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
                
            elif action_type == "wait_for_results":
                print(f"   → Waiting for results to load...")
                await asyncio.sleep(2)
                
            # Wait after action
            wait_time = action_info.get("wait", 1)
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            print(f"   ⚠️  Error in action {action_type}: {str(e)}")
            await asyncio.sleep(1)
    
    async def record_demo(self):
        """Record the full demo"""
        print("\n" + "="*60)
        print("   RealDiag Simple Demo Recorder")
        print("="*60)
        print(f"\n📁 Output directory: {self.output_dir}")
        print(f"🌐 Website: {WEBSITE_URL}")
        print(f"📺 Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
        print(f"\n🎬 Recording {len(DEMO_ACTIONS)} actions...\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = self.output_dir / f"realdiag_demo_{timestamp}.webm"
        
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            self.browser = await p.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                viewport={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT},
                record_video_dir=str(self.output_dir),
                record_video_size={"width": VIDEO_WIDTH, "height": VIDEO_HEIGHT}
            )
            self.page = await self.context.new_page()
            
            # Execute all actions
            for i, action in enumerate(DEMO_ACTIONS, 1):
                desc = action.get("description", action.get("action", ""))
                print(f"\n📍 Action {i}/{len(DEMO_ACTIONS)}: {desc}")
                await self.perform_action(action)
            
            print("\n✅ Recording complete! Saving video...")
            
            # Close and save
            await self.page.close()
            await self.context.close()
            await self.browser.close()
        
        # Find the generated video
        video_files = list(self.output_dir.glob("*.webm"))
        if video_files:
            latest_video = max(video_files, key=lambda p: p.stat().st_mtime)
            print(f"\n🎉 Video saved: {latest_video}")
            print(f"📊 File size: {latest_video.stat().st_size / 1024 / 1024:.1f} MB")
            print(f"\n💡 To convert to MP4:")
            print(f"   ffmpeg -i {latest_video.name} -c:v libx264 -crf 23 -preset medium realdiag_demo.mp4")
        else:
            print("\n⚠️  No video file found")
        
        return video_files[0] if video_files else None

async def main():
    recorder = SimpleDemoRecorder()
    await recorder.record_demo()
    print("\n✨ Done! You can now add voiceover in a video editor.\n")

if __name__ == "__main__":
    asyncio.run(main())
