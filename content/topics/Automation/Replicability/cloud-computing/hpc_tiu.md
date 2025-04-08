---
title: "HPC TiU for Cloud Computing"
description: "A free cloud solution from Tilburg University for heavy computation tasks (employees only)."
keywords: "cloud, virtual computers, HPC TiU, infrastructure, parallel, research cloud"
weight: 1
draft: false
author: "Roshini Sudhaharan"
authorlink: "https://nl.linkedin.com/in/roshinisudhaharan"
aliases:
  - /configure/research-cloud
---

## HPC TiU: Overview

HPC TiU (High Performance Computing, previously known as TiU Blade Computing) is one of TiU's academic computing environments and started out as a shared workspace for TiSEMS's Finance Department. Its primary purpose was and still is to provide researchers with a shared environment with a lot more sources (memory and processing power) available in contrast to a regular workstation.

{{% warning %}}
__**Important Note**__

Every Tilburg University employee can gain access to the Tilburg University HPC environment. However, the environment is not available to students. Hence, many of the web links in this article may lead to pages on Tilburg University's intranet, which require you to log in with a Tilburg University username that has employee access rights.

Access for external researchers is possible. The guest researcher must have a Tilburg University username, known as a PNIL account (staff-not-on-payroll). A PNIL account can be requested through the HRM department.
{{% /warning %}}

HPC TiU is an interactive environment which looks and feels like a regular TiU Windows workspace. It's a cloud-solution, which means it's available from anywhere in the world (provided there's an internet connection available). Through this environment users have access to a selection of popular statistical software and programming tools, some of which are licensed to use on campus only.

<p align = "center">
<img src = "../images/blade.png" width="600">
<figcaption> Pros and Cons of Using HPC TiU </figcaption>
</p>

### How to request access to HPC TiU?

You can [request access to HPC TiU](https://servicedesk.uvt.nl/tas/public/ssp/content/detail/knowledgeitem?unid=db72c119bf344fb78a196d5b6c669ecc) via the IT Service Desk and filling in a form. Access for external researchers is possible. The guest researcher needs to have a Tilburg University username, and a so-called PNIL-account (staff-not-on-payroll). These accounts can be requested at the HRM department.

Once your request is approved, you can access HPC TiU. HPC TiU servers are protected with MFA, Therefore, you have to make sure you have MFA set up for your account.

### Connecting to HPC TiU through an RDP (Remote Desktop Protocol) connection file

Connect to HPC TiU using the following URL: [https://rdweb.campus.utvt.nl/RDWeb](https://rdweb.campus.utvt.nl/RDWeb). Log in with your TiU user account (campus\\[username]) and password. Select HPC TiU and your settings file will be downloaded. Double-click that file and your session will start. For your convenience, you can place this file on your desktop and use it again later. After clicking connect, your client is going to set up a connection to the HPC TiU server. At that point, the MFA request will be sent to your mobile device. After authorizing the MFA request, your session is started on the HPC TiU server.

### Connecting to HPC TiU through the webinterface (all OS's)

Alternatively connect through the webinterface to the HPC TiU environment using the following URL: [https://rdweb.campus.uvt.nl/RDWeb/webclient/](https://rdweb.campus.uvt.nl/RDWeb/webclient/). Any OS (__**Windows, macOS, ChromeOS or Linux**__) in combination with a modern browser will do. In this case, you also do not need to download an RDP connection file. Log in with your TiU user account and password. At this point, the MFA request will be sent to your mobile device. Choose your preferences regarding local resources access.

### Sensitive datasets

If you use sensitive data, you should be aware of how or "where" this data is used. You should treat sensitive data with special care and if you're unsure please ask for information from LIS on how to proceed. For example, if one uses a dataset which may only be used on the university campus it could be very likely one may not use HPC TiU.

### Where to Save your Files?

**Local drive access**

- When using HPC TiU users have access to the local drive of their client computer. It is not recommended using this feature for sensitive data since your local machine might be compromised without you realizing this. Besides that, it's a very slow method.

**Shared folders**

- Users should be aware that, especially with shared folders (like O:-drive) it's possible that other users can (un)intentionally alter files. This could potentially influence the outcome of research using those files. The Tilburg University O:-drive, as is the M:-drive, is backed up daily and it's therefore possible to restore a compromised file to a previous state. The retention time (time backups are kept) is two weeks.

- The C:-drive is only intended for the Operating System and Applications.

- The local scratch drives (D:-drive) can be used to create a sub-folder under D:\Data to place the files that require fast disk accesss. To this end the servers are equipped with Solid State Drives (SSD's). Be aware that any data will be removed during the monthly maintenance window.

- The S:-drive is not being backed up. This drive is intented as a bulk storage for data that at any time can be reproduced or retrieved from its source.

{{% warning %}}
__**Scheduled maintenance**__

Every __**Friday after the 2nd Tuesday of the month**__ the TiU HPC servers will be put offline for maintenance. LIS reserves 7:30 am until 12 am to perform necessary maintenance on the servers. Do **NOT** run your analyses when maintenance is performed, because unsaved work will be lost. __**Any personal data stored locally on the servers and the scratch discs will be removed**__ during the maintenance window.
{{% /warning %}}

{{% tip %}}
Here is an additional cloud computing solution you might want to check out to level up your research infrastructure: [SURFsara's Cartesius Cluster](https://tilburgsciencehub.com/topics/automation/replicability/cloud-computing/cartesius_cluster/)
{{% /tip %}}
