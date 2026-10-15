# Research Deep Dive: Technical Execution & Workflow

Based on the Perplexity research run for Mega-Prompt #3, here is the masterclass breakdown of the state-of-the-art AI video workflow required to maintain character consistency and handle complex destruction.

---

## 1. The Core Strategy: Decoupling
The biggest mistake solo creators make is trying to generate the character *and* the destruction in a single text-to-video prompt (which leads to melting and morphing). 

The secret pipeline treats:
*   **Character Consistency** as an image problem.
*   **Destruction** as a separate text-to-video physics problem.
*   **Storytelling** as a compositing problem in post-production.

---

## 2. Character Consistency (The "Freeze")
You must define the character once at high quality and reuse that definition. 

### The Image Workflow
1.  **Design Session:** Use Midjourney (or Flux) to design 20-40 images of Alf in different poses on neutral backgrounds. 
2.  **Character Bible:** Save the best 5 "hero" images.
3.  **Prompt Discipline:** Use Midjourney's Character Reference (`--cref`) or train a quick LoRA on those images. Always use the exact same text descriptor string: *"chubby orange tabby cat, tiny neon green leg warmers, pink sweatband..."*

---

## 3. Motion & Physics (The Destruction)
When generating the disaster using Runway Gen-3, Luma, or Kling, **do not include the cat in the prompt.** Ask the model to solve only the environment physics.

### Structuring Destruction Prompts
Text-to-video models respond best to highly structured, timeline-based prompts:
*   **0-1s (Setup):** "A brightly lit 1980s aerobics studio with mirrored walls..."
*   **1-3s (Cause):** "Suddenly, a massive iron wrecking ball crashes through the mirrors..."
*   **3-5s (Debris):** "Glass explodes outward, dust fills the air, heavy rigid debris falls."
*   **Camera:** "Static camera on a tripod, realistic physics, no people, no animals."

*Note:* Adding phrases like "rigid bodies, heavy chunks" prevents the debris from looking rubbery or melting.

---

## 4. The Compositing Layer (Where it comes together)
This is where you spend your time. 

### The Assembly Line
1.  **Generate Background Video:** The 4-second wrecking ball crash.
2.  **Generate Cat Performance:** A static image (or very simple 2-second video on a white background) of Alf looking deadpan. 
3.  **Rotoscope / Mask:** Use an AI masking tool in CapCut or After Effects to cut Alf out of his background.
4.  **Composite:** Drop Alf on top of the destruction video. 
5.  **Sell the Effect:** This is the most important step. Add a global **camera shake** to the entire composition at the moment of impact. Add a soft shadow under Alf, and put a slight dust/glow overlay *on top* of him so he feels seated in the environment. 

### Efficiency
Once you build a library of "Alf poses" (transparent PNGs), you only have to generate the background destruction video for each new short. This is how you can easily scale to producing 3 high-quality shorts per week.
