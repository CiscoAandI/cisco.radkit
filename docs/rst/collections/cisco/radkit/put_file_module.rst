.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.put_file_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.put_file module -- Uploads a file to a remote device using SCP or SFTP via RADKit
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 2.0.0).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.put_file_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.put_file`.

.. version_added

.. rst-class:: ansible-version-added

New in cisco.radkit 1.7.5

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- Uploads a file to a remote device using SCP or SFTP via RADKit


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.put_file_module_requirements:

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

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-client_ca_path:

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

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-client_cert_path:

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

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-client_key_password_b64:
      .. _ansible_collections.cisco.radkit.put_file_module__parameter-radkit_client_private_key_password_base64:

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

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-client_key_path:

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
        <div class="ansibleOptionAnchor" id="parameter-device_host"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-device_host:

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

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-device_name:

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
        <div class="ansibleOptionAnchor" id="parameter-identity"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_identity"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-identity:
      .. _ansible_collections.cisco.radkit.put_file_module__parameter-radkit_identity:

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
        <div class="ansibleOptionAnchor" id="parameter-local_path"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-local_path:

      .. rst-class:: ansible-option-title

      **local_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-local_path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Path to the local file to be uploaded


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-protocol"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-protocol:

      .. rst-class:: ansible-option-title

      **protocol**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-protocol" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Protocol to use for uploading, either scp or sftp


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-remote_path"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-remote_path:

      .. rst-class:: ansible-option-title

      **remote_path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-remote_path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Path on the remote device where the file will be uploaded


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-service_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_service_serial"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__parameter-radkit_serial:
      .. _ansible_collections.cisco.radkit.put_file_module__parameter-radkit_service_serial:
      .. _ansible_collections.cisco.radkit.put_file_module__parameter-service_serial:

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

    - name: Upload file to device using SCP
      put_file:
        device_name: router1
        local_path: /path/to/local/file
        remote_path: /path/to/remote/file
        protocol: scp

    - name: Upload file to device using SFTP
      put_file:
        device_name: router1
        local_path: /path/to/local/file
        remote_path: /path/to/remote/file
        protocol: sftp



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
        <div class="ansibleOptionAnchor" id="return-message"></div>

      .. _ansible_collections.cisco.radkit.put_file_module__return-message:

      .. rst-class:: ansible-option-title

      **message**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-message" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Status message


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always


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
