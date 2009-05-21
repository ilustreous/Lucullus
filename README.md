Lucullus Project
================

Lucullus is a framework to manage and visualize scientific data in a browser.

The server is based on pylons (python) and uses cairo to render 2d image tiles in realtime. On client-side a custom JavaScript library based on jQuery allows easy navigation through huge amounts of data with a google-maps-like interface.

Plugins exist to manage, edit and visualize:
* Sequence alignments  (Fasta format)
* PHB trees used by ClustalW or PHYLIB (Newick format)

Installation and Setup
======================

Install ``lucullus`` using easy_install::

    easy_install lucullus

Make a config file as follows::

    paster make-config lucullus config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.
