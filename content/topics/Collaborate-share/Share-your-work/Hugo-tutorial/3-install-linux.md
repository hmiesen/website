---
title: "Install Hugo Extended on Linux using snap"
description: "Install Hugo on a Linux environment using snap"
draft: false
weight: 3
date: 2025-07-07
author: "Harold Miesen"
---

## Install Hugo Extended on Linux using snap

Snap is a universal package manager developed by Canonical (the makers of Ubuntu). It allows you to install software in isolated containers, which include all necessary dependencies — making it easy to run the latest versions of applications across different Linux distributions.

Using snap to install Hugo ensures:

- You get the Extended version by default,
- Automatic updates,
- Fewer dependency issues across distros.

### Step 1: Update Your System

```bash
sudo apt update && sudo apt upgrade
```

### Step 2: Install Required Packages

```bash
sudo apt install git curl wget tar
```

> If `git` is not yet installed, the command above will install it.

### Step 2.1: Verify Git Installation

```bash
git --version
```

You should see a version number if Git is correctly installed.

### Step 3: Install Snap (if not already installed)

```bash
sudo apt install snapd
```

> `snapd` is the background service used to manage snap packages.

### Step 4: Install Hugo Extended via Snap

```bash
sudo snap install hugo --channel=extended --classic
```

> The `--channel=extended` flag ensures you get the Hugo Extended version (required for SCSS/SASS).
The `--classic` flag gives Hugo permission to access the full system, which is necessary for many real-world use cases.

### Step 4: Verify Installation

```bash
hugo version
```

You should see output like:

```bash
hugo v0.124.1+extended linux/amd64 BuildDate=...
```

Look for `+extended` in the output.
Hugo Extended is now installed on Linux!

---

Done installing? Proceed to the [Launch Site](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/4-launch-site/) page or go back to [Hugo Tutorial: Start Here](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/1-index/).
