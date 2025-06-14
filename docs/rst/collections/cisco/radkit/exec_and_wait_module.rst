.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.exec_and_wait_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.exec_and_wait module -- Executes commands on devices using RADKit and handles interactive prompts
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 2.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.exec_and_wait_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.exec_and_wait`.

.. version_added

.. rst-class:: ansible-version-added

New in cisco.radkit 1.7.61

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- This module runs commands on specified devices using RADKit, handling interactive prompts with pexpect.
- Enhanced with retry logic, progress monitoring, and better error handling.


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.exec_and_wait_module_requirements:

Requirements
------------
The below requirements are needed on the host that executes this module.

- radkit
- pexpect






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
        <div class="ansibleOptionAnchor" id="parameter-answers"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-answers:

      .. rst-class:: ansible-option-title

      **answers**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-answers" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of answers corresponding to the expected prompts.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-client_ca_path"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-client_ca_path:

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

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-client_cert_path:

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

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-client_key_password_b64:
      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-radkit_client_private_key_password_base64:

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

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-client_key_path:

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
        <div class="ansibleOptionAnchor" id="parameter-command_retries"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-command_retries:

      .. rst-class:: ansible-option-title

      **command_retries**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-command_retries" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Maximum number of retries for command execution failures.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`1`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-command_timeout"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-command_timeout:

      .. rst-class:: ansible-option-title

      **command_timeout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-command_timeout" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Time in seconds to wait for a command to complete.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`15`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-commands"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-commands:

      .. rst-class:: ansible-option-title

      **commands**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-commands" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of commands to execute on the device.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-continue_on_device_failure"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-continue_on_device_failure:

      .. rst-class:: ansible-option-title

      **continue_on_device_failure**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-continue_on_device_failure" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Continue processing other devices if one device fails.


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-delay_before_check"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-delay_before_check:

      .. rst-class:: ansible-option-title

      **delay_before_check**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-delay_before_check" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Delay in seconds before performing a final check on the device state.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`10`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-device_host"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-device_host:

      .. rst-class:: ansible-option-title

      **device_host**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-device_host" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Hostname or IP address of the device as it appears in the RADKit inventory. Use either device\_name or device\_host.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-device_name"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-device_name:

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

      Name of the device as it appears in the RADKit inventory. Use either device\_name or device\_host.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-identity"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_identity"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-identity:
      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-radkit_identity:

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
        <div class="ansibleOptionAnchor" id="parameter-prompts"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-prompts:

      .. rst-class:: ansible-option-title

      **prompts**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-prompts" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      List of expected prompts to handle interactively.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-recovery_test_command"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-recovery_test_command:

      .. rst-class:: ansible-option-title

      **recovery_test_command**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-recovery_test_command" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Custom command to test device responsiveness during recovery.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"show clock"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-seconds_to_wait"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-seconds_to_wait:

      .. rst-class:: ansible-option-title

      **seconds_to_wait**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-seconds_to_wait" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Maximum time in seconds to wait after sending the commands before checking the device state.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-service_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_service_serial"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-radkit_serial:
      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-radkit_service_serial:
      .. _ansible_collections.cisco.radkit.exec_and_wait_module__parameter-service_serial:

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


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

        - name: Test network connectivity (execution test, not success test)
          cisco.radkit.exec_and_wait:
            device_name: "{{ inventory_hostname }}"
            commands:
              - "ping 8.8.8.8 repeat 2"
            prompts: []
            answers: []
            seconds_to_wait: 60
            delay_before_check: 5
          register: ping_test
          # Note: This tests command execution, ping may fail due to network policies

        - name: Execute show commands safely
          cisco.radkit.exec_and_wait:
            device_name: "{{ inventory_hostname }}"
            commands:
              - "show version"
              - "show clock"
              - "show ip interface brief"
            prompts: []
            answers: []
            seconds_to_wait: 30
            delay_before_check: 2
            command_retries: 2
          register: show_commands

        - name: Reload Router and Wait Until Available by using ansible_host
          cisco.radkit.exec_and_wait:
            #device_name: "{{inventory_hostname}}"
            device_host: "{{ansible_host}}"
            commands:
              - "reload"
            prompts:
              - ".*yes/no].*"
              - ".*confirm].*"
            answers:
              - "yes
    "
              - "
    "
            seconds_to_wait: 300  # total time to wait for reload
            delay_before_check: 10  # Delay before checking terminal
            recovery_test_command: "show clock"
          register: reload_result

        - name: Reload Router and Wait Until Available by using inventory_hostname
          cisco.radkit.exec_and_wait:
            device_name: "{{inventory_hostname}}"
            commands:
              - "reload"
            prompts:
              - ".*yes/no].*"
              - ".*confirm].*"
            answers:
              - "yes
    "
              - "
    "
            seconds_to_wait: 300  # total time to wait for reload
            delay_before_check: 10  # Delay before checking terminal
            command_retries: 1
            continue_on_device_failure: false
          register: reload_result

        - name: Configuration change with confirmation
          cisco.radkit.exec_and_wait:
            device_name: "{{ inventory_hostname }}"
            commands:
              - "configure terminal"
              - "interface loopback 999"
              - "description Test interface"
              - "exit"
              - "exit"
            prompts: []
            answers: []
            seconds_to_wait: 30
            delay_before_check: 2
            recovery_test_command: "show running-config interface loopback 999"
          register: config_result

        - name: Reset the Connection
          # The connection must be reset to allow Ansible to poll the router for connectivity
          meta: reset_connection



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
        <div class="ansibleOptionAnchor" id="return-device_name"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-device_name:

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

      Device name (for single device compatibility)


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices:

      .. rst-class:: ansible-option-title

      **devices**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Results for each device processed


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices/attempt_count"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices/attempt_count:

      .. rst-class:: ansible-option-title

      **attempt_count**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices/attempt_count" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Number of recovery attempts


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices/device_name"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices/device_name:

      .. rst-class:: ansible-option-title

      **device_name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices/device_name" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Name of the device


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices/executed_commands"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices/executed_commands:

      .. rst-class:: ansible-option-title

      **executed_commands**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices/executed_commands" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      List of commands executed


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices/recovery_time"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices/recovery_time:

      .. rst-class:: ansible-option-title

      **recovery_time**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices/recovery_time" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`float`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Time taken for device recovery


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices/status"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices/status:

      .. rst-class:: ansible-option-title

      **status**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices/status" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Execution status (SUCCESS/FAILED)


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-devices/stdout"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-devices/stdout:

      .. rst-class:: ansible-option-title

      **stdout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-devices/stdout" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Command output


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>



  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-executed_commands"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-executed_commands:

      .. rst-class:: ansible-option-title

      **executed_commands**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-executed_commands" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Commands executed (for single device compatibility)


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-stdout"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-stdout:

      .. rst-class:: ansible-option-title

      **stdout**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-stdout" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Output of commands (for single device compatibility)


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-summary"></div>

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-summary:

      .. rst-class:: ansible-option-title

      **summary**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-summary" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Summary of execution across all devices


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-summary/failed_devices"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-summary/failed_devices:

      .. rst-class:: ansible-option-title

      **failed_devices**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-summary/failed_devices" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Number of devices that failed


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-summary/successful_devices"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-summary/successful_devices:

      .. rst-class:: ansible-option-title

      **successful_devices**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-summary/successful_devices" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Number of devices that succeeded


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-indent"></div><div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-summary/total_devices"></div>

      .. raw:: latex

        \hspace{0.02\textwidth}\begin{minipage}[t]{0.3\textwidth}

      .. _ansible_collections.cisco.radkit.exec_and_wait_module__return-summary/total_devices:

      .. rst-class:: ansible-option-title

      **total_devices**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-summary/total_devices" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

      .. raw:: latex

        \end{minipage}

    - .. raw:: html

        <div class="ansible-option-indent-desc"></div><div class="ansible-option-cell">

      Total number of devices processed


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
