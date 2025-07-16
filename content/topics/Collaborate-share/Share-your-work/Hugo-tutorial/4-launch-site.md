---
title: "Using Hugo: Create and Deploy a Static Site"
description: "Learn how to launch your site with Hugo after installation"
draft: false
weight: 4
date: 2025-07-07
author: "Harold Miesen"
---

## Using Hugo: Create and Deploy a Static Site

### Step 1: Create a New Project
Start a new Hugo site:

```powershell (Windows) or bash (Linux)
hugo new site my-hugo-site
cd my-hugo-site
```
> __**TIP**__: Choose a meaningful name for your project folder. You can manage multiple Hugo sites independently.


### Step 2: Add a Theme (Ananke)
Add the [Ananke](https://github.com/theNewDynamic/gohugo-theme-ananke) theme using Git submodules:

```powershell (Windows) or bash (Linux)
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke

```
> __**Why Ananke**__? It's a modern, responsive, and accessible theme - great for learning and production alike.

By now, you should have the following directory structure:

```
my-hugo-site/
├── hugo.toml     # Site configuration
├── content/        # Pages
├── themes/         # Downloaded theme
├── static/         # Custom assets (images, CSS, JS)
├── layouts/        # Optional layout overrides
└── public/         # Generated output (DO NOT EDIT)
```

> The `public/` folder is regenerated with every `hugo` build. Never edit it manually.

### Step 3: Configure `hugo.toml`
Edit hugo.toml in your favorite editor and set basic site configuration by adding the following lines:

```toml
baseURL = "http://localhost/"
languageCode = "en-us"
title = "My Hugo Site"
theme = "ananke"
```

__**Additional settings**__ you may want to add:
```toml
paginate = 10
enableRobotsTXT = true
```

### Bonus: Set Up a Default Archetype (Optional)
If you’d like Hugo to automatically add front matter when creating new content, you can define a default archetype.

Create a file at:

```
archetypes/default.md
```

And at the following content:

```markdown
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
---
```

- When you run a command like hugo new about.md, Hugo will use this template.
- The title will be auto-generated from the filename (e.g., about becomes About).
- The date is set to the current timestamp.
- The page will be created as a draft, which you can later publish by setting draft: false.

### Step 4: Run Local Server
Start the Hugo development server in __**the root**__ of your project:
```powershell (Windows) or bash (Linux)
hugo server -D
```

> Visit [http://localhost:1313](http://localhost:1313) in your browser.

> Live reload is enabled - changes are reflected immediately.

### Bonus: Deploy to GitHub Pages (Recommended Setup)

#### 1. Commit your project source to main
Make sure your Hugo project (including content, theme, and config files) is version-controlled:

```powershell (Windows) or bash (Linux)
git init
git add .
git commit -m "Initial commit with Hugo source files"
git remote add origin https://github.com/<your-username>/my-hugo-site.git
git branch -M main
git push -u origin main
```

> This keeps your full source code in the `main` branch.

#### 2. Build the static site
Use Hugo to generate the final website:

```powershell (Windows) or bash (Linux)
hugo --minify
```

> The output will be placed in the `public/` directory.

#### 3. Deploy the contents of `public` to `gh-pages`
You'll now push only the contents of the `public/` folder to a __**separate branch**__:

```powershell (Windows) or bash (Linux)
cd public
git init
git checkout -b gh-pages
git remote add origin https://github.com/<your-username>/my-hugo-site.git
touch .nojekyll
git add .
git commit -m "Deploy site to GitHub Pages"
git push -f origin gh-pages
```

> `touch .nojekyll` disables Jekyll prcessing on Github Pages, which can interfere with Hugo's folder structure (e.g. `/assets/`).

#### 4. Configure GitHub Pages
1. Go to your repository on GitHub
2. Open __**Settings**__ -> __**Pages**__
3. Under __**Source**__, choose:
    - Branch: `gh-pages`
    - Folder: `/ (root)`
4. Save

> Your site will be available at: `https://<username>.githubio/<repo>/`

### Bonus: Automate Deployment
Instead of manually pushing `public/`, you can automate this with [GitHub Actions](https://github.com/features/actions).

You're now ready to add content to your static Hugo site and to continue to the [Adding content to your Hugo site](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/5-add-content/), or go back to [Hugo Tutorial: Start Here](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/index/)