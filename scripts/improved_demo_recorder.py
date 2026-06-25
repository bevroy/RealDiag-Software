#!/usr/bin/env python3
"""
RealDiag Improved Demo Video Generator
=======================================
Records actual diagnostic features with realistic interactions
"""

import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
WEBSITE_URL = "https://realdiag.netlify.app"
OUTPUT_DIR = Path("demo_output_improved")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Comprehensive demo script showing actual features
DEMO_SCRIPT = [
    # Introduction - Homepage
    {"action": "navigate", "url": "/", "wait": 3, "description": "Show homepage"},
    {"action": "scroll_smooth", "amount": 400, "wait": 2, "description": "Scroll to features"},
    {"action": "scroll_smooth", "amount": 400, "wait": 2, "description": "Continue scrolling"},
    
    # Main Diagnostic Tool
    {"action": "navigate", "url": "/diagnose", "wait": 4, "description": "Open diagnostic tool"},
    {"action": "wait", "wait": 2, "description": "Let page load"},
    {"action": "type_slow", "selector": "input[type='text'], textarea, input[placeholder]", "text": "chest pain", "wait": 1},
    {"action": "wait", "wait": 1, "description": "After typing"},
    {"action": "click", "selector": "button:has-text('Search'), button:has-text('Analyze'), button[type='submit']", "wait": 5},
    {"action": "wait", "wait": 3, "description": "Wait for AI results"},
    {"action": "scroll_smooth", "amount": 300, "wait": 2, "description": "View diagnostic results"},
    {"action": "scroll_smooth", "amount": 300, "wait": 2, "description": "View more results"},
    
    # Try expanding results if available
    {"action": "click_if_exists", "selector": "details, summary, [role='button'], .expand, .accordion", "wait": 2, "index": 0},
    {"action": "scroll_smooth", "amount": 200, "wait": 2, "description": "Show expanded content"},
    
    # Symptom Search
    {"action": "navigate", "url": "/symptom-search", "wait": 3, "description": "Symptom search page"},
    {"action": "type_slow", "selector": "input[type='text'], textarea, input[placeholder]", "text": "shortness of breath", "wait": 1},
    {"action": "wait", "wait": 2, "description": "Show search"},
    {"action": "scroll_smooth", "amount": 300, "wait": 2, "description": "View symptom info"},
    
    # Features Demo
    {"action": "navigate", "url": "/features-demo", "wait": 3, "description": "Features demonstration"},
    {"action": "scroll_smooth", "amount": 400, "wait": 2, "description": "Show features"},
    {"action": "scroll_smooth", "amount": 400, "wait": 2, "description": "Continue features"},
    
    # Integration Page
    {"action": "navigate", "url": "/integration", "wait": 3, "description": "EHR integration"},
    {"action": "scroll_smooth", "amount": 400, "wait": 2, "description": "Show integration options"},
    
    # End on homepage
    {"action": "navigate", "url": "/", "wait": 2, "description": "Back to homepage"},
    {"action": "scroll_to_top", "wait": 1, "description": "Scroll to top"},
]

class ImprovedDemoRecorder:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.browser = None
        self.page = None
        
    async def perform_action(self, action_info):
        """Execute a single demo action with better error handling"""
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
                    # Try multiple common selectors
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
                            await self.page.fill(sel, "")  # Clear first
                            # Type slowly for realistic demo
                            for char in text:
                                await self.page.type(sel, char, delay=100)
                            print(f"   ✓ Successfully typed in: {sel}")
                            break
                        except:
                            continue
                    else:
                        print(f"   ⚠️  No input field found")
                except Exception as e:
                    print(f"   ⚠️  Could not type: {str(e)[:50]}")
                
            elif action_type == "click":
                selector = action_info["selector"]
                print(f"   → Clicking: {selector}")
                try:
                    # Try to find and click the element
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.click(selector, timeout=3000)
                    print(f"   ✓ Clicked successfully")
                except Exception as e:
                    print(f"   ⚠️  Could not click: {str(e)[:50]}")
                    
            elif action_type == "click_if_exists":
                selector = action_info["selector"]
                index = action_info.get("index", 0)
                print(f"   → Trying to click: {selector}")
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements and len(elements) > index:
                        await elements[index].click()
                        print(f"   ✓ Clicked element")
                    else:
                        print(f"   ⚠️  Element not found (optional)")
                except:
                    print(f"   ⚠️  Could not click (optional)")
                
            elif action_type == "scroll_smooth":
                amount = action_info["amount"]
                print(f"   → Smooth scrolling: {amount}px")
                # Smooth scroll with animation
                await self.page.evaluate(f"""
                    window.scrollBy({{
                        top: {amount},
                        left: 0,
                        behavior: 'smooth'
                    }});
                """)
                
            elif action_type == "scroll_to_top":
                print(f"   → Scrolling to top")
                await self.page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
                
            elif action_type == "wait":
                print(f"   → {description or 'Waiting...'}")
                
            # Wait after action
            wait_time = action_info.get("wait", 1)
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            print(f"   ❌ Error in {action_type}: {str(e)[:100]}")
            await asyncio.sleep(1)
    
    async def record_demo(self):
        """Record the full demo"""
        print("\n" + "="*70)
        print("   RealDiag Improved Demo Recorder - Actual Feature Demonstration")
        print("="*70)
        print(f"\n📁 Output directory: {self.output_dir}")
        print(f"🌐 Website: {WEBSITE_URL}")
        print(f"📺 Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
        print(f"\n🎬 Recording {len(DEMO_SCRIPT)} actions...\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = self.output_dir / f"realdiag_demo_improved_{timestamp}.webm"
        
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
            for i, action in enumerate(DEMO_SCRIPT, 1):
                desc = action.get("description", action.get("action", ""))
                print(f"\n📍 Step {i}/{len(DEMO_SCRIPT)}: {desc}")
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
            print(f"   cd {self.output_dir}")
            print(f"   ffmpeg -i {latest_video.name} -c:v libx264 -crf 23 -preset medium realdiag_demo_improved.mp4")
        else:
            print("\n⚠️  No video file found")
        
        return video_files[0] if video_files else None

async def main():
    recorder = ImprovedDemoRecorder()
    await recorder.record_demo()
    print("\n✨ Done! This video shows actual diagnostic features.\n")
    print("📝 Next steps:")
    print("   1. Convert to MP4 using the command above")
    print("   2. Add professional voiceover explaining each feature")
    print("   3. Add background music and title cards")
    print("   4. Upload to website")

if __name__ == "__main__":
    asyncio.run(main())
