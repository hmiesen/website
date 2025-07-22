---
type: "hugo-tutorial"
title: "Install Hugo Extended on Windows using winget"
description: "Instructions for installing Hugo Extended on Windows using winget"
draft: false
weight: 2
date: 2025-07-07
author: "Harold Miesen"
---

## Install Hugo Extended on Windows using winget

Why should you use winget?

__**Winget**__ (Windows Package Manager) is Microsoft’s official command-line tool for installing software on Windows, much like brew on macOS or apt on Linux. It simplifies the installation and updating of software directly from the terminal.

Using winget to install Hugo ensures that:

- You get the latest version (including Extended),

- It’s installed system-wide in a predictable location,

- You can update it later just by running winget upgrade.

### Step 1: Open PowerShell as Administrator

Search for __**PowerShell**__, right-click it, and choose __**Run as administrator**__.

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

> ```powershell
> winget uninstall Hugo.Hugo.Extended
> ```

> After removal, check:

> ```powershell
> hugo version
> ```

> If Hugo has been succesfully removed from your system, you should see the following error message: `hugo : The term 'hugo' is not recognized...`. 

### Step 4: Confirm Installation

```powershell
hugo version
```

Look for `+extended` in the output.
Hugo Extended is now installed on Windows!


---


Done installing? Proceed to the [Launch Site](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/4-launch-site/) page or go back to [Hugo Tutorial: Start Here](/topics/Collaborate-share/Share-you-work/Hugo-tutorial/1-index/).
