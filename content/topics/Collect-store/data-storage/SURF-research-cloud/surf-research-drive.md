---
title: "Set up SURF Research Drive to Store Data"
description: "Learn how to set up a Research Drive account, upload and download files, share files and folders, and use owncloud and rclone to selectively retrieve files from command line and code."
keywords: "surf, rd, resarch drive, owncloud, rclone, large files, webdav, store, storage"
weight: 1
draft: false
author: "Harold Miesen,Kars Wijnhoven"
authorlink: "https://www.linkedin.com/in/haroldmiesen/"
aliases:
  - /setup/research-drive
  - /use/research-drive
  - /setup/owncloud
  - /setup/rclone
---

## What is SURF Research Drive?

__**[SURF Research Drive](https://www.surf.nl/en/research-drive-securely-and-easily-store-and-share-research-data)**__ is a secure cloud storage platform developed by [SURF](https://www.surf.nl/en), the collaborative organisation for ICT in Dutch education and research. Throughout this guide, we will refer to it simply as Research Drive or RD. It is especially useful for storing large datasets and collaborating with internal and external partners - including students, companies, and international colleagues.​

{{% warning %}}

SURF services are only available for researchers affiliated with Dutch institutions.

{{% /warning %}}

Key features of Research Drive (RD) include:​

1. Project-Based Storage: Data is tied to the project rather than individual users, so access remains even if team members leave.

1. Flexible Collaboration: You can share folders and files with others inside or outside your organization. Folder owners can create user groups, manage permissions (read/write), and organize folder structures. Ownership is transferable.

1. Integration with Other (SURF) Services: You can connect easily RD with High Performance Computing and other services.

1. Support and Storage at Tilburg University: At Tilburg University, data stewards can assist with folder setup, permissions, and overal storage management. Researchers can use up to 500 GB at no cost. For larger storage needs, additional space can be requested. Contact the [Research Data Office](mailto:rdo@tilburguniversity.edu) if you have any questions.

<p align = "center">
<img src = "../images/surf-research-drive.png" width="600">
<figcaption>Pros and Cons of Using SRD</figcaption>
</p>

## How to Gett Access

{{% warning %}}

Some links below lead to Tilburg University's intranet and require login.

{{% /warning %}}

Tilburg University researchers can request a folder by filling in this [Self Service Portal form](https://servicedesk.uvt.nl/tas/public/ssp/content/detail/service?unid=8fae79bb308044f39c4d6c03478882c8&from=25e5484c-7a81-4b49-b872-5176e950adce). The project folder owner and other project members can invite collaborators and give access to the (sub)folder(s).

Need help? Reach out to the [Research Data Office](mailto:rdo@tilburguniversity.edu) for guidance.

## Accessing your Files

There are [several ways to upload or download your files](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827677/How+to+upload+or+download+your+files) to and from RD, some of which are:

1. Via the Web Interface (browser).
1. With the ownCloud Desktop client.
1. Via rclone (command line).

### Upload Recommendations
Uploading data to Research Drive can be done in a few different ways depending on your needs. RD can handle simultaneous uploads of files up to several gigabytes through __**the browser**__. If you're working with a large number of files or want to keep folders synced automatically, __**the ownCloud client**__ is your best bet. It also resumes uploads automatically if something goes wrong. If you want to upload even larger data sets and you are comfortable with command line, we recommend using tools like __**curl**__ or __**rclone**__. These give you greater control and are ideal for automated of scripted workflows.

<p align = "center">
<img src = "../images/browser-owncloud-rclone.png" width="600">
<figcaption>When to use which tool or service given the number of files and the size per file</figcaption>
</p>

### Ad 1. Web Interface

The easiest way to access RD is via the browser.

1. Visit [researchdrive.surf.nl/index.php/login](https://researchdrive.surfsara.nl/index.php/login) or the institutional instance of your institution. For Tilburg University, use [tilburguniversity.data.surf.nl/index.php/login](https://tilburguniversity.data.surfsara.nl/index.php/login).

1. Login with __**SURFconext**__ or [eduID](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/166560110/Research+Drive+How+to+create+an+eduID+account).

1. You can now browse, upload, and download files - similar to Dropbox or Google Drive.

### Ad 2. OwnCloud Desktop Client

To easily collaborate on research, you can synchronize documents to your local workstation through the [ownCloud Desktop Client](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827682/ownCloud+desktop+client). The ownCloud Desktop Client keeps your RD files in sync with a folder on your harddisk. 


{{% tip %}}

If you want to use RD to synchronize data with SURF Research Cloud (SRC), it's worth reading the following article: [Getting Started with SURF Research Cloud](http://localhost:8070/topics/Automation/Replicability/cloud-computing/getting-started-research-cloud/). This article suggests OwnCloud as a good alternative for synchronizing data with SRC, as RD is causing issues at the time of writing. Please read the article for more details on these issues.

{{% /tip %}}

### Ad 3. Via rclone

[Rclone](https://rclone.org) is an open-source command line program to manage files on cloud storage. You can use it to selectively access, download, upload, move and delete data on RD. This will save you disk space: you won't need to download the entire project directory on your local disk, but only the files that you need.

The key advantage of using __**rclone**__ is that you can work with files programmatically, __**from the command line or your code directly**__.

## Install Rclone

### On Windows (Tilburg University)

1. In [RD](URL: tilburguniversity.data.surfsara.nl/index.php/login), under 'Security', create a token for Rclone and note down the username and password.

1. Download [Rclone for Windows](https://rclone.org/downloads/). Make sure you know __**which folder**__ your rclone.exe is in, e.g., `C:\Tools\rclone\rclone.exe`.

1. Open __**PowerShell**__ in Windows.

1. Type in `cmd.exe`.

1. Navigate to __**the folder**__ where the rclone.exe file is located.

1. Type `rclone config`.

1. Follow the steps and complete the configuration (Name: `RD`, URL: `https://tilburguniversity.data.surfsara.nl/remote.php/nonshib-webdav`; username: `username`; password: `password`).

1. Add __**the folder path**__ in the "Environment Variables" window, under User variables for [your usernname], e.g., `C:\Tools\rclone`.

1. Test it by opening __**a new Command Prompt**__ (`cmd`) or __**PowerShell**__ window and by typing `rclone --version`.

1. You are now __**ready to use**__ rclone commands, e.g., `rclone copy file.txt "RD:User (Projectfolder)/Documents"`.

### On Linux

1. First, you will need to install __**rclone**__. Download from [rclone.org](https://rclone.org/downloads/), or run the following command on your personal machine in __**bash**__: `curl https://rclone.org/install.sh | sudo bash`.

{{% tip %}}
On computing services and research clusters (HPC), make sure that `module load rclone` is in your `./bash_profile`.
{{% /tip %}}

1. Run the following command in __**bash**__ to configure rclone: `rclone config`. You will be guided through the configuration. You can read this [comprehensive guide](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/102827686/Access+Research+Drive+via+Rclone) on how to configure it properly.

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

You can find instructions on how to use it [here](https://pypi.org/project/python-rclone/).

## Share your Files

You can share files in RD by:

1. Giving access to other RD users.
1. Creating public links (if your institution allows it).

Follow [this guide](https://wiki.surfnet.nl/display/RDRIVE/How+to+share+a+folder+or+file) to learn how to do it.

{{% warning %}}

Tilburg University disabled sharing with public links for security reasons.

{{% /warning %}}

If you need technical support - such as configuring Rclone or connecting Research Drive with SURF Research Cloud - feel free to contact the [Digital Research Support (DRS)](https://www.tilburguniversity.edu/intranet/research-support-portal/drs) team at [digitalresearchsupport@tilburguniversity.edu](mailto: digitalresearchsupport@tilburguniversity.edu).
