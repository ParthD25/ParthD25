# GitHub profile README copy research

The profile README is a GitHub showcase, not a portfolio site and not a resume.
This note records how well-regarded profiles actually sound, then what that
implies for Parth's cards. Nothing here was invented about Parth; project and
hobby facts were checked against [parthdave.me](https://www.parthdave.me/) and
public repos under [ParthD25](https://github.com/ParthD25).

## Avi Vashishta (the given reference)

- Blog: [How I rebuilt my GitHub profile with animated SVG cards](https://www.avivashishta.com/blog/github-profile-readme-animated-svg-cards)
- Live profile: [github.com/AVIVASHISHTA29](https://github.com/AVIVASHISHTA29) (the blog also writes `AviVashishta29`; both resolve to the same account)
- Source: [AVIVASHISHTA29/AVIVASHISHTA29](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29)

Hero phrasing in `scripts/render_readme_cards.py` / the hero `alt`:

- Eyebrow: `FULLSTACK ENGINEER AT DOCK` — present-tense identity as a builder, not a school or graduation date.
- Intro (first person, one thought): `I build AI products, make Reels about them, and teach people to do the same.`
- No degree, no "open to work", no internship season.

Section headings:

- Heatmap: `Every day, in blue`
- Tiles: `BUILD` / `BRAND` / `LEARN` (verbs, not "Experience")
- Repos: `What I'm coding`
- Footer only: `avivashishta.com / linkedin / instagram / live terminal` — no email card.

The blog's own template prompt for a hero is "my name, one line about me" — not a credentials strip.

## Other profiles (tone, not layout)

| Profile | Intro / heading tone | Why it matters |
| --- | --- | --- |
| [Monica Powell](https://github.com/M0nica) | "I'm a software engineer who is passionate about making contributing to open-source more approachable…" / `Find me around the web` | First person, what she cares about, small link list. |
| [Anurag Hazra](https://github.com/anuraghazra) | "I'm a self-taught passionate FrontEnd developer from India" then `I love writing TypeScript, and building fun experiments` | Identity + what he likes making. |
| [Lee Reilly](https://github.com/leereilly) | "Hey, I’m Lee" then ships, games, experiments. Heading: `Featured personal open source projects` | Showcase of things he made, not a hiring pitch. |
| [Jonathan Gin](https://github.com/JonathanGin52) | "Hey, I'm Jonathan" / "Nice to meet you!" then a community game | Profile as a place people hang out. |
| [Thaiane Braga](https://github.com/thaiane) | "Hi, I'm Thai Braga!" / `A little more about me...` and "I love connecting with different people" | Casual hello, then skills as a personal object, not a CV. |
| [Max Rohowsky](https://github.com/maxontech) | "Hi There! I'm Max…" / `Projects` | Project-first. His Education/Experience tables are the *resume* pattern to avoid. |
| [Yufan You (ouuan)](https://github.com/ouuan) | Name, then tools, research, blog — listed in [awesome-github-profile-readme](https://github.com/abhisheknaiidu/awesome-github-profile-readme) | Student who still leads with work and interests, not "seeking internships". |
| [Tim Burgan](https://github.com/timburgan) | The whole README *is* a community chess game | Extreme version of "this is a GitHub page, not LinkedIn". |

Lists used to pick examples: [abhisheknaiidu/awesome-github-profile-readme](https://github.com/abhisheknaiidu/awesome-github-profile-readme), [maxrohowsky/best-github-profile-readme](https://github.com/maxrohowsky/best-github-profile-readme).

## Patterns to copy

1. **First person, present tense, "I build…"** — Avi, Monica, Anurag. Not "Seeking X internships".
2. **One human line** about what he makes, optionally a second about life outside the repo.
3. **Section titles that sound like a person** — `What I'm coding`, `What I build with`, `Every day on GitHub` — not `Featured work`, `Skills`, `Open to Summer 2027`.
4. **Project blurbs describe the project** (Avi: "Turns a PDF into a guided lesson…"). Keep Parth's existing one-liners; they already do this.
5. **Links live in a small footer.** Avi has no contact chips and no email on the README. Portfolio + LinkedIn in the footer is enough.

## Patterns to reject

- Degree / school / graduation date as the first thing a visitor reads.
- "Open to work" / internship season / job-family laundry list.
- Email as a card (that's a resume header).
- Vanity counts used as credentials (already dropped in the previous redesign).

## Facts used for Parth's new copy (verified)

From [parthdave.me](https://www.parthdave.me/):

- Self-description: AI engineer who builds applied AI / product systems.
- Featured-style products on the site: SimplyWins, RaceShift, Prism Style, BlueCore, Plattr, PawPulse, Forkcast (plus others). Public GitHub currently features SimplyWins, RaceShift, Plattr, PawPulse — those four stay on the cards.
- Hobbies: "Snowboarding and skydiving are still on my bucket list. Until then I cook, bake, take on DIY builds and love cars, both building them and watching them race." So cooking and cars are current; snowboarding is a stated interest, not a claim that he already snowboards.

From public GitHub ([ParthD25](https://github.com/ParthD25)):

- NeurOps exists; `docs/idea.md` names the product **Fireline** (kitchen ticket-firing policy). Mention only as another thing he builds, not as a fifth featured card.
- BlueCore / Forkcast / Prism Style are on the portfolio; they are not all public GitHub repos, so they are not added as README cards.

Not used (hiring-pitch leftovers): CMU M.S., AI & Systems Management, Dec 2027, Summer 2027, internship tracks, email card.
