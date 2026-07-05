# Tree QR Code Project

Stick a QR code + name plate on a tree. Anyone with a smartphone camera scans
it and instantly sees the tree's name, species, facts, and uses — no app
install required.

> **This repo is already hosted, live, and set up to auto-publish:**
> - Code: https://github.com/RohitLambade/tree-qr-code
> - Site: https://rohitlambade.github.io/tree-qr-code/

## How to use this, step by step

### 1. Start the app

Open a terminal in this project folder and run:

```bash
python3 app.py
```

This opens **Tree QR Manager** in your browser automatically, at
`http://127.0.0.1:8877`. Leave the terminal window open while you work —
closing it (or pressing Ctrl+C in it) shuts the tool down. (First time only:
run `pip3 install -r requirements.txt` before this step.)

### 2. Add a tree

In the **Add a Tree** form on the left, fill in:
- **Common name** and **Scientific name** — the only two required fields.
- Everything else is optional: tagline, family, height, planted year,
  conservation status, local names, description, fun facts, uses, a photo
  URL, and its location on campus.

Click **Save Tree**. It immediately appears as a card under **Your Trees** on
the right. Repeat for each tree you want to add.

### 3. Publish it (make it live)

Click **⟳ Generate + Publish to Website**. One click does all of this:
1. Rebuilds every tree's web page.
2. Regenerates every QR code and printable label.
3. Commits and pushes the changes to GitHub automatically.

GitHub Pages then rebuilds the live site — usually live within about a
minute. You'll never need to run a `git` command yourself; see
[How auto-publish works](#how-auto-publish-works) below for the one-time
setup this depends on.

### 4. Print the label

Click **Print** on a tree's card (or **🖨 Print All Labels** at the top for
every tree at once). This opens a print-ready page in your browser with the
QR code and the tree's name, sized for a small label, and sends it straight
to your printer.

- Print on **weatherproof/waterproof sticker paper**, or print normally and
  have it **laminated** (a local print/photocopy shop can do either cheaply).
- Prefer a physical PDF instead? Click **📂 Open Labels Folder** — it also
  contains `printable_labels.pdf` with every label laid out on A4 sheets.

### 5. Mount it on the tree

- **Don't nail or glue directly into a living tree.** Attach the label to a
  small wooden/plastic stake near the base, or a soft strap/zip-tie looped
  loosely around the trunk so it doesn't cut into the bark as the tree grows.
- Mount it at roughly chest height, facing the main path people walk along,
  so it's easy to spot and scan.

### 6. Scan it like a visitor would

Open your phone's regular camera app (no extra app needed) and point it at
the printed QR code. It should show a link to tap — tapping it opens the
tree's page in your phone's browser.

**Test with mobile data, not WiFi**, before mounting labels for real — that's
the actual condition a visitor will be in, and confirms the page truly loads
over the open internet rather than only on your home/school network.

### Editing or removing a tree later

Click **Edit** on any tree card to change its details, or **Delete** to
remove it — then click **⟳ Generate + Publish to Website** again. Both
changes go live the same way: an edited tree's page updates in place; a
deleted tree's page, QR code, and label are all removed automatically so it
stops being reachable.

---

## How auto-publish works

Publishing depends on git already being authenticated on the computer running
`app.py` — done once already on this machine via `gh auth login`. As long as
that's true, the **Generate + Publish** button always keeps GitHub in sync;
you never touch git directly.

**If you move this project to a different computer** (e.g. deploying it onto
the school's own machine instead of running it here), repeat that one-time
step there:
```bash
gh auth login
```
After that, the button handles everything from then on. If git isn't
authenticated on a given machine, the button still generates everything
locally and tells you publishing was skipped, rather than failing silently.

## Setting up hosting from scratch (reference only — already done here)

This step is already complete for this repo. It's here in case you ever fork
this project into a brand new repo and need to redo it:

**Option A — GitHub Pages (recommended, free forever)**
1. Create a GitHub repository and push this project to it.
2. Repo **Settings → Pages** → Source = "Deploy from a branch", Branch =
   `main`, Folder = `/docs`. Save.
3. GitHub gives you a URL like `https://your-username.github.io/your-repo/`.

**Option B — Netlify Drop (fastest, no git needed)**
1. Go to Netlify's drag-and-drop deploy page and log in.
2. Drag the `docs` folder onto the page.
3. Netlify gives you a live URL instantly.

Then paste that URL into **Website address** at the top of the Tree QR
Manager page, click **Save Settings**, and click **Generate + Publish to
Website** so the QR codes point at the real, live pages.

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
