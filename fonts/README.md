Subset WOFF builds of the typefaces used on [parthdave.me](https://www.parthdave.me/):

- **Space Grotesk** (display) — SIL Open Font License 1.1, [floriankarsten/space-grotesk](https://github.com/floriankarsten/space-grotesk)
- **Inter** (body) — SIL Open Font License 1.1, [rsms/inter](https://github.com/rsms/inter)
- **JetBrains Mono** (labels) — SIL Open Font License 1.1, [JetBrains/JetBrainsMono](https://github.com/JetBrains/JetBrainsMono)

Each file is subset to printable ASCII plus a few punctuation marks and arrows (`U+0020–007E` and a short extras list) with `pyftsubset --flavor=woff`. `scripts/render_readme_cards.py` embeds them as `data:font/woff` URIs so GitHub `<img>` SVGs can paint the site’s type without requesting Google Fonts.
