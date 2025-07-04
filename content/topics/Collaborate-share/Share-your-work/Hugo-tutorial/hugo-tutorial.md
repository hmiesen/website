---
type: "hugo-tutorial"
indexexclude: "true"
title: "Hugo Tutorial"
description: "Learn how to install and use Hugo, a famous static site generator."
keywords: "hugo, static, website, generator, class, academic"
draft: false
weight: 11
date: 2021-07-04
author: "Harold Miesen"
---

## Tutorial: Create Static Sites with Hugo Extended on Windows
This guide walks you through installing **Hugo Extended** on Windows using `winget`, and helps you get started with your first Hugo project. We’ll begin with a quick introduction to **Markdown**, since it’s the foundation of how content is created in Hugo.

## What is Markdown?
Markdown is a lightweight markup language that allows you to format text using plain-text syntax. It’s easy to read and write, and it converts to clean HTML behind the scenes. Hugo uses Markdown files (`.md`) for all content — such as blog posts, documentation pages, or static content.

### Why Use Markdown?
- Easy to write and read in raw form
- Ideal for version control (like Git)
- Supported by many tools, editors, and platforms
- Clean conversion to HTML and other formats

## Common Markdown Syntax (Live Table)

<table>
  <thead>
    <tr>
      <th>Markdown Syntax</th>
      <th>Rendered Output</th>
      <th>How to Write It</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code># Heading</code></td>
      <td><h1>Heading</h1></td>
      <td><code># Heading</code></td>
    </tr>
    <tr>
      <td><code>**bold**</code></td>
      <td><strong>bold</strong></td>
      <td><code>**bold**</code></td>
    </tr>
    <tr>
      <td><code>*italic*</code></td>
      <td><em>italic</em></td>
      <td><code>*italic*</code></td>
    </tr>
    <tr>
      <td><code>`inline code`</code></td>
      <td><code>inline code</code></td>
      <td><code>`inline code`</code></td>
    </tr>
    <tr>
      <td>Code block</td>
      <td><pre><code></code></pre></td>
      <td><pre><code>```bash
hugo new site mysite
```</code></pre></td>
    </tr>
    <tr>
      <td><code>[OpenAI](url)</code></td>
      <td><a href="https://openai.com">OpenAI</a></td>
      <td><code>[OpenAI](https://openai.com)</code></td>
    </tr>
    <tr>
      <td><code>- Item</code></td>
      <td>
        <ul>
          <li>Item list</li>
        </ul>
      </td>
      <td><pre><code>- First item
- Second item</code></pre></td>
    </tr>
    <tr>
      <td><code>1. Item</code></td>
      <td>
        <ol>
          <li>Numbered list</li>
        </ol>
      </td>
      <td><pre><code>1. First item
2. Second item</code></pre></td>
    </tr>
    <tr>
      <td><code>&gt; Quote</code></td>
      <td><blockquote>This is a quote</blockquote></td>
      <td><code>&gt; This is a quote</code></td>
    </tr>
  </tbody>
</table>

## Why Use Hugo Extended?
Hugo Extended includes all the features of standard Hugo, plus:

- SCSS/SASS support (for styling with modern themes)
- Better compatibility with theme pipelines
- Support for asset bundling and minification

Many popular Hugo themes require the **Extended** version.

---

## Installing Hugo Extended on Windows (via `winget`)

### Step 1: Open PowerShell or Command Prompt as Administrator

Search for "PowerShell", right-click it, and select **"Run as administrator"**.

Then run:

```bash
winget install Hugo.Hugo.Extended
```

### Step 2: Confirm Installation

After installation, check that Hugo is available:

```bash
hugo version
```

Expected output (example):

```
hugo v0.124.1+extended windows/amd64 BuildDate=...
```

Look for `+extended` in the version string — this confirms you're using the Extended version.

---

## Getting Started with Hugo

### Step 3: Create a New Hugo Site

In your terminal:

```bash
hugo new site my-site
```

This creates a new folder called `my-site` with the basic directory structure.

### Step 4: Add a Theme

Change into the site folder:

```bash
cd my-site
```

Then add a theme as a Git submodule. Example using the Ananke theme:

```bash
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke themes/ananke
```

### Step 5: Configure the Theme

Open the `config.toml` file and add:

```toml
theme = "ananke"
```

You can also customize the site title and other settings here.

### Step 6: Add Your First Page

```bash
hugo new about_me/hello-world.md
```

Edit the newly created Markdown file in `content/about_me/`.

---

## Start the Local Server

```bash
hugo server -D
```

Then open your browser and go to:  
[http://localhost:1313](http://localhost:1313)

You should see your new Hugo site running locally!

---

## Project Folder Structure (Simplified)

```
my-site/
├── config.toml
├── content/
│   └── about_me/
├── themes/
│   └── ananke/
└── public/ (generated after build)
```

## Deploying Your Hugo Site to GitHub Pages

This guide walks you through publishing your Hugo static website using **GitHub Pages**.

### Step 1: Create a GitHub Repository
1. Go to [https://github.com](https://github.com)
2. Click **New repository**
3. Name your repo, for example: `my-hugo-site`
4. Leave **README**, **.gitignore**, and **license** unchecked
5. Click **Create repository**

---

### Step 2: Initialize Git in Your Hugo Project
Open a terminal in the root of your Hugo site (where `config.toml` is located):

```bash
git init
git remote add origin https://github.com/<your-username>/my-hugo-site.git
git add .
git commit -m "Initial commit"

---

## Useful Resources

- [Hugo Documentation](https://gohugo.io/documentation/)
- [Markdown Cheatsheet](https://www.markdownguide.org/cheat-sheet/)
- [Hugo Themes](https://themes.gohugo.io/)
- [Winget Documentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

---

Happy building! 🚀
