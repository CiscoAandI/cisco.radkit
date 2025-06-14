.. meta::
  :antsibull-docs: 2.16.3


.. _plugins_in_cisco.radkit:

Cisco.Radkit
============

Collection version 2.0.0

.. contents::
   :local:
   :depth: 1

Description
-----------

Collection of plugins and modules for interacting with RADKit

**Author:**

* Scott Dozier <scdozier@cisco.com>

**Supported ansible-core versions:**

* 2.15.0 or newer

.. ansible-links::

  - title: "Issue Tracker"
    url: "https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible/issues"
    external: true
  - title: "Repository (Sources)"
    url: "https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible"
    external: true




.. toctree::
    :maxdepth: 1

Plugin Index
------------

These are the plugins in the cisco.radkit collection:


Modules
~~~~~~~

* :ansplugin:`command module <cisco.radkit.command#module>` -- Execute commands on network devices via Cisco RADKit
* :ansplugin:`controlapi_device module <cisco.radkit.controlapi_device#module>` --
* :ansplugin:`exec_and_wait module <cisco.radkit.exec_and_wait#module>` -- Executes commands on devices using RADKit and handles interactive prompts
* :ansplugin:`genie_diff module <cisco.radkit.genie_diff#module>` -- This module compares the results across multiple devices and outputs the differences.
* :ansplugin:`genie_learn module <cisco.radkit.genie_learn#module>` -- Runs a command via RADKit, then through genie parser, returning a parsed result
* :ansplugin:`genie_parsed_command module <cisco.radkit.genie_parsed_command#module>` -- Runs a command via RADKit, then through genie parser, returning a parsed result
* :ansplugin:`http module <cisco.radkit.http#module>` -- Execute HTTP/HTTPS requests on devices via Cisco RADKit
* :ansplugin:`http_proxy module <cisco.radkit.http_proxy#module>` -- Starts a local HTTP (and SOCKS) proxy through RADKIT for use with modules that can utilize a proxy
* :ansplugin:`port_forward module <cisco.radkit.port_forward#module>` -- Forwards a port on a device in RADKIT inventory to localhost port.
* :ansplugin:`put_file module <cisco.radkit.put_file#module>` -- Uploads a file to a remote device using SCP or SFTP via RADKit
* :ansplugin:`service_info module <cisco.radkit.service_info#module>` -- Retrieve RADKit service information and status
* :ansplugin:`snmp module <cisco.radkit.snmp#module>` -- Perform SNMP operations via RADKit
* :ansplugin:`ssh_proxy module <cisco.radkit.ssh_proxy#module>` --
* :ansplugin:`swagger module <cisco.radkit.swagger#module>` -- Interacts with Swagger/OpenAPI endpoints via RADKit

.. toctree::
    :maxdepth: 1
    :hidden:

    command_module
    controlapi_device_module
    exec_and_wait_module
    genie_diff_module
    genie_learn_module
    genie_parsed_command_module
    http_module
    http_proxy_module
    port_forward_module
    put_file_module
    service_info_module
    snmp_module
    ssh_proxy_module
    swagger_module


Connection Plugins
~~~~~~~~~~~~~~~~~~

* :ansplugin:`network_cli connection <cisco.radkit.network_cli#connection>` --
* :ansplugin:`radkit_context connection <cisco.radkit.radkit_context#connection>` -- RADKit connection context management (internal use)
* :ansplugin:`terminal connection <cisco.radkit.terminal#connection>` --

.. toctree::
    :maxdepth: 1
    :hidden:

    network_cli_connection
    radkit_context_connection
    terminal_connection


Inventory Plugins
~~~~~~~~~~~~~~~~~

* :ansplugin:`radkit inventory <cisco.radkit.radkit#inventory>` -- Ansible dynamic inventory plugin for RADKIT.

.. toctree::
    :maxdepth: 1
    :hidden:

    radkit_inventory



.. seealso::

    List of :ref:`collections <list_of_collections>` with docs hosted here.
