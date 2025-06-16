.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.radkit_context_connection:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.radkit_context connection -- RADKit connection context management (internal use)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This connection plugin is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 2.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this connection plugin,
    see :ref:`Requirements <ansible_collections.cisco.radkit.radkit_context_connection_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.radkit_context`.

.. version_added

.. rst-class:: ansible-version-added

New in cisco.radkit 2.0.0

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- Internal utility for managing RADKit client connections and contexts
- Not intended for direct use by end users
- Provides connection pooling and context management for RADKit plugins


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.radkit_context_connection_requirements:

Requirements
------------
The below requirements are needed on the local controller node that executes this connection.

- radkit-client






.. Options


.. Attributes


.. Notes

Notes
-----

.. note::
   - This is an internal utility plugin and should not be used directly
   - Used by other RADKit connection plugins for connection management

.. Seealso


.. Examples



.. Facts


.. Return values


..  Status (Presently only deprecated)


.. Authors

Authors
~~~~~~~

- Scott Dozier (@scdozier)


.. hint::
    Configuration entries for each entry type have a low to high priority order. For example, a variable that is lower in the list will override a variable that is higher up.

.. Extra links

Collection links
~~~~~~~~~~~~~~~~

.. ansible-links::

  - title: "Issue Tracker"
    url: "https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible/issues"
    external: true
  - title: "Repository (Sources)"
    url: "https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible"
    external: true


.. Parsing errors
