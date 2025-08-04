---
title: "Using Hugo: Create and Deploy a Static Site"
description: "Learn how to launch your site with Hugo after installation"
draft: false
weight: 4
date: 2025-07-07
author: "Harold Miesen"
---

## Using Hugo: Create and Deploy a Static Site

Hugo is a powerful static site generator that transforms plain text and templates into fast,
secure, and fully pre-rendered websites. Unlike dynamic sites that rely on databases, static
sites are composed of HTML files that can be easily hosted anywhere—from GitHub Pages to
cloud providers—with excellent performance and minimal maintenance.

### Step 1: Create a New Project
Start by opening a terminal window:

- Windows: open __**powershell**__
- Linux: open the __**terminal**__ application.

> The terminal starts in a default folder, but you can choose where to create your Hugo project.

Use the `cd` command to move into the folder where you'd like to store your Hugo project. For example:

__**Windows powershell**__:

```
cd ~\Documents\Websites
```
__**Linux**__

```
cd ~/Documents/Websites
```

The tilde (`~`) is a shortcut that represents your __**home directory**__—your personal user folder.

- On __**Windows**__ (powershell): `~` means something like `C:\Users\YourName`
- On __**Linux**__: `~` means something like `/home/Yourname`

So when you run `cd ~/Documents` you're navigating to the `Documents` folder inside your home directory.

You can also create a new folder first:

```
mkdir HugoProjects
cd HugoProjects
```

Create a new Hugo site by running the following command in the folder in which you want to create the site:

```
hugo new site my-hugo-site
cd my-hugo-site
```

This creates a new folder called my-hugo-site in your current directory. Hugo will place all the
starter files inside that folder.

> For example, if you're in `C:\Users\YourName\Documents\HugoProjects`, the new project will be
created at `C:\Users\YourName\Documents\HugoProjects\my-hugo-site`.

> __**TIP**__: Choose a meaningful name for your project folder. You can manage multiple Hugo sites
independently.

### Step 2: Add a Theme (Ananke)
Add the [Ananke](https://github.com/theNewDynamic/gohugo-theme-ananke) theme using Git submodules:

```
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke

```
> __**Why Ananke**__? It's a modern, responsive, and accessible theme - great for learning and
production alike.

By now, you should have a directory structure looking something like this:

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
Edit hugo.toml in your favorite editor and set basic site configuration by adding the
following lines:

```
baseURL = "http://localhost/"
languageCode = "en-us"
title = "My Hugo Site"
theme = "ananke"
```

__**Additional settings**__ you may want to add:
```
paginate = 10
enableRobotsTXT = true
```

If you’d like Hugo to automatically add front matter when creating new content, you can define
a default archetype.

Create a file at `archetypes/default.md`.

And add the following content:

```
---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
---
```

- When you run a command like hugo new about.md, Hugo will use this template.
- The title will be auto-generated from the filename (e.g., about becomes About).
- The date is set to the current timestamp.
- The page will be created as a draft, which you can later publish by setting `draft: false`.

### Step 4: Run Local Server
Start the Hugo development server in __**the root**__ of your project:
```
hugo server -D
```

Visit [http://localhost:1313](http://localhost:1313) in your browser.

> - Live reload is enabled - changes are reflected immediately.
> - The -D flag in hugo server includes draft content in the local build, which is useful during
development but should be avoided in production to prevent publishing unfinished work.

### Bonus: Deploy to GitHub Pages (Recommended Setup)

#### 1. Commit your project source to main
Make sure your Hugo project (including content, theme, and config files) is version-controlled:

```
git init
git add .
git commit -m "Initial commit with Hugo source files"
git remote add origin https://github.com/<your-username>/my-hugo-site.git
git branch -M main
git push -u origin main
```

> This keeps your full source code in the `main` branch.

#### 2. Build the static site
Go to the root of your project and use Hugo to generate the final website:

```
hugo --minify
```

> The output will be placed in the `public/` directory.

#### 3. Deploy the contents of `public` to `gh-pages`
You'll now push only the contents of the `public/` folder to a __**separate branch**__:

```
cd public
git init
git checkout -b gh-pages
git remote add origin https://github.com/<your-username>/my-hugo-site.git
touch .nojekyll
git add .
git commit -m "Deploy site to GitHub Pages"
git push -f origin gh-pages
```

> `touch .nojekyll` disables Jekyll prcessing on Github Pages, which can interfere with Hugo's
folder structure (e.g. `/assets/`).

#### 4. Configure GitHub Pages
1. Go to your repository on GitHub
2. Open __**Settings**__ -> __**Pages**__
3. Under __**Source**__, choose:
    - Branch: `gh-pages`
    - Folder: `/ (root)`
4. Save

> Your site will be available at: `https://<username>.githubio/<repo>/`

### Bonus: Deploy to Nginx Server (Advanced Alternative Setup)

#### 1. Build the static site
First, generate your Hugo site from the root of your project:

```
hugo --minify
```

Hugo will output the static site to the `public/` directory.

#### 2. Connect to your server
Use SSH to connect to your server:

```
ssh	&lt;your-username&gt;@&lt;your-server-ip&gt;
```

Make sure your server has nginx installed and running. You can check with: `nginx -v`.

> You can find an Install Guide on nginx [here](https://nginx.org/en/docs/install.html).
> [Here](https://nginx.org/en/docs/beginners_guide.html) is a Beginner's Guide that describes some simple tasks that can be done with it.

#### 3. Upload your site files
Use `scp` or any file transfer method (like rsync, FTP, etc.) to upload the contents of the `public/` directory to your server.

For example, using `scp`:

```
scp -r public/* &lt;your-username&gt;&lt;your-server-ip&gt;:/var/www/&lt;your-site&gt;/
```

Make sure `/var/www/<your-site>/` is the correct path where your nginx site will serve content from.

### 4. Configure Nginx
Create or edit an nginx configuration file for your site:

```
sudo nano /etc/nginx/sites-available/&lt;your-site&gt;
```

Example configuration:

```
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/&lt;your-site&gt;;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Enable the site:

```
sudo ln -s /etc/nginx/sites-available/&lt;your-site&gt; /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

This tells Nginx to serve your static Hugo site.

### 5. (Optional) Add a domain name
Make sure your domain's DNS points to your server IP, and update `server_name` in the config accordingly.

Your site should now be live at `http://<yourdomain.com>` or `http://<your-server-ip>`.

### Bonus: Automate Deployment
Instead of manually pushing `public/`, you can automate this with [GitHub Actions](https://github.com/features/actions).

You're now ready to add content to your static Hugo site and to continue to the 
[Adding content to your Hugo site](../5-add-content/),
or go back to [Hugo Tutorial: Start Here](../1-index/).
