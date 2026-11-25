# Horoofy Kids — حروفي

A responsive, Arabic-first learning website for young children. Learn Arabic and English letters, count from 1 to 30 with a different fruit for every number, and practice with five interactive games, including an Arabic animal missing-letter game.

## Features

- 28 Arabic letters and 26 English letters with words, simple explanations, letter forms, search, and a learned filter.
- Speech buttons for letter names and words, using the browser Web Speech API when available.
- Numbers 1–30 with Arabic names and local spoken audio.
- Four playable activities: match an Arabic letter, identify an English initial, count objects, and practice addition or subtraction.
- Learning progress is saved locally in the browser.
- Responsive layouts, RTL Arabic page, keyboard-friendly controls, reduced-motion support, and no account or personal data.

## Structure

`index.html`, `letters-ar.html`, `letters-en.html`, `numbers.html`, and `games.html` are independent static pages. `progress.html` returns visitors to the home page. `css/` holds the shared design system and page styles. `js/data.js` holds the educational data; `js/app.js` handles page rendering, speech, games, navigation, and local progress. All paths are relative for GitHub Pages subpaths.

## Run locally

Use a static HTTP server (speech synthesis support can be limited under `file://`). In VS Code, install Live Server, open this folder, and select **Go Live**. Or run `python -m http.server 8000` in this directory and visit `http://localhost:8000`.

Speech uses `speechSynthesis` and language tags `ar` and `en`; voice availability and pronunciation vary by operating system and browser. The site does not autoplay speech. Google Fonts are optional; system font fallbacks are provided.

## Deploy to GitHub Pages

Commit this folder to a GitHub repository, then in **Settings → Pages**, choose the branch and folder containing `index.html` (repository root if this folder is the repo root). Pages serves the linked static files without a build step. Relative links support deployment under a repository path.

## Customize

Edit CSS custom properties in `css/style.css` to adjust colors, radius, and shadows. Font choices are in each page's Google Fonts link plus the CSS fallback stack. Add or edit word entries in `js/data.js`; keep Arabic, English, and number arrays in the same order and complete. Replace the letter and word art through the `.letter-art` and `.detail-letter` styles or add local illustrations with meaningful alt text when extending the markup.

## Photos and speech

Letter cards use real photos stored locally in `assets/photos/`; source pages, creators, and licenses are listed in `assets/PHOTO-CREDITS.md`. The images are from Wikimedia Commons and each has its own reuse terms.

Letter and word audio clips are local MP3 files in `audio/ar/` and `audio/en/`. They use neural Egyptian Arabic and US English voices generated with the community `edge-tts` client. The recordings are synthesized rather than human voice-actor recordings; the site plays the saved clips without contacting the speech service.

To refresh the free media, install the Python package `edge-tts` and run `python tools/fetch_free_media.py`. This requires an internet connection. The photo-generation script records the source licensing and credit details alongside the downloaded images.
