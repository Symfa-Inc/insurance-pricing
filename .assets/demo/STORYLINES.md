# Insurance Pricing demo film: storylines

Subject: Insurance Pricing, a single-page app (Next.js frontend, FastAPI backend) that estimates annual
health-insurance charges from six applicant details with an AutoGluon model, shows each input's SHAP
contribution as a "Feature Impact" bar chart, and has OpenAI write a plain-English interpretation.
Viewer: a pricing analyst, underwriter or product lead who has to quote a premium and defend it.

One real piece of data travels through every option: the applicant **48, female, BMI 30.4, 2 children,
smoker, northwest**, captured from the running app (backend on :8017, production frontend on :3017). Her real
estimate is **$33,216.29** (smoker +$8,602, BMI +$2,473, age +$740, sex +$246, region -$98, children +$0).
With smoker set to No the real estimate is **$10,517.92** (smoker -$9,056). Both interpretations are real
OpenAI output for exactly these inputs (6 runs each; see `project/REVIEW.md` for how the shown runs were picked).

---

## A. "One applicant, one what-if" (chosen)

- **Device / form:** a moment in someone's day (one analyst, one applicant, one question) told as one continuous
  take inside the product. The camera never leaves the app except for short chapter cards drawn over it by
  the app's own emerald accent bar.
- **What the viewer sees and feels:** the form gets filled in front of them (typed ages, a region dropdown),
  Estimate runs, a number lands, then the reasons: the Feature Impact bars and the written interpretation,
  which agrees with the chart. Then the what-if: smoker Yes to No, and the price counts down by $22,698 while
  the smoker bar swings from green to red. Calm, factual, the tool doing real work.
- **First two seconds:** a designed poster on the app's #fafafa ground: the shield mark and "Insurance Pricing",
  "Know the price. Know why." with "why." in emerald, and the real estimate card for this applicant, its
  Feature Impact bars growing out of the centre line.
- **Beats:** hook (poster) → "Start with one applicant" → type age, BMI, children → pick region → Estimate →
  price lands (AutoGluon) → "Why this price?" → Feature Impact tooltip, "Smoking adds $8,602", colour key →
  interpretation (OpenAI) matches the chart → "What if she quits smoking?" → Smoker Yes to No → Estimate →
  price counts down, bars swing, text rewrites → "Down $22,698 a year" → whole page → end card.
- **Look:** the app's own system: #fafafa ground, zinc ink, emerald accent (#00d294 bar, #009767 text), Geist +
  Geist Mono only; real UI at 1.25x to 2.6x, never a small window floating on a void.
- **Sound:** a light lo-fi bed at 100 BPM (Lyria), soft clicks on real clicks, faint key ticks while typing,
  two alternating whooshes on the accent-bar wipes; the bed fades to silence under the end card.

**Why this one:** a stranger follows it without narration: one person, one question that everybody in
insurance knows the answer to, and every number on screen is the product's own output. It shows all three
things the app does (estimate, explain, compare) in the order a user meets them.

## B. "The number first"

- **Device / form:** the result first, then a pull-back that explains it.
- **What the viewer sees:** "$33,216.29" fills the frame in Geist Mono. Six coloured slivers slide out from
  behind it and become the Feature Impact bars; the camera pulls back through the price card to the
  interpretation, then to the form that produced it.
- **First two seconds:** the number alone, an emerald underline drawing beneath it.
- **Beats:** number → bars → reasons → form → whole app → what-if counts the number down → end card.
- **Look:** same palette, giant tabular numerals, one continuous zoom-out.
- **Sound:** a single pulse that opens up as the camera pulls back.
- **Not chosen because:** it is striking but explains the tool backwards; the interactions (typing, the
  dropdowns, Estimate) would happen off camera or out of order.

## C. "Six inputs"

- **Device / form:** type carries the argument; each of the six inputs gets a kinetic word ("48", "30.4",
  "smoker") that punches into its field, then a hard cut to the bar it moved.
- **What the viewer sees:** a rhythm of input → bar → input → bar, ending on the price.
- **First two seconds:** "48" in 300 px Geist on white, flying into the Age field.
- **Beats:** six input/bar pairs → price → what-if → end card.
- **Look:** white and emerald type planes alternating with the app.
- **Sound:** cut on every beat, a riser into the price.
- **Not chosen because:** it turns into a kinetic-type slideshow, and six pairs in 60 s leave no time for
  believable dropdown and button interactions or for the written interpretation.

The chosen film borrows one thing from B: the hook shows the finished estimate card before the story starts.
