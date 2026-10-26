# SPEC: Insurance Pricing product demo

> v2 (owner feedback, `../demo-insurance-pricing-v2.mp4`): 61.0 s. Chapter cards are kinetic headline cards, 2.4 s,
> centred on both axes (sheet whips in/out with the emerald bar on its edge, ghost type sweeps to ink word by word,
> emerald rule under the accent word, one motion graphic per card). Push-ins isolate their panel (the other panels fade
> to the ground) and centre it inside the 5% safe area; wide shots centre the 976 px content column. Music fades
> 57.6-60.4 s, silence to 61.0 s. Times below are v1; `R()` in src/app.timeline.js maps them (-0.6 s after 21.6 s,
> -1.2 s after 37.8 s). See REVIEW.md "v2".

GOAL:    a pricing analyst finishes the film knowing Insurance Pricing turns six applicant details into an
         annual estimate, shows how much each input moved it, explains it in plain English, and makes a
         what-if a two-click job.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps, H.264 yuv420p + AAC.
TIME:    63.2 s x 30 = 1896 frames. Music bed 100 BPM (Lyria, generated, trimmed 0.08 s so beats fall on
         multiples of 0.6 s): 1 beat = 18 frames, 1 bar = 72 frames (2.4 s). Every accent-bar wipe starts on
         a beat (5.4, 21.0, 23.4, 37.2, 39.6, 55.2 s); the bed fades 60.0-62.4 s (one bar) to digital silence.

