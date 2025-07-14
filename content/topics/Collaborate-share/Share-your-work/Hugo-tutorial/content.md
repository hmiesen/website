---
title: "Using Hugo: Create and Deploy a Static Site"
description: "Learn how to build your site with Hugo after installation."
draft: false
weight: 5
date: 2025-07-07
author: "Your Name"
---

## Using Hugo: Create and Deploy a Static Site

### Step 1: Create a New Project
Start a new Hugo site:

```powershell (Windows) or bash (Linux)
hugo new site my-hugo-site
cd my-hugo-site
```
> __**TIP**__: Choose a meaningful name for your project folder. You can manage multiple Hugo sites independently.


## Project Directory Structure

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

---

### Step 2: Add a Theme (Ananke)
Add the [Ananke](https://github.com/theNewDynamic/gohugo-theme-ananke) theme using Git submodules:

```powershell (Windows) or bash (Linux)
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke

```
> __**Why Ananke**__? It's a modern, responsive, and accessible theme - great for learning and production alike.


### Step 3: Configure `hugo.toml`
Edit hugo.toml in hour favorite editor and set basic site configuration by adding the following lines:

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

### Step 4: Add Content
Create a sample page:

```powershell (Windows) or bash (Linux)
hugo new about/hello-world.md
```

Edit the file `hello-world.md` in the `content/about` folder:

```markdown
---
title: "Hello World"
date: 2025-07-07
draft: false
---

Welcome to my first Hugo site!
```
__**Note**__: Hugo marks new content as drafts by default. Set `draft: false` to make it visible.

### Step 5: Run Local Server
Start the Hugo development server in __**the root**__ of your project:
```powershell (Windows) or bash (Linux)
hugo server -D
```

> Visit [http://localhost:1313](http://localhost:1313) in your browser.

> Live reload is enabled - changes are reflected immediately.

---

## Markdown Basics
Hugo uses [Markdown](https://www.markdownguide.org/) to write content.

### Headings

```markdown
# H1
## H2
### H3
```

### Emphasis

```markdown
*italic* __**bold**__ `inline code`
```

### Lists & Links

```markdown
- Unordered item
1. Ordered item
[Visit Hugo](https://gohugo.io)
```

### HTML
Markdown supports raw HTML when you need more flexibility than Markdown syntax allows.

#### Example 1: Custom Layout

```html
<pre>
  &lt;div class="custom-box"&gt;&lt;
    h3&gt;Hello from HTML!&lt;/h3&gt;
      &lt;p&gt;This content uses plain HTML inside a Markdown file.&lt;/p&gt;
  &lt;/div&gt;
</pre>
```

> Hugo will render this HTML as-is, even within `.md` files:

> <div class="custom-box">
>   <h3>Hello from HTML!</h3>
>   <p>This content uses plain HTML inside a Markdown file.</p>
> </div>

---

## Bonus: Deploy to GitHub Pages (Recommended Setup)

### 1. Commit your project source to main
Make sure your Hugo project (including content, theme, and config files) is version-controlled:

```powershell (Windows) or bash (Linux)
git init
git add .
git commit -m "Initial commit with Hugo source files"
git remote add origin https://github.com/<username>/my-hugo-site.git
git branch -M main
git push -u origin main
```

> This keeps your full source code in the `main` branch.

### 2. Build the static site
Use Hugo to generate the final website:

```powershell (Windows) or bash (Linux)
hugo --minify
```

> The output will be placed in the `public/` directory.

### 3. Deploy the contents of `public` to `gh-pages`
You'll now push only the contents of the `public/` folder to a __**separate branch**__:

```powershell (Windows) or bash (Linux)
cd public
git init
git checkout -b gh-pages
git remote add origin https://github.com/<username>/my-hugo-site.git
touch .nojekyll
git add .
git commit -m "Deploy site to GitHub Pages"
git push -f origin gh-pages
```

> `touch .nojekyll` disables Jekyll prcessing on Github Pages, which can interfere with Hugo's folder structure (e.g. `/assets/`).

### 4. Configure GitHub Pages
1. Go to your repository on GitHub
2. Open __**Settings**__ -> __**Pages**__
3. Under __**Source**__, choose:
    - Branch: `gh-pages`
    - Folder: `/ (root)`
4. Save

> Your site will be available at: `https://<username>.githubio/<repo>/`

## Bonus: Automate Deployment
Instead of manually pushing `public/`, you can automate this with [GitHub Actions](https://github.com/features/actions).

## Resources
- [Hugo Docs](https://gohugo.io/documentation/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Ananke Theme](https://github.com/theNewDynamic/gohugo-theme-ananke)

You're now ready to build and publish static sites with Hugo!
Go back to [Hugo Tutorial: Start Here](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/index/)
