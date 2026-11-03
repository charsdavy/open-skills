# Creative direction and the approved quality reference

## View the images

- [Momonga search reference](../assets/momonga-search-reference.png)
- [Momonga header reference](../assets/momonga-header-reference.png)

These are the original generated images from the user-approved campaign, not upload templates. Native sizes: 1536 × 1024 and 1915 × 821. The shipped examples were resampled to 3840 × 2560 and 3840 × 1646, with that limitation disclosed. Prefer higher-detail originals when available; do not copy the example's upsampling unnecessarily.

## Why the campaign worked

1. **Product truth first.** Actual clipboard, knowledge, and download features determined the claims. No generic “AI everything,” fictitious subscription, or unsupported mobile behavior.
2. **Distinct conversion jobs.** Search answered a concrete pain: “Find that copy. Keep your flow.” Header explained value: “More than a clipboard.” Breadth became one still life, not a wall of feature bullets.
3. **Brand translation.** The existing squirrel/paper motif became tactile illustration. Actual forest/ivory/sage colors gained a small apricot accent. The pair shared material and type but used deliberate dark/light contrast.
4. **Short, exact, large copy.** One headline, one support phrase, few labels; the illustration reinforced the benefit instead of competing with it.
5. **Contained focal mass for search/header.** Content stayed grouped centrally, with sacrificial background for cropping and overlays. Negative space was intentional for these two placements, not a rule for device screenshots.
6. **Source versus export.** File dimensions/encoding and originals were checked after generation. A requested size in a prompt was not considered proof.

Do NOT universalize the mascot, clay material, green, Mac label, slogans, or “three tools.” A photo app may need photographic truth; a game needs real gameplay. Transfer the reasoning.

## Visual contract

Before production, specify audience/pain, one verified outcome, visual proof, brand invariants, material/lighting, focal point, type hierarchy, exact copy/line breaks, and exclusions. Add central foreground bounds and crop/overlay reserve only for Search Results and Header. For screenshots, specify readable UI scale, device/copy placement, and screen fit instead. Prefer a concrete benefit over API/feature density.

Do not claim “free,” “lifetime,” “offline AI,” “16× faster,” perfect privacy, or “works everywhere” unless current evidence supports the precise statement and the placement permits it. Optional features/external API costs must not become misleading included-value claims.

## Search/header ONLY: composition defaults, not official safe zones

**Do not use this section's central grouping, four-sided margins, or percentage rectangles for device screenshots, including framed marketing versions.** Screenshots follow the independent layout rules in [screenshots-and-bezels.md](screenshots-and-bezels.md).

For **both Search Results and Header**, prioritize a **compact central cluster plus generous negative space on all four sides**. Consider the combined bounds of the headline, brand, support, and main illustration, not just the headline's alignment. Keep components near enough to read as one group, with internal breathing room. Do not scatter a logo in one corner, a slogan in another, and feature cards along the edges.

Start search essential content around x=18–82%, y=16–75%; start an ultrawide header around x=20–80%, y=20–70%. Reserve additional bottom room if actual store templates overlay app information. Adjust to official templates and observed previews, never a magic percentage.

These starting rectangles occupy only about 64% × 59% of the search canvas and 60% × 50% of the header canvas. The remaining perimeter is intentional crop/overlay reserve. Keep it visually quiet: a continuous brand background or subtle gradient is fine; small peripheral labels, stickers, feature chips, and decorative high-contrast objects are not. Do not compensate for sparse content by spreading the group toward the borders.

Identify sacrificial decoration separately from essential words, identifiable artwork, and complete hardware. Do not plan to crop a bezel. If shrinking makes UI unreadable, shorten copy or use fewer devices rather than microscopic screens.

## Search/header ONLY: model-agnostic prompt recipe

Use this recipe for Search Results or Header artwork, never as a device-screenshot layout template.

```text
Create ONE [Search Results or Header] image for [app], in English.
Canvas: [dimensions/aspect]; verify actual pixels after export.
Purpose: [one visitor decision and one verified benefit].
References: [explicit attachments and the role of each].
Preserve: [identity, colors, feature truth].
Visual language: [material, lighting, tone, type hierarchy].
Composition: ONE compact, centered cluster containing ALL meaningful text and artwork.
Keep the whole cluster within [foreground rectangle]. Leave generous quiet background
on ALL FOUR sides: [left/right/top/bottom margins], with extra bottom-overlay reserve.
Do not distribute content across the full canvas, place important elements near edges,
or fill the perimeter with labels, badges, or decorative objects.
Exact text: [quoted headline, line breaks, support, limited labels].
Artwork: [one specific scene or product metaphor].
Forbidden: [extra text, prices, awards, invented features, fake hardware, guides].
Output: one finished image, no alternatives collage or outer poster border.
```

For headers explicitly request ultrawide composition; do not crop a search poster into a banner. For the second image state shared invariants and intentional differences. For edits, state what changes and what stays fixed.

Models do not guarantee exact copy, dimensions, logo geometry, or safety margins. Inspect. Fix one concrete defect per iteration. If exact text/identity repeatedly fails, use a permitted precise layout workflow, not false approval of misspellings. Screenshots and Apple bezels remain unpainted source assets.

## Screenshot narrative

Screenshots have no compact-centering or generous four-sided-margin requirement. Let real UI occupy a large, readable area; adapt device/copy placement to each platform and orientation rather than inheriting search/header safe rectangles. Preserve official hardware and screen geometry.

Default sequence: outcome → core interaction → distinctive capability → cross-device value → control/trust. Include only supported steps; adapt count/order to each platform. A Watch interaction is not a tiny Mac dashboard.

Explore 2–3 headline alternatives in text, then choose one visual direction before generation. Do not automatically spend on many expensive variants. Later A/B tests may compare one variable; no uplift is claimed without data.
