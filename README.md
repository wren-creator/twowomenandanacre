# Two Women and an Acre

Placeholder site for the farm: organic growing, agritourism visits, foraging
classes and education, and a small-batch shop (tea, tinctures, jellies, and
jams) launching soon. Hosted on GitHub Pages.

**Live site:** https://twowomenandanacre.com/

## Contents

- `index.html` — the one-page site
- `styles.css` — all styling, kraft-paper/jam-jar palette, light and dark
  mode via CSS custom properties and `prefers-color-scheme`
- `assets/` — farm photos:
  - `hero-garden.jpg` — wide shot of the raised beds, used as the hero
    background
  - `garden-corner.jpg` — strawberries, herbs, and potted saplings, used
    beside the "Our Acre" text
  - `harvest-counter.jpg` — fresh harvest with a jar of pickled okra,
    used beside the Shop section
  - `fig-tree.jpg`, `grape-vine.jpg`, `squash-blossom.jpg`,
    `cabbage-head.jpg` — the "what we grow, this season" snapshot strip
    under the "what we do" cards
  - `farm-girl-cinnamon-rolls.jpg`, `farm-girl-sourdough.jpg` — the
    "Friends of the Acre" card for Farm Girl Bakery
  - `bed-closeup.jpg` — a raised bed close-up, not placed on the page
    yet, good candidate for a future addition to the grow strip or the
    Organic Growing card once there are matching photos for Agritourism
    and Foraging too

## More photos later

The three `.packet` cards in "what we do" (Organic Growing, Agritourism,
Foraging & Education) still use line-art icons rather than photos, to
keep that grid visually consistent until there are photos for all three.
Once there are, swap the `<svg class="icon">` blocks in `index.html` for
`<img>` tags. More snapshots can be added to `.grow-strip` any time, it's
just a repeating `<figure>` pattern.

## Friends of the Acre

A `.friends-grid` of `.friend-card`s for local farms and makers, each
with two photos and a link (currently just Farm Girl Bakery). Copy the
existing `.friend-card` block in `index.html` to add another.

## Contact

- Email: admin@twowomenandanacre.com (needs mailbox/forwarding set up,
  same as was done for britleyhoff@britleyhoffconsulting.com)
