---
title: "Install Hugo Extended on Linux using wget"
description: "Install Hugo Extended for native Linux environments using wget."
draft: false
weight: 4
date: 2025-07-07
author: "Your Name"
---

## Install Hugo Extended on Linux using wget

### Step 1: Update and Install Prerequisites

```bash
sudo apt update && sudo apt install git curl wget tar
```

> If `git` is not yet installed, the command above will install it.

### Step 1.1: Verify Git Installation

```bash
git --version
```

You should see a version number if Git is correctly installed.

### Step 2: Download and Install Hugo Extended

Visit the [Hugo Releases](https://github.com/gohugoio/hugo/releases) to get the latest version.

```bash
wget https://github.com/gohugoio/hugo/releases/download/v0.124.1/hugo_extended_0.124.1_Linux-64bit.tar.gz
mkdir -p ~/hugo && tar -xvzf hugo_extended_0.124.1_Linux-64bit.tar.gz -C ~/hugo
sudo mv ~/hugo/hugo /usr/local/bin/
```

### Step 3: Check Installation

```bash
hugo version
```

Look for `+extended` in the output.
Hugo Extended is now installed on WSL!

---

Done installing? Proceed to the [Hugo Usage Guide](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/content.md) or go back to [Hugo Tutorial: Start Here](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/index/).
