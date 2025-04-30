---
title: "Set up SURF Research Drive to Store Data"
description: "Learn how to set up a Research Drive account, upload and download files, share files and folders, and use owncloud and rclone to selectively retrieve files from command line and code."
keywords: "surf, rd, resarch drive, owncloud, rclone, large files, webdav, store, storage"
weight: 1
draft: false
author: "Harold Miesen"
authorlink: "https://www.linkedin.com/in/haroldmiesen/"
aliases:
  - /setup/research-drive
  - /use/research-drive
  - /setup/owncloud
  - /setup/rclone
---

## What is SURF Research Drive?

__**[SURF Research Drive (SRD)](https://www.surf.nl/en/research-drive-securely-and-easily-store-and-share-research-data)**__ is a cloud-based storage service developed by [SURF](https://www.surf.nl/en), the collaborative organisation for ICT in Dutch education and research. It is designed to support research teams that require substantial storage capacity and secure, collaborative data sharing.​

{{% warning %}}

SURF services are only available for researchers affiliated with Dutch institutions.

{{% /warning %}}

Key features of Research Drive (RD) include:​

1. Team-Based Storage: Data is organised per project rather than per individual, ensuring continuity and accessibility even if team members change.

1. Secure Collaboration: Facilitates safe and structured data sharing with researchers and partners, both within and outside the Netherlands.

1. Integration with Other Services: Offers seamless access to multiple storage environments, providing a unified view of data across various platforms.

1. Data Stewardship: Each project is managed by a data steward responsible for organising folder structures, managing user access, and allocating storage quotas.

Research Drive is particularly suitable for research teams that need to store large volumes of data securely and collaborate efficiently across institutional boundaries.​

<p align = "center">
<img src = "../images/surf-research-drive.png" width="600">
<figcaption>Pros and Cons of Using SRD</figcaption>
</p>

## Obtain an Account

{{% warning %}}

Some of the web links in this article may lead to pages on Tilburg University's intranet. You need to log in to the intranet with your Tilburg University credentials to access the pages behind these weblinks.

{{% /warning %}}

If you are an employee at Tilburg University, you can request access to RD by contacting the [Research Data Office](https://www.tilburguniversity.edu/intranet/research-support-portal/rdm/advice). Ask a team member to grant you access to the directories required for your project(s).

## Access your Files

There are [several ways to upload or download your files](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827677/How+to+upload+or+download+your+files) to and from RD, some of which are:

1. Via the RD Web Interface.
1. With the ownCloud Desktop client.
1. Via rclone.

### Upload Recommendations
RD can handle simultaneous uploads of files up to several gigabytes through __**the browser**__. For larger number of files __**the ownCloud client**__ is highly recommended as it will automatically handle large number of files and upload resumption in case of upload problems. If you want to upload even larger data sets and when you are familiar with your system's command line interface, it is recommended to use an upload client like __**curl**__ or __**rclone**__.

<p align = "center">
<img src = "../images/browser-owncloud-rclone.png" width="600">
<figcaption>When to use which tool or service given the number of files and the size per file</figcaption>
</p>

### Ad 1. Via the RD Web Interface

The easiest way to access RD is via the browser.

1. Visit [researchdrive.surf.nl/index.php/login](https://researchdrive.surfsara.nl/index.php/login) or the institutional instance of your institution. For Tilburg University, use the following link: [tilburguniversity.data.surf.nl/index.php/login](https://tilburguniversity.data.surfsara.nl/index.php/login).

1. If you have an university account, login via __**SURFconext**__. Otherwise you can login using your [eduID](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/166560110/Research+Drive+How+to+create+an+eduID+account).

1. You can now access your folders and files in your RD. You can also upload and download files directly from your browser, like how you would do on Google Drive or Dropbox.

### Ad 2. With OwnCloud Desktop Client

To easily collaborate on research, you can synchronize documents to your local workstation through the [ownCloud Desktop Client](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827682/ownCloud+desktop+client). The ownCloud Desktop Client keeps your RD files in sync with a folder on your harddisk. 

### Ad 3. Via rclone

[Rclone](https://rclone.org) is an open-source command line program to manage files on cloud storage. You can use it to selectively access, download, upload, move and delete data on RD. This will save you disk space: you won't need to download the entire project directory on your local disk, but only the files that you need.

The key advantage of using __**rclone**__ is that you can work with files programmatically, __**from the command line or your code directly**__.

## Install Rclone

### Install on Windows (RD Tilburg University)

1. In [RD](URL: tilburguniversity.data.surfsara.nl/index.php/login), under 'Security', create a token for Rclone. Note down the username and password provided by RD.

1. Download [Rclone for Windows](https://rclone.org/downloads/). Make sure you know __**which folder**__ your rclone.exe is in, e.g., `C:\Tools\rclone\rclone.exe`.

1. Open __**PowerShell**__ in Windows.

1. Type in `cmd.exe`.

1. Navigate to __**the folder**__ where the rclone.exe file is located.

1. Type `rclone config`.

1. Follow the steps and complete the configuration (Name: `RD`, URL: `https://tilburguniversity.data.surfsara.nl/remote.php/nonshib-webdav`; username: `username`; password: `password`).

1. Add __**the folder path**__ in the "Environment Variables" window, under User variables for [your usernname], e.g., `C:\Tools\rclone`.

1. Test it by opening __**a new Command Prompt**__ (`cmd`) or __**PowerShell**__ window and by typing `rclone --version`.

1. You are now __**ready to use**__ rclone commands, e.g., `rclone copy file.txt "RD:User (Projectfolder)/Documents"`.

### Install on Linux

1. First, you will need to install __**rclone**__. Download from [rclone.org](https://rclone.org/downloads/), or run the following command on your personal machine in __**bash**__: `curl https://rclone.org/install.sh | sudo bash`.

{{% tip %}}
On computing services and research clusters (HPC), make sure that `module load rclone` is in your `./bash_profile`.
{{% /tip %}}

1. Run the following command in __**bash**__ to configure rclone: `rclone config`. You will be now guided through the configuration. You can read this [comprehensive guide](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827686/Access+Research+Drive+via+Rclone) on how to configure it properly.

## Use Rclone (Windows and Linux)

### Some useful commands

#### List all files in directory
```
rclone ls RD:
```

#### Copy source directory to destination directory
```
rclone copy /my/folder RD:my/destination/folder
```

{{% tip %}}
You can find these and many more command examples on this [comprehensive guide on accessing and using rclone with Research Drive](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827686/Access+Research+Drive+via+Rclone).
{{% /tip %}}

### Use rclone in your (python) code

In order to use __**rclone**__ directly in your code, you will need a wrapper like __**python-rclone**__ for Python. You can install it with:
```bash
pip install python-rclone
```

You can find instructions on how to use it __**[here](https://pypi.org/project/python-rclone/)**__.

## Share your Files

You may want to share your files with other colleagues. You can do so by either sharing them with other RD users or via a public link. Follow [this guide](https://wiki.surfnet.nl/display/RDRIVE/How+to+share+a+folder+or+file) to learn how to do it.

{{% warning %}}

Tilburg University disabled sharing with public links for safety reasons.

{{% /warning %}}

If you need technical support using the RD environment, or if you're looking for a suitable solution for your research, the __**[Digital Research Support (DRS)](https://www.tilburguniversity.edu/intranet/research-support-portal/drs)**__ Team at LIS TiU can assist you. The DRS team can be reached via the following email address: [digitalresearchsupport@tilburguniversity.edu](mailto: digitalresearchsupport@tilburguniversity.edu).
