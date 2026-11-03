# Apple requirements: discover, freeze, verify

## Authoritative sources

| Question | Official source |
| --- | --- |
| Header/search dimensions and encoding | https://developer.apple.com/help/app-store-connect/reference/app-information/creative-assets-specifications/ |
| Screenshot slots, counts, orientation | https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/ |
| Composition, text, claims, previews | https://developer.apple.com/app-store/asset-best-practices/ |
| Actual Apple device artwork | https://developer.apple.com/design/resources/#product-bezels |
| Product image usage restrictions | https://developer.apple.com/app-store/marketing/guidelines/#section-products |
| Accurate metadata and actual app use | https://developer.apple.com/app-store/review/guidelines/#accurate-metadata |

Read rendered pages and expand collapsed sections. Record URL, access date, quoted requirement, selected slot/device, exceptions, and uncertainty in a local evidence note. Separate a spec table, an asset template, and actual App Store Connect placement availability.

External-marketing instructions to use download badges are not instructions to add them inside App Store screenshots/creative assets. Apply each rule to its actual placement.

## Dated seed, NOT permanent truth

The following selected values were observed in rendered Apple documentation on **2026-11-03**. Recheck every production run. The planner seeds these choices but leaves verification empty. They are not exhaustive catalogs or promises that all models have the same framebuffer.

| Placement / display | Selected dimensions |
| --- | --- |
| Search, placement-specific | 3840 × 2560 (3:2); observed minimum 1920 × 1280 |
| Product page header, placement-specific | 3840 × 1646 (approximately 21:9) |
| Alternative universal creative | 5244 × 2950; PNG only for this format |
| iPhone Pro, medium Dynamic Island slot | 1206 × 2622 portrait or 2622 × 1206 landscape |
| iPhone Duo outer | 1398 × 2034 or 2034 × 1398 |
| iPhone Duo inner | 2007 × 2853 or 2853 × 2007 |
| iPad 13-inch slot | 2064 × 2752 or inverse; also 2048 × 2732 or inverse |
| Mac | 1280 × 800, 1440 × 900, 2560 × 1600, or 2880 × 1800; 16:10 |
| Apple TV | 1920 × 1080 or 3840 × 2160 |
| Apple Vision Pro | 3840 × 2160 |
| Apple Watch | 422 × 514, 410 × 502, 416 × 496, 396 × 484, 368 × 448, or 312 × 390, matched to the selected model |

Observed rules: 1–10 screenshots per device size; PNG/JPEG; no alpha or transparency. Watch screenshot size must remain consistent across the app's localizations. The screenshot page requires a medium Dynamic Island iPhone screenshot and a 13-inch iPad screenshot when iPad is supported. Its Duo section says screenshots become required starting April 2027 for apps using iOS 27.1 SDK or later. **This skill's default Duo coverage is a user preference now, independent of that future submission deadline.**

Do not require all listed sizes at once. Match the chosen official slot, capture, orientation, and artwork. A frame's outer size, its aperture, a native framebuffer, and an upload canvas are four different dimensions.

Creative-placement guidance describes surfaces on iOS 27 / iPadOS 27 and later. Confirm eligibility for the intended app record; do not assume a Mac listing has every mobile store placement. A requested design can be delivered as marketing artwork while upload availability remains unverified.

## Official device artwork

On the verification date, Product Bezels listed iPhone Duo, iPhone 18/17/16, iPad families, Watch families, Apple TV, iMac, Studio Displays, and MacBook families. **No Apple Vision Pro bezel was visible in that section.** This is a dated observation, not a permanent absence claim. Search current official platform resources before blocking a visionOS framed variant.

Follow download links from the current Apple page; never manufacture URLs from filename conventions. Record referring page, direct package URL, final download host, retrieval date, original filename, device/color/orientation/display, package/artwork SHA-256, and license. An Apple-linked CDN is acceptable when provenance is established. Never bypass sign-in or license prompts.

Observed product-image rules: use supplied images as-is; no cropping, tilting, flipping, recoloring, extra reflections/shadows/highlights, obstructed hardware, or graphics entering/exiting screens. Place copy beside, not on top of, hardware. Preserve relative device scale. Use the latest officially supplied generation supported by the app. Recheck restrictions rather than treating fashionable mockups as permission.

## Outcomes

- Verified specification: current official requirement plus dated local evidence.
- Locally validated output: files pass against that snapshot; Apple preview/approval may remain outstanding.
- Blocked: missing official resource, runtime, verifiable spec, or irreconcilable requirements. Complete independent work and list the concrete prerequisite.
- Not applicable: supported by project/listing evidence, not convenience.

Missing runtime never authorizes invented UI; missing bezel never authorizes generated/third-party hardware.
