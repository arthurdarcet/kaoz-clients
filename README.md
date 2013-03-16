Kaoz-clients
============

Clients for Kaoz, a free IRC notifier.

Overview
--------
There are several scripts which interfaces with a Kaoz server (https://github.com/BinetReseau/Kaoz).
These scripts aims to be installed in folder `/usr/share/kaoz-clients`.
The subfolders contain configuration files for several hooks, but `pipes` and `style`.

Pipes and style
---------------
`pipes` provides several `ircpipe` programs to be used to send message to IRC and keeping this simple.
Advanced users may choose to personalize an `ircpipe` for its own needs, regarding the default settings (eg. default IRC channel, Kaoz host, SSL CA).

`irc-style.sh` defines convenient variables to format IRC messages with font style and colors.
`config.sh` should be modified to reflect the configuration of your kaoz server. It is used by all the ircpipe.* scripts.

Git
---
`git` folder contains a post-receive hook for Git repositories.
To use this hook, copy `hook-post-receive` file to the `hooks/post-receive` location of you Git repository and modify it according to your configuration.

Nagios
------
Nagios is a service monitoring tool.
`nagios` folder contains a script which format Nagios notifications messages.
To make Nagios use this script to publish notifications on IRC, put the content of the two `.cfg` files in your Nagios configuration.

NUT (Network UPS Tools)
-----------------------
UPS provides tools to monitor power devices.
`nut-ups` folder contains a script to format NUT notifications with IRC colors.

PAM (Pluggable Authentication Modules)
--------------------------------------
Linux provides an extensible authentication system.
`pam` folder PAM configuration files to be used to report on IRC each login/logout, being with SSH, local login or su/sudo.
Each Linux distribution has a different set of default configuration files for PAM, so you should not copy and paste the configuration files to your `/etc/pam.d/` directory.
You may instead edit by hand your files and add a `pam_exec.so` line with `notify-message` script.

Contact
-------

Kaoz is provided by "Binet Réseau", a student association from France's École polytechnique.
If you have inquiries, comments or suggestions, you may contact us at br@eleves.polytechnique.fr

<pre>
                 ________________
               _/ ______________ \_
             _/ _/              \_ \
            / _/   ____    ____   \ \
           / /    / __ \  / __ \   | |
          / /    / /_/ / / /_/ /   | |
          | |   / _, &lt;  / _, _/    | |
          | |  / /_/ / / / | |     | |
          | | /_____/ /_/  | |    / /
           \ \              \ \__/ /
            \ \_             \____/
             \_ \________________
               \________________/

</pre>
