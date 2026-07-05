# Tree QR Code Project

Stick a QR code + name plate on a tree. Anyone with a smartphone camera scans
it and instantly sees the tree's name, species, facts, and uses — no app
install required.

This project has a **local admin app** — no coding or file-editing needed to
add trees, generate QR codes, or print labels. Anyone at the school can run
it on a laptop.

> **This repo is already hosted, live, and set up to auto-publish:**
> - Code: https://github.com/RohitLambade/tree-qr-code
> - Site: https://rohitlambade.github.io/tree-qr-code/
>
> The QR codes already generated in `output/` point at that live URL, and
> clicking **Generate + Publish to Website** in the app pushes changes to
> GitHub automatically (see below). The "Hosting" section further down is
> just for reference — you don't need to redo it unless you fork this into a
> new repo.

## Adding a tree updates the live site automatically

Clicking **Generate + Publish to Website** does everything in one step:
rebuilds every tree's page, regenerates QR codes/labels, **and** commits +
pushes the changes to GitHub — no `git add` / `commit` / `push` needed, ever.
GitHub Pages then rebuilds the live site automatically (usually live within
about a minute). Deleting a tree works the same way: its page and QR/label
files are removed automatically on the next click, so it stops being
reachable once you publish.

This only works because git is already authenticated on this computer (done
once, via `gh auth login`, when this repo was first set up). **If you move
this project to a different computer** (e.g. the school's own machine), you
need to repeat that one-time step there — clone the repo, run
`gh auth login` once, and from then on the button handles everything. If git
isn't authenticated, the button still generates everything locally and shows
you the reason publishing was skipped.

## Quick start (for non-technical use)

1. Install Python 3 if it isn't already installed (comes preinstalled on Mac;
   on Windows, download it from python.org and check "Add to PATH" during
   install).
2. Open a terminal / command prompt in this project folder and run, once:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Every time you want to use the tool, run:
   ```bash
   python3 app.py
   ```
   This opens **Tree QR Manager** in your web browser automatically
   (`http://127.0.0.1:8877`). Leave the terminal window open while you use it
   — closing it (or pressing Ctrl+C in it) shuts the tool down.
4. In the browser page:
   - Fill in the **Add a Tree** form and click **Save Tree**. Repeat for each
     tree. Click **Edit** or **Delete** on any tree card to change it later.
   - Click **Generate + Publish to Website** whenever you've added or changed
     trees — this updates the pages, QR codes, and labels, and pushes the
     update live automatically (see below).
   - Click **Print All Labels** (or **Print** on a single tree) to open a
     print-ready page and send it straight to your printer.
   - Use **Open Labels Folder** / **Open Website Folder** to browse the
     generated files directly.

Adding trees, generating QR codes, and printing all run entirely on that one
computer without internet. Publishing the update live does need an internet
connection (see the auto-publish note above).

## The one thing that does need the internet: hosting

The QR code on a tree points to a web page. For a visitor's *phone* to open
that page, the page needs to live somewhere reachable from their phone — it
can't stay only on the school computer that generated it. This is a
one-time setup, typically done once by whoever is comfortable with it:

**Option A — GitHub Pages (recommended, free forever)**
1. Create a GitHub repository (e.g. `tree-qr-code`) and push this project to it.
2. Repo **Settings → Pages** → Source = "Deploy from a branch", Branch =
   `main`, Folder = `/docs`. Save.
3. GitHub gives you a URL like `https://your-username.github.io/tree-qr-code/`.

**Option B — Netlify Drop (fastest, no git needed)**
1. Go to Netlify's drag-and-drop deploy page and log in.
2. Drag the `docs` folder onto the page.
3. Netlify gives you a live URL instantly.

Once you have that URL, paste it into **Website address** at the top of the
Tree QR Manager page and click **Save Settings**, then **Generate + Publish
to Website** again so the QR codes point to the real, live pages. Whenever
you add or edit a tree afterward, just click that same button — **the QR
codes themselves never need to change or be reprinted**, since they always
point to the same URLs, and their content updates automatically.

## Printing and mounting on the tree

- Print on **weatherproof / waterproof sticker paper**, or print normally and
  **laminate** it (a local print/photocopy shop can do both cheaply).
- **Don't nail or glue directly into a living tree.** Mount the label on a
  small wooden/plastic stake near the base, or attach it with a soft strap /
  zip-tie loosely around the trunk so it doesn't cut into the bark as the
  tree grows.
- Place it at a height and angle that's easy for a person to scan (roughly
  chest height, facing the main pathway).
- Before mass-printing, scan one label with your own phone over mobile data
  (not WiFi) to confirm it opens the right page — that's the exact scenario
  a real visitor will have.

## Tree fields reference

| Field | Required | Notes |
|---|---|---|
| Common name | yes | Displayed as the big heading. |
| Scientific name | yes | Shown in italics. |
| Tagline | no | One sentence under the title — what makes this tree special. |
| Family, Height, Planted year, Conservation status | no | Shown in the Quick Facts grid. |
| Local names | no | e.g. "Hindi: Nariyal" — add as many as you like. |
| Description | no | The main paragraph. |
| Fun facts | no | Bulleted list. |
| Uses & benefits | no | Bulleted list. |
| Photo URL | no | Link to a photo. Leave blank to show a placeholder icon. |
| Location on campus | no | Helps staff find the tree later. |

Three sample trees (King Coconut, Neem, Banyan) are included as a working
demo — edit or delete them from the app once you're adding your school's
real trees.

## For technical users: the CLI scripts

The app is a thin UI over two scripts, which still work standalone if you
prefer the command line or want to script/automate this:

```bash
python3 scripts/build_site.py                                    # data/trees.json -> docs/*.html
python3 scripts/generate_qr.py --base-url https://your-url-here   # data/trees.json -> output/*.png, printable_labels.pdf
```

Project layout:
- `data/trees.json` — the tree database (edited by the app, or by hand).
- `data/config.json` — school name + hosting URL (edited by the app).
- `core/` — shared logic (site building, QR/label generation, data storage,
  and git publishing) used by both `app.py` and the CLI scripts.
- `templates/tree_page_template.html` — the HTML template for a tree's page.
- `docs/` — generated static website (host this folder).
- `output/` — generated QR codes, labels, and print-ready PDF.

## Proposing this to the school

See the separate one-page proposal (shared alongside this project) for a
ready-to-present pitch: the problem, the solution, cost, and a suggested
pilot plan you can walk the principal through.
