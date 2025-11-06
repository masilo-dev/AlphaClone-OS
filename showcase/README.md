# AlphaClone OS Animated Showcase

This directory contains a high-definition animated video showcase of the AlphaClone System OS interface.

## 🎬 Animation Features

The animation demonstrates:

- **Startup Sequence**: AlphaClone logo appears at center, pulses, and expands into the full interface
- **Modular Panels**: Six core modules (WebCore, MobileCore, DashCore, ChatCore, CRMCore, APIHub)
- **Smooth Animations**: 60fps CSS3 animations with smooth transitions
- **Brand Colors**: 
  - Deep Purple: `#7928CA`
  - Neon Cyan: `#00FFFF`
  - Dark Background: `#0B0F19`
  - Accent Blue: `#007AFF`
- **Visual Effects**:
  - Grid lines with pulsing animation
  - Holographic scan overlay
  - Ambient lighting effects
  - Glowing gradients on module activation
  - Matrix-style code visualization
  - Reflection effects

## 📺 Viewing the Animation

### Option 1: Open in Browser

Simply open `alphaclone-os-animation.html` in a modern web browser:

```bash
# From the showcase directory
open alphaclone-os-animation.html

# Or on Linux
xdg-open alphaclone-os-animation.html

# Or on Windows
start alphaclone-os-animation.html
```

The animation will:
1. Start with the AlphaClone logo (0-3 seconds)
2. Expand into the main interface (3-5 seconds)
3. Sequentially activate each module every 3 seconds
4. Loop continuously

### Option 2: Run with a Local Server

For best results, serve the file with a local web server:

```bash
# Using Python
python3 -m http.server 8000

# Using Node.js
npx http-server

# Then open http://localhost:8000/alphaclone-os-animation.html
```

## 🎥 Exporting as Video

### Method 1: Screen Recording (Recommended)

The easiest way to export as a video is to use screen recording:

**On macOS:**
```bash
# QuickTime Player: File > New Screen Recording
# Or use built-in screen recording (Cmd + Shift + 5)
```

**On Windows:**
```bash
# Use built-in Xbox Game Bar (Win + G)
# Or OBS Studio
```

**On Linux:**
```bash
# Use OBS Studio or SimpleScreenRecorder
```

### Method 2: Browser-based Recording

Use browser extensions like:
- **Loom** - Screen recorder extension
- **Screencastify** - Chrome extension
- **Nimbus Screenshot & Screen Video Recorder**

### Method 3: Using Playwright/Puppeteer (Advanced)

For automated high-quality recording:

```javascript
// record-animation.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: './videos/',
      size: { width: 1920, height: 1080 }
    }
  });
  
  const page = await context.newPage();
  await page.goto('file://' + __dirname + '/alphaclone-os-animation.html');
  
  // Record for 30 seconds
  await page.waitForTimeout(30000);
  
  await context.close();
  await browser.close();
})();
```

Then run:
```bash
npm install playwright
node record-animation.js
```

### Method 4: Using FFmpeg with Browser

1. Open the HTML file in Chrome/Firefox
2. Press F12 to open DevTools
3. Use the FPS counter to ensure 60fps
4. Use OBS Studio or FFmpeg to capture the browser window

```bash
# Example FFmpeg command (Linux/macOS)
ffmpeg -video_size 1920x1080 -framerate 60 -f x11grab -i :0.0+0,0 -t 30 alphaclone-os-demo.mp4

# Example FFmpeg command (Windows)
ffmpeg -video_size 1920x1080 -framerate 60 -f gdigrab -i desktop -t 30 alphaclone-os-demo.mp4
```

## 📐 Video Specifications

The animation is designed to meet these specifications:

- **Aspect Ratio**: 16:9 (1920x1080)
- **Duration**: 30 seconds (loopable)
- **Frame Rate**: Smooth 60fps CSS animations
- **Resolution**: 4K ready (scales to any resolution)
- **Format**: HTML5/CSS3 (export to MP4, WebM, or MOV)

## 🎨 Customization

To customize the animation, edit the `alphaclone-os-animation.html` file:

### Change Animation Timing

```javascript
// Auto-cycle interval (currently 3000ms = 3 seconds)
setInterval(() => {
    activateModule(currentIndex);
    currentIndex = (currentIndex + 1) % modules.length;
}, 3000); // Change this value
```

### Modify Colors

```css
/* Edit the CSS variables */
.header-logo {
    background: linear-gradient(135deg, #7928CA 0%, #00FFFF 100%);
}

.module-icon {
    background: linear-gradient(135deg, #7928CA 0%, #007AFF 100%);
}
```

### Adjust Module Content

Find the module sections in the HTML and modify:
- Module titles
- Descriptions
- Matrix code lines
- Icons (using emoji or custom SVG)

## 🚀 Usage in Presentations

This animation is perfect for:

- Product demos
- Marketing videos
- Conference presentations
- Website hero sections
- Social media content
- Documentation videos

## 📋 Technical Details

### Technologies Used

- Pure HTML5, CSS3, JavaScript (no external dependencies)
- CSS Grid for layout
- CSS Animations and Keyframes
- CSS Gradients and Filters
- JavaScript for interactive cycling

### Browser Compatibility

Works best in modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Performance

- Optimized for 60fps
- GPU-accelerated animations
- Minimal JavaScript overhead
- No external assets or network requests

## 📝 License

This animation is part of the AlphaClone-OS project and follows the same MIT license.

---

**Need help?** Open an issue at https://github.com/masilo-dev/AlphaClone-OS/issues
