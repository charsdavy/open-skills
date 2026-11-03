# Real screenshots and official device composition

## Coverage and discovery

Inspect app-target product types, schemes, `SUPPORTED_PLATFORMS`, `SDKROOT`, `TARGETED_DEVICE_FAMILY`, deployment targets, supported destinations, Catalyst flags, and release configuration. Read effective settings for relevant schemes if needed. `Package.swift` is supporting evidence, not proof that every platform ships.

| Supported surface | Required default coverage |
| --- | --- |
| iPhone | Pro, Duo closed outer, Duo open inner |
| iPadOS | Matching supported iPad, including required 13-inch store slot |
| macOS / shipped Catalyst app | Real Mac UI with appropriate official Mac artwork |
| watchOS | Native Watch upload plus officially framed Watch presentation |
| tvOS | Real TV app capture plus official Apple TV presentation |
| visionOS | Actual spatial-app capture plus official permitted presentation if available |

Each supported surface needs an upload and a framed presentation. A framed upload can satisfy both; native-only uploads need a separate marketing version. Keep unresolved frame requirements blocked. Screenshot obligations do not apply to a creative-only request.

## Screenshot layout: independent of search/header

The compact central cluster and generous four-sided clear space apply **only to Search Results and Header, not to screenshots or their framed marketing versions**. Do not import their percentage rectangles, crop/overlay reserves, or `safe_rect`/`content_bounds` requirements into screenshot layouts.

Prioritize large, legible actual UI and a clear workflow. Device and copy placement can vary by platform, orientation, and narrative; a device may occupy most of the canvas. Centering and perimeter whitespace are optional design choices, not acceptance gates. Continue to obey current Apple dimensions and artwork usage rules: this freedom does not permit clipping/obstructing official hardware, stretching UI, or misfitting the screen aperture.

## Capture truth

1. Run the actual app in an isolated test container/account where possible. Use a real device or simulator matching device generation, resolution, orientation, OS, and display. Do not overwrite personal libraries or alter real cloud settings to stage images.
2. Seed plausible fictional content through supported fixtures, storage, or interactions; render production views. Recreated HTML is not a screenshot. Disclose fixture limitations: cached content does not prove live synchronization.
3. Set English UI/locale, consistent theme, clean status bars where supported, representative populated screens. Exclude secrets, real accounts, developer consoles, broken placeholders, permission dialogs, and accidental keyboard occlusion. Do not change behavior to imply unavailable functionality.
4. Capture the active framebuffer or supported screenshot attachment. Record path/hash, target/version/build, device, OS, orientation, display, scenario, and method. Keep original pixels before alpha flattening or composition.
5. Visually verify desired UI, blank/black frames, loading state, truncation, selection, and exact native dimensions. A successful automation command is not evidence of the correct screen.

Examples, subject to the available runtime and permissions:

```sh
xcrun simctl list devices available
xcrun simctl io <device-id> screenshot <output.png>
xcrun xcresulttool export attachments --path <result.xcresult> --output-path <folder>
```

Unavailable launch/capture means a blocked capture, not permission to synthesize plausible UI. Complete independent work and report the prerequisite.

## iPhone Duo: two captures

- Separate `duo-outer` and `duo-inner` sources, official bezels, native dimensions, and upload entries.
- Capture the active closed outer and open inner displays. Never stretch Pro/outer UI onto the inner display, merely rotate portrait UI, or paint a second display.
- Inner UI uses its real responsive layout and a supported orientation, paired with matching open-device artwork.
- Verify the framebuffer: a capture path may return an inactive black screen or rounded dimensions. Recover an exact capture rather than resizing it and claiming native fidelity.
- Missing runtime/artwork remains a named blocked item; never silently deliver only one state.

## Frame provenance and composition

Get actual files from current Apple Design Resources. Download data resources; do not run installers or bypass licenses. Cache standalone artwork locally and exclude it from redistributable skill packages.

Record referring page, download URL/date, original package/artwork filename and SHA-256, exact model/color/orientation/display, source dimensions, and aperture/mask. Extract the official layer when available; do not redraw a generic phone.

```text
campaign background
  + actual capture uniformly fitted to the measured screen aperture
  + intact official hardware / supplied mask
  + editorial copy outside hardware
```

Measure the current asset, not another generation's coordinates. Validate aspect ratios/transforms; scale hardware and screen together. Use exact mask/corner/cutout geometry. No stretching, tilting, cropping, recoloring, artificial hardware shadows, obstructed hardware, or UI emerging from screens. Preserve complete devices and relative scale.

Never send hardware/UI through generative repainting. Use a compositor that retains them exactly, subject to host rules. Generated backgrounds can remain separate. Re-render from sources rather than repeatedly resampling finished images.

## Special surfaces

- Watch: native canvases often become illegible inside frames. Default native uploads plus larger framed marketing images. This is a design strategy, **not a blanket Apple prohibition on Watch frames**. Larger marketing canvases are not native upload slots. Keep Watch upload sizes consistent across localizations.
- Mac: real app/desktop context, official Mac artwork; do not put Mac UI in an iPhone. Store canvas and framebuffer may differ; never distort UI to match.
- Apple TV: use its official presentation resource and permitted display composition. Do not invent an Apple television or put the app screen on the TV box. If the resource cannot support the composition, deliver native uploads and block the framed dependency.
- Apple Vision Pro: use actual spatial captures. Do not insert flat UI into lenses or invent a physical screen aperture. Find a current official licensed presentation/template; otherwise deliver compliant native captures and explicitly block the requested framed version. No fabricated hardware or third-party substitution.

Official artwork provenance and upload compliance are distinct checks. Attractive artwork can still use a wrong slot or device.