LOOK:    the product's own system, nothing invented.
         ground #fafafa (app bg-zinc-50); surfaces #ffffff; borders #f4f4f5/#e4e4e7; ink #18181b,
         secondary #71717b; ONE accent family from the app: emerald-400 #00d294 (the header bar, the wipe bar,
         callout rule), emerald-600 #009767 (one word per headline), emerald-700 #007956 (URL).
         Display: Geist 600, 104-124 px, tracking -0.04em. Numbers: Geist Mono 600 (as the app's price).
         Body: Geist 400/500. Two families only: Geist and Geist Mono (the app's next/font pair).
         Accent underline (poster "why." and every card): ONE rule, src/accent.css: 10 px #00d294 bar whose top is
         6 px below the font's deepest descender (computed from Geist metrics), never a px offset from the line box.
         Callouts: Geist 600 30 px on white, 1 px #e4e4e7 border, 4 px #00d294 left rule, 12 px radius,
         shadow 0 12 32 rgba(24,24,27,.12), 2 px #71717b leader drawn from an 8 px emerald dot on the element.
         The UI is the real page rebuilt as DOM from the captured production build (its own Tailwind CSS,
         captured markup, real /predict responses) at 1905 x 1080 CSS px (1920 minus the page's reserved
         scrollbar gutter, so every element sits where the live page puts it: measured 0 px off), framed by a
         camera between 1.0x (whole page) and 2.6x.
OBJECTS: cursor = macOS-style black arrow, white 1.6 px edge, 26 px tall in app space (52-68 px on screen);
         number inputs = the app's 38 px fields; typing selects the old value (#b3d7ff) then types one
         character per 0.11-0.12 s with a 1 px caret; dropdown = white card 4 px under the select, 32 px rows,
         hovered row #f4f4f5, check mark on the current value (the native OS popup drawn in the app's zinc
         style); Estimate button = the app's states: hover #27272a, press 0.98, pending "Estimating" + spinner
         at opacity 0.4, done = disabled until an input changes.
MOTION:  camera power2.inOut 1.0-1.1 s, one move at a time, never during a click; 2D only (force3D false).
         cursor power3.inOut 0.5-0.62 s; press = cursor 0.86 for 0.07 s.
         menu open 0.2 s power2.out (opacity, scaleY 0.96->1, y -4->0); close 0.14 s power2.in.
         result cards: the app's animate-fade-in-up (0.4 s ease-out, y 8->0, 100 ms apart).
         price counts per frame (1.1 s power2.out, then 1.4 s power2.inOut on the what-if);
         SHAP bars 0.7 s power2.out from the centre line; a sign flip shrinks the old bar 0.45 s power2.in
         and grows the new one 0.55 s power2.out; values count through zero and change colour there.
         interpretation bullets swap one by one (blur 4 px, 60 ms apart).
         chapter card: the app's emerald header bar, 14 px wide, sweeps left to right in 0.55 s power3.inOut
         and draws a #fafafa sheet behind it; words land 0.16 s each, 80 ms apart (blur 8->0, no translate);
         the bar sweeps again to uncover the product. This is the only transition between chapters; the
         poster changes into the first card by a blur swap on the same sheet.
SHOTS (global seconds):
  0.0-3.3   HOOK poster: mark + "Insurance Pricing", "Know the price. Know why.", the real estimate card;
            Feature Impact bars grow from the centre line, values count, "why." gets its underline.
  3.3-5.4   poster blurs out on the same sheet; "Start with one applicant" lands.
  5.4-10.2  wipe uncovers the form at 2.6x: cursor enters from below; Age 35->48, BMI 27.5->30.4,
            Children 1->2, each click / select / type.
  10.2-14.0 pan down: Region opens, cursor tracks Northeast -> Northwest, select, close; Estimate hover,
            press, "Estimating".
  14.0-21.0 pull back to 1.25x: the app's pending card ("Running estimate..."), then the three result cards
            fade up, price counts to $33,216.29, bars grow; push to the price (2.2x),
            callout "Estimated by an AutoGluon model".
  21.0-24.0 card "Why this price?"
  24.0-31.0 Feature Impact at 2.55x: hover the info icon, the real tooltip; callouts "Smoking adds $8,602",
            "Green raises it, red lowers it".
  31.0-37.2 Interpretation at 2.57x: callout on the OPENAI badge "Plain-English reasons from OpenAI";
            the $8,602 sentence is marked; callout "Matches the chart: +8602".
  37.2-40.2 card "What if she quits smoking?"
  40.2-43.8 form at 2.6x: Smoker Yes -> No (open, track, select, close); Estimate re-enables; press.
  43.8-55.2 pull back: price counts $33,216.29 -> $10,517.92, smoker bar swings +8602 -> -9056, BMI flips to
            -3689, age grows to +1922, every bullet rewrites; push to the price, "Down $22,698 a year";
            to the bars, "Was +$8,602, now -$9,056"; pull back to the whole page.
  55.2-63.2 end card: wipe, the mark is drawn upward, "Insurance Pricing" letter by letter,
            "Know the price. Know why.", insurance-pricing.symfa.ai; held 5.6 s; music fades 60.0-62.4 s,
            0.8 s of silence closes the film.
SOUND:   music bed (lo-fi rhodes/bass/brushes, Lyria RealTime, candidate C of 3), low-passed 15 kHz, -3 dB
         at 110 Hz, loudness-normalised to -17 LUFS, true peak <= -2 dBTP; soft click on every real click
         (0.55), faint key ticks while typing (0.3), two alternating whoosh takes on the six wipes (0.16).
BANNED:  persistent caption or subtitle strip; any hard content swap without a tween; error, empty-state,
         "N/A", "fallback" or key text; the idle "Enter your details" card in frame; localhost or browser
         chrome; the Next.js dev badge; spinners longer than 1.3 s; dark void ground; glow, particles,
         gradients beyond the app's own 1 px emerald card rule; glass cards; pill chips; titles that drift after
         landing; three cards in a row; the logo docked in a corner; click rings; serif fallback fonts.
QA:      frames every 2 s and around every seam (+-0.2 s) and every zoom peak at full resolution; text >= 28 px
         for headlines and callouts; consecutive-frame diff on static labels (no raster flicker); the
         interpretation text and every number match assets/data/api-*.json; audio: music from 0, no clipping,
         silence in the last 0.5 s.
