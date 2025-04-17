---
title: "Getting Started with SURF Research Cloud (SRC)"
description: "A free cloud solution for conducting research."
keywords: "cloud, virtual computers, SURF, infrastructure, parallel, research cloud, service desk"
weight: 5
#date: 2021-01-06T22:01:14+05:30
draft: false
author: "Shrabastee Banerjee,Harold Miesen"
authorlink: "https://sites.google.com/view/shrabastee,https://www.linkedin.com/in/haroldmiesen"
aliases:
  - /configure/research-cloud
  - /get/chromedriver
---

## SURF Research Cloud: Overview

[SURF Research Cloud (SRC)](https://www.surf.nl/en/services/compute/surf-research-cloud) is an easy-to-use online platform that helps you set up your own digital workspace in just a few steps. Without needing advanced IT skills, you can access powerful computing resources, storage, and research software to work with large datasets or perform complex analyses. Everything runs in the cloud, so you can work from anywhere and focus on your research rather than the technical setup.

The platform also makes it simple to collaborate with colleagues by allowing you to share your workspace, tools, and data. SRC offers a reliable, flexible, and secure environment that supports modern research in a wide range of disciplines. You can offer your colleagues secure access to this research environment by means of a simple authentication process through [SURF's Research Access Management (SRAM)](https://www.surf.nl/en/services/identity-access-management/surf-research-access-management).

{{% warning %}}
__**Important Note**__

Access to SRC is available to researchers and staff who are affiliated with a Dutch research or higher education institution that is a member of SURF. However, it's possible to invite external collaborators — such as international partners or researchers from non-member institutions — by granting them guest access, making it easy to work together across organizational boundaries.

{{% /warning %}}

<p align = "center">
<img src = "../images/surf-research-cloud.png" width="600">
<figcaption> Pros and Cons of Using SRC </figcaption>
</p>

### Accessing SURF's compute services
In case you want to become a user of SRC, we refer you to the information on [requesting access](https://www.surf.nl/en/access-to-compute-services) to SURF's compute services. At current, there are three ways of accessing SURF's compute services:

1. __**Small Compute applications (NWO)**__ for limited amounts of computing time, data services, and support directly via SURF (max 1 year, an extension of max 6 months is possible). You can apply for limited amounts of computing time, data services and support at SURF [here](https://www.surf.nl/en/small-compute-applications-nwo).
1. __**Large Compute applications (NWO)**__ for large amounts of computing time, data services and support via the NWO portal (2 years with 1 year extension possible). You can apply for large amounts of computing time on national computing facilities via NWO [here](https://www.nwo.nl/en/calls/computing-time-on-national-computing-facilities).
1. __**Direct access to SURF compute services**__ provided through your institution or based on a contract with SURF directly.

Applications are done through SURF, but funded by [NWO](https://www.nwo.nl/en).

### Access to SRC requested through Small Compute applications (NWO)

Apply for (limited) amounts of computing time: go to [small compute applications (NWO)](https://www.surf.nl/en/small-compute-applications-nwo) and click on the 'Request portal' button. Login with SURFConext selecting your institution and using your institutional credentials. You will be transferred to the Small Compute applications form via the SURF's Servicedesk. Fill out the form. Once your appplication is approved, you will receive an email from SURF to join a Collaboration (CO) and set up your initial workspace. SURF has linked a 'wallet' (an existing budget) to your CO that represents the fact that you have credits to spend on running workspaces. You can check the status of your application at [SURF's service desk](https://servicedesk.surf.nl).

{{% tip %}}

__**Pause your workspace when not in use**__

Don't forget to pause your workspace when you are not working in it. Use the "PAUSE" button. It is visible next to the access button when you extend the display of your workspace. Pausing your workspace helps you to spare your budget. While your workspace is paused, it will not consume any CPU or GPU credits. The configuration of your workspace and the current data on it are preserved.

{{% /tip %}}

### Using SRC and inviting members to your CO

You can find detailed information on how to use SRC [here](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/9798172/SURF+Research+Cloud). If you want to invite admins and member to a collaboration, please visit the following SURF Wiki page: [Invite admins and members to a CO](https://servicedesk.surf.nl/wiki/spaces/IAM/pages/74226148/Invite+admins+and+members+to+a+collaboration).

### Integration of SURF Research Drive (SRD) with SRC

{{% warning %}}

__**Data synchronization with SRD**__

When using a Windows virtual machine, [data synchronization with SRD](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/9798456/Connect+Research+Drive) can be cumbersome. At the moment of writing, SURF has implemented a mechanism that lets you connect SRD to SRC and then displays the SRD folders as a network drive.
However, this functionality is flawed:

* It syncs data through the C-drive which creates a bottleneck for large datasets (the C-drive is set to a maximum of 75GB by default).
* The SRD network drive is shown with the same usage and capacity as the C-drive, which is confusing to you as a user.
* The local cache is cleared only once an hour, thus updating large datasets needs to be in steps of X GB (X being the amount of free space on C). Clearing the cache is, of course, possible, but takes extra manual steps.

We highly advise NOT to use this functionality as it will only be confusing to you as a user, and is inefficient. We have filed an issue at SURF.

{{% /warning %}}

### Alternative for SRD integration: Data Sync with ownCloud (OC)

{{% warning %}}

__**Notes**__

* This use case is only valid when all local data is leading and the remote data needs to be updated to achieve synchronicity between the two.
* The environment variable is not permanent, so when a new session is started, it will no longer be present.

{{% /warning %}}

In the case where there are discrepancies between local and remote data on the workspace (you have already been running analyses on local data), and the local data needs to be synced to the remote SRD, ownCloud is a user-friendly alternative.
However, by default, the ownCloud desktop client will rename the local file (adding something like 'conflict copy datetime' to the filename) and download the remote file. This only leads to redundant data on the local copy and does not achieve of updating the remote storage with the local changes.

The workaround for this is to set an environment variable before running a first OC sync:

1. Open a Powershell terminal with Administrator privileges.
1. Enter the command `setx OWNCLOUD_UPLOAD_CONFLICT_FILES 1`.
1. If you haven't installed OC yet, you can do so now.
1. Add a sync connection and run it.

The remote data will now be overwritten with the local copy in cases where there are conflicts.

### Additional support for Tilburg University employees

If you need support using SRC or if you're looking for a suitable solution for your research, the Digital Research Support (DRS) Team at LIS can assist you. The team can be reached via the following email address: [digitalresearchsupport@tilburguniversity.edu](mailto: digitialresearchsupport@tilburguniversity.edu). Or contact the DRS team through the Self-Service Portal of TiU.

{{% tip %}}

If DRS has created a CO for a research project earlier at your request, and you subsequently apply for a grant, you must clearly indicate in your grant application that it should be added to the already exisiting CO.

{{% /tip %}}
