# Atlas — Phase 1: Website

Local prototype for Christian Hegarty's live CV and portfolio. Atlas and phase names are internal only.

## Preview

From this folder run:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765. Stop the server with Ctrl+C. It listens only on this Mac.

## Files

- `index.html`: the business card and navigation dialog.
- `styles.css`: bone and blue-black palette, paper, embossing, and responsive layouts.
- `script.js`: menu opening, dismissal, and focus restoration.
- `paper-grain.svg`: lightweight local menu texture.
- `card-grain.svg`: slightly stronger fine grain for the business card.
- `background-paper-03-mirrored.svg`: four mirrored centre crops in a repeating 1200 × 900px block; each paper tile stays 600 × 450px at every browser size.
- `background-paper-03.jpg`: Paper and Fabrics-03 from the user’s Joel Grimes Assets collection, used as a faint grayscale background overlay. The original asset remains in the shared Photoshop Assets folder.
- `about.html`, `contact.html`, `projects.html`, `cv.html`: initial destination pages, ready for fuller content.

No packages, external fonts, analytics, or build step are required.

## Agreed design

- Pale neutral background `#F4F4F1`, a deeper bone card `#E9E8E2`, and blue-black ink `#17283A`.
- A subtle central CH blind emboss sits behind the centred name. Contact sits at the bottom left, level with Explore at the bottom right.
- A fine blind-embossed line follows the card perimeter, inset 3–6px according to the card width.
- A central business card scales with browser width and height, with a maximum size. Both faces remain straight at rest and during the flip; hover changes only the shadow.
- Tap, click, or activate the card with a keyboard to open the menu.
- About, Projects, CV, and Back, in that order. Contact is accessed directly from the card.
- Background blur while the menu is open.
- Back, Escape, or an outside click closes the menu and returns focus to the card.
- Separate destination pages; no scrolling homepage sections.
- Reduced-motion preferences are respected.

## Delivery boundary

This is a local prototype. No AWS resources or deployment workflow have been created. Git commits, pushes, and publishing still require the user's approval. Earlier chapter files remain intact.

Next: review the card and menu, develop the page content, then set up GitHub Actions and AWS hosting.

## Dark appearance

The device’s dark-mode preference activates `dark.css`: blue-black textured background, softened bone card, and a gentle edge glow. Light appearance keeps the approved palette. Destination pages and the menu retain bone surfaces with blue-black text in dark mode.

For review, append `?theme=dark` or `?theme=light` to any page URL. `theme.js` carries that preview choice through page links without saving a device preference. Remove the parameter to return to automatic mode.

The About page uses `about.css` for a bone paper layout, a three-line heading, readable mission statement and links to Projects, CV and Contact. The columns stack on smaller viewports; dark appearance remains automatic.

All content pages share an expanding bone card with fine grain, a raised edge and a shadow. The textured surround remains visible; card height follows the content with normal page scrolling. Dark mode adds the warm backlight around these cards.

## Shared page conventions

About, Projects and CV use `.content-page`, `.page-header`, `.eyebrow.page-label` and `.page-footer`. Both divider-to-label offsets use `--rule-label-gap` (1.5rem), with matching 44px label boxes and inherited letter spacing. Use these classes for future reading pages. All reading pages share a 76rem maximum card width and the same responsive padding from `.page`; do not override these per page. Stable scrollbar space keeps their horizontal edges aligned as content length changes.

Contact is the exception: a reverse business card using the same `.business-card` dimensions, 1.75 aspect ratio, viewport breakpoints, grain, raised edge and dark-mode glow as the homepage. Its email and return link remain independent keyboard-accessible links. Reading-page cards grow with content; the contact card retains its proportions.

Selecting Contact at the lower left of the homepage card turns the card over with a 3D flip; the return link reverses it. `card-flip.js` animates two non-interactive card faces before normal navigation, explicitly hiding each face when it turns away to avoid text showing through. Reduced-motion preferences and loading failures fall back to ordinary links.

## CV page

`cv.html` contains the reviewed profile, expertise, career history and education, with CV-only responsive layout rules in `cv.css`. It inherits the shared reading-card sizing. Six local badge images in `assets/badges/` were obtained from the supplied public Credly pages; each links to its corresponding badge record. The AWS architecture qualification is AWS Certified Solutions Architect – Associate.

## DPI case study

`dpi.html` and `dpi.css` present the project purpose, workflow, current local architecture, proposed AWS design, key functions and next steps. `projects.html` links to the case study. Architecture and function descriptions are based on the current Python source and its architecture notes; the web interface exists, while purchase planning remains separate. Screenshots in `assets/dpi/` are captures of the existing Jinja template rendered with illustrative records, not live account data. No source application files or account data were changed.

## Website case study

`website.html`, `website.css` and `website.js` document the site structure, card styling, transitions, themes and selected implementation excerpts. The first portfolio entry links to this case study. Its native dialog loads the real site in an iframe, with appearance and reset controls, Escape handling within the frame, and focus returned to the opening button on close. Build screenshots are stored in `assets/website/`. The footer returns to the main screen.
