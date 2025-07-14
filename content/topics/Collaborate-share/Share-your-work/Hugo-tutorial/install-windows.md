---
type: "hugo-tutorial"
title: "Install Hugo Extended on Windows using winget"
description: "Instructions for installing Hugo Extended on Windows using winget."
draft: false
weight: 2
date: 2025-07-07
author: "Harold Miesen"
---

## Install Hugo Extended on Windows using winget

### Step 1: Open PowerShell as Administrator

Search for **PowerShell**, right-click it, and choose **Run as administrator**.

### Step 2: Install Git (if not already installed)

```powershell
winget install --id Git.Git -e --source winget
```

> If `git` is not yet installed, the command above will install it.

Check Git installation:
```powershell
git --version
```

You should see a version number if Git is correctly installed.

### Step 3: Install Hugo Extended

```powershell
winget install Hugo.Hugo.Extended
```

> __**Tip**__: Uninstall any previous Hugo version first to avoid conflicts.

### Step 4: Confirm Installation

```powershell
hugo version
```

Look for `+extended` in the output.
Hugo Extended is now installed on Windows!


---


Done installing? Proceed to the [Hugo Usage Guide](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/content/) or go back to [Hugo Tutorial: Start Here](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/index/).
