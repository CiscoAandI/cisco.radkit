.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.genie_diff_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.genie_diff module -- This module compares the results across multiple devices and outputs the differences.
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 1.8.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.genie_diff_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.genie_diff`.

.. version_added

.. rst-class:: ansible-version-added

New in cisco.radkit 0.2.0

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- This module compares the results across multiple devices and outputs the differences between the parsed command output or the learned model output.
- If diff\_snapshots is used, compares differences in results from the same device.


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.genie_diff_module_requirements:

Requirements
------------
The below requirements are needed on the host that executes this module.

- radkit






.. Options

Parameters
----------

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Parameter
    - Comments

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-diff_snapshots"></div>

      .. _ansible_collections.cisco.radkit.genie_diff_module__parameter-diff_snapshots:

      .. rst-class:: ansible-option-title

      **diff_snapshots**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-diff_snapshots" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Set to true if comparing output from the same device.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-result_a"></div>

      .. _ansible_collections.cisco.radkit.genie_diff_module__parameter-result_a:

      .. rst-class:: ansible-option-title

      **result_a**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-result_a" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Result A from previous genie\_parsed\_command


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-result_b"></div>

      .. _ansible_collections.cisco.radkit.genie_diff_module__parameter-result_b:

      .. rst-class:: ansible-option-title

      **result_b**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-result_b" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Result B from previous genie\_parsed\_command


      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name:  Get show version parsed (initial snapshot)
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr1
        os: iosxe
      register: cmd_output
      delegate_to: localhost

    - name:  Get show version parsed (2nd snapshot)
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr1
        os: iosxe
      register: cmd_output2
      delegate_to: localhost

    - name:  Get a diff from snapshots daa-csr1
      cisco.radkit.genie_diff:
        result_a: "{{ cmd_output }}"
        result_b: "{{ cmd_output2 }}"
        diff_snapshots: yes
      delegate_to: localhost

    - name:  Get show version parsed from routerA
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr1
        os: iosxe
      register: cmd_output
      delegate_to: localhost

    - name: Get show version parsed from routerB
      cisco.radkit.genie_parsed_command:
        commands: show version
        device_name: daa-csr2
        os: iosxe
      register: cmd_output2
      delegate_to: localhost

    - name:  Get a diff from snapshots of routerA and routerB
      cisco.radkit.genie_diff:
        result_a: "{{ cmd_output }}"
        result_b: "{{ cmd_output2 }}"
        diff_snapshots: no
      delegate_to: localhost



.. Facts


.. Return values

Return Values
-------------
Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this module:

.. tabularcolumns:: \X{1}{3}\X{2}{3}

.. list-table::
  :width: 100%
  :widths: auto
  :header-rows: 1
  :class: longtable ansible-option-table

  * - Key
    - Description

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-genie_diff_result"></div>

      .. _ansible_collections.cisco.radkit.genie_diff_module__return-genie_diff_result:

      .. rst-class:: ansible-option-title

      **genie_diff_result**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-genie_diff_result" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Result from Genie Diff


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-genie_diff_result_lines"></div>

      .. _ansible_collections.cisco.radkit.genie_diff_module__return-genie_diff_result_lines:

      .. rst-class:: ansible-option-title

      **genie_diff_result_lines**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-genie_diff_result_lines" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Result from Genie Diff split into a list


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>



..  Status (Presently only deprecated)


.. Authors

Authors
~~~~~~~

- Scott Dozier (@scdozier)



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
