# RealDiag Automated Demo Video - Setup Guide

## 🤖 AI-Powered Demo Recording

This automated system creates professional demo videos using:
- **Playwright** - Browser automation for screen recording
- **Edge TTS** - Microsoft's free AI text-to-speech
- **Python** - Orchestration and timing

---

## 📋 Quick Start

### Option 1: Automated Python Script (Recommended)

1. **Install dependencies:**
```bash
cd scripts
pip install -r requirements_demo.txt
playwright install chromium
```

2. **Run the recorder:**
```bash
python automated_demo_recorder.py
```

3. **Wait 3-5 minutes** while the AI navigates the site and generates voiceover

4. **Compile the final video:**
```bash
cd demo_output
./compile_video.sh
```

**Output:** `RealDiag_Demo_YYYYMMDD_HHMMSS.mp4`

---

### Option 2: Cloud-Based (No Installation)

Use **Synthesia.io** or **Loom AI**:

#### Synthesia.io (Premium):
1. Sign up at https://synthesia.io
2. Upload DEMO_VIDEO_SCRIPT.md
3. Choose AI avatar (professional healthcare presenter)
4. Select voice (US English, professional)
5. Generate video automatically
6. **Cost:** ~$30/month or $0.16/minute

#### Loom AI (Simpler):
1. Install Loom extension
2. Record screen manually
3. Use Loom AI to:
   - Auto-generate transcript
   - Add AI voiceover
   - Edit and trim
4. **Cost:** Free tier available

---

### Option 3: Manual Recording with AI Voice

1. **Generate voiceover only:**
```bash
python generate_voiceover_only.py
```
This creates audio files in `demo_output/audio_*.mp3`

2. **Record screen manually** using OBS Studio

3. **Sync in video editor** (DaVinci Resolve, Premiere)

---

## 🎙️ Voice Options

### Microsoft Edge TTS (Free, High Quality):
- `en-US-JennyNeural` - Professional female (recommended)
- `en-US-GuyNeural` - Professional male
- `en-US-AriaNeural` - Friendly, conversational
- `en-GB-SoniaNeural` - British female
- `en-GB-RyanNeural` - British male

### To change voice:
Edit `automated_demo_recorder.py`, line 25:
```python
VOICE = "en-US-GuyNeural"  # Change here
```

---

## 🎬 How It Works

### Automated Recording Process:

1. **Browser Launch** - Opens Chrome in 1920x1080
2. **Navigate Site** - Goes through each page automatically
3. **Actions** - Types, clicks, scrolls as scripted
4. **Screenshots** - Captures frames at key moments
5. **Voiceover** - Generates AI narration for each segment
6. **Video Recording** - Playwright records full session
7. **Compilation** - FFmpeg combines video + audio

### Timeline (192 seconds = 3 minutes 12 seconds):
- 0:00-0:25 - Introduction & homepage
- 0:25-1:49 - Symptom search demo (chest pain)
- 1:49-2:17 - Advanced features (red flags, calculators)
- 2:17-3:00 - EHR integration & pricing
- 3:00-3:12 - Closing

---

## 🛠️ Customization

### Change Script:
Edit `SCRIPT` array in `automated_demo_recorder.py`:
```python
SCRIPT = [
    {
        "time": 0,
        "text": "Your custom narration here",
        "action": "show_homepage",
        "duration": 7
    },
    # Add more segments...
]
```

### Change Timing:
Adjust `duration` values to make sections longer/shorter

### Change Voice Speed:
```python
# In generate_voiceover() function:
communicate = edge_tts.Communicate(text, VOICE, rate="+10%")  # Faster
# or
communicate = edge_tts.Communicate(text, VOICE, rate="-10%")  # Slower
```

---

## 🎨 Post-Production

The automated script creates a basic video. For polish:

1. **Import to DaVinci Resolve** (free) or Premiere Pro
2. **Add title cards:**
   - Opening: "RealDiag - Clinical Decision Support"
   - Section markers: "Symptom Search", "Advanced Features"
3. **Add background music** (low volume)
4. **Color grade** (optional)
5. **Add transitions** between sections
6. **Export final video**

---

## 📊 Quality Settings

### Current Settings:
- **Resolution:** 1920x1080 (1080p)
- **Frame Rate:** 30fps
- **Video Codec:** H.264
- **Audio:** AAC, 128kbps

### To Change:
Edit `automated_demo_recorder.py`:
```python
VIDEO_WIDTH = 1920   # Change to 3840 for 4K
VIDEO_HEIGHT = 1080  # Change to 2160 for 4K
FPS = 30            # Change to 60 for smoother motion
```

---

## 🐛 Troubleshooting

### "Playwright not found"
```bash
playwright install chromium
```

### "edge-tts fails"
- Check internet connection
- Try alternative voice
- Use pyttsx3 for offline TTS

### Video quality issues:
- Increase bitrate in FFmpeg command
- Record at 4K then downscale
- Use lossless codec during editing

### Audio sync issues:
- Check segment timing in SCRIPT
- Adjust duration values
- Use video editor to manually sync

### Slow website loading:
- Increase `asyncio.sleep()` times
- Check internet speed
- Use local development version

---

## 💰 Cost Comparison

| Method | Cost | Quality | Time | Skill Level |
|--------|------|---------|------|-------------|
| Automated Python | Free | Good | 5 min | Medium |
| Synthesia.io | $30/mo | Excellent | 10 min | Easy |
| Manual + AI Voice | Free | Great | 30 min | Medium |
| Professional Studio | $500+ | Excellent | 2-3 days | N/A |

---

## 📚 Resources

- **Edge TTS Voices:** https://speech.microsoft.com/portal/voicegallery
- **Playwright Docs:** https://playwright.dev/python/
- **FFmpeg Guide:** https://ffmpeg.org/ffmpeg.html
- **Synthesia.io:** https://synthesia.io
- **DaVinci Resolve:** https://www.blackmagicdesign.com/products/davinciresolve

---

## 🎯 Next Steps

1. **Test the automated recorder** with default settings
2. **Review the output** - check audio quality and timing
3. **Tweak as needed** - adjust voice, speed, timing
4. **Polish in video editor** - add branding, music
5. **Publish** to YouTube, Vimeo, website

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements_demo.txt`)
- [ ] Playwright browsers installed
- [ ] Script runs without errors
- [ ] Video output created in demo_output/
- [ ] Audio quality acceptable
- [ ] Timing matches expectations
- [ ] Final video exported
- [ ] Uploaded to hosting platform

---

**Questions?** Contact support@realdiag.org
