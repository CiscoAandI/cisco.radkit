.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.genie_learn_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.genie_learn module -- Runs a command via RADKit, then through genie parser, returning a parsed result
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 1.8.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.genie_learn_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.genie_learn`.

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

- Runs a command via RADKit, then through genie parser, returning a parsed result


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.genie_learn_module_requirements:

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
        <div class="ansibleOptionAnchor" id="parameter-client_ca_path"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-client_ca_path:

      .. rst-class:: ansible-option-title

      **client_ca_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-client_ca_path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Alternate path to client ca cert for RADKIT If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_CLIENT\_CA\_PATH will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-client_cert_path"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-client_cert_path:

      .. rst-class:: ansible-option-title

      **client_cert_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-client_cert_path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Alternate path to client cert for RADKIT If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_CLIENT\_CERT\_PATH will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-client_key_password_b64"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_client_private_key_password_base64"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-client_key_password_b64:
      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-radkit_client_private_key_password_base64:

      .. rst-class:: ansible-option-title

      **client_key_password_b64**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-client_key_password_b64" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-aliases:`aliases: radkit_client_private_key_password_base64`

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Client certificate password in base64 If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_CLIENT\_PRIVATE\_KEY\_PASSWORD\_BASE64 will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-client_key_path"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-client_key_path:

      .. rst-class:: ansible-option-title

      **client_key_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-client_key_path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Alternate path to client key for RADKIT If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_CLIENT\_KEY\_PATH will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-device_name"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-device_name:

      .. rst-class:: ansible-option-title

      **device_name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-device_name" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Name of device as it shows in RADKit inventory


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-exec_timeout"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-exec_timeout:

      .. rst-class:: ansible-option-title

      **exec_timeout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-exec_timeout" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Specifies how many seconds RADKit will for command to complete

      Can optionally set via environemnt variable RADKIT\_ANSIBLE\_EXEC\_TIMEOUT


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`0`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-filter_attr"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-filter_attr:

      .. rst-class:: ansible-option-title

      **filter_attr**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-filter_attr" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Attrbute to match RADKit inventory, which can select multiple devices at once. (use with filter\_pattern, ex 'name')


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-filter_pattern"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-filter_pattern:

      .. rst-class:: ansible-option-title

      **filter_pattern**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-filter_pattern" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Pattern to match RADKit inventory, which can select multiple devices at once. (use instead of device\_name)


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-identity"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_identity"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-identity:
      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-radkit_identity:

      .. rst-class:: ansible-option-title

      **identity**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-identity" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-aliases:`aliases: radkit_identity`

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Identity to authentiate with RADKit (xxxx@cisco.com). If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_IDENTITY will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-models"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-models:

      .. rst-class:: ansible-option-title

      **models**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-models" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      models to execute on device


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-os"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-os:

      .. rst-class:: ansible-option-title

      **os**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-os" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      The device OS (if omitted, the OS found by fingerprint)


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"fingerprint"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-remove_model_and_device_keys"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-remove_model_and_device_keys:

      .. rst-class:: ansible-option-title

      **remove_model_and_device_keys**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-remove_model_and_device_keys" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Removes the model and device keys from the returned value when running a single model against a single device.

      NOTE; This does not work with diff


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-service_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_service_serial"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-radkit_serial:
      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-radkit_service_serial:
      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-service_serial:

      .. rst-class:: ansible-option-title

      **service_serial**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-service_serial" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-aliases:`aliases: radkit_serial, radkit_service_serial`

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Radkit service serial If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_SERVICE\_SERIAL will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-wait_timeout"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__parameter-wait_timeout:

      .. rst-class:: ansible-option-title

      **wait_timeout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-wait_timeout" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Specifies how many seconds RADKit will wait before failing task.

      Note that the request is not affected, and it will still eventually complete (successfully or unsuccessfully)

      Can optionally set via environemnt variable RADKIT\_ANSIBLE\_WAIT\_TIMEOUT


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`0`

      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name: Get parsed output from rtr-csr1 with removed return keys
      cisco.radkit.genie_learn:
        device_name: rtr-csr1
        models: platform
        os: iosxe
        remove_model_and_device_keys: yes
      register: cmd_output
      delegate_to: localhost

    - name: Show Chassis Serial Number
      debug:
        msg: "{{ cmd_output['genie_learn_result']['chassis_sn'] }}"



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
        <div class="ansibleOptionAnchor" id="return-ansible_module_results"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__return-ansible_module_results:

      .. rst-class:: ansible-option-title

      **ansible_module_results**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-ansible_module_results" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Dictionary of results is returned if running command on multiple devices or with multiple models


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-command"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__return-command:

      .. rst-class:: ansible-option-title

      **command**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-command" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Command


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-device_name"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__return-device_name:

      .. rst-class:: ansible-option-title

      **device_name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-device_name" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Device in Radkit


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-exec_status"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__return-exec_status:

      .. rst-class:: ansible-option-title

      **exec_status**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-exec_status" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Status of exec from RADKit


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-exec_status_message"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__return-exec_status_message:

      .. rst-class:: ansible-option-title

      **exec_status_message**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-exec_status_message" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Status message from RADKit


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-genie_learn_result"></div>

      .. _ansible_collections.cisco.radkit.genie_learn_module__return-genie_learn_result:

      .. rst-class:: ansible-option-title

      **genie_learn_result**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-genie_learn_result" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Dictionary of parsed results


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
