.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.swagger_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.swagger module -- Interacts with Swagger/OpenAPI endpoints via RADKit
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 1.8.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.swagger_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.swagger`.

.. version_added

.. rst-class:: ansible-version-added

New in cisco.radkit 0.3.0

.. contents::
   :local:
   :depth: 1

.. Deprecated


Synopsis
--------

.. Description

- Provides comprehensive interaction with Swagger/OpenAPI endpoints through RADKit
- Supports all standard HTTP methods with automatic request/response handling
- Includes proper status code validation and JSON response processing
- Automatically updates Swagger paths before making requests
- Designed for network device API automation and integration


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.swagger_module_requirements:

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

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-client_ca_path:

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

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-client_cert_path:

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

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-client_key_password_b64:
      .. _ansible_collections.cisco.radkit.swagger_module__parameter-radkit_client_private_key_password_base64:

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

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-client_key_path:

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

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-device_name:

      .. rst-class:: ansible-option-title

      **device_name**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-device_name" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

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

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-identity:
      .. _ansible_collections.cisco.radkit.swagger_module__parameter-radkit_identity:

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
        <div class="ansibleOptionAnchor" id="parameter-json"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-json:

      .. rst-class:: ansible-option-title

      **json**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-json" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Request body to be encoded as json or None


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-method"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-method:

      .. rst-class:: ansible-option-title

      **method**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-method" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      HTTP method (get,post,put,patch,delete,options,head)


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-parameters"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-parameters:

      .. rst-class:: ansible-option-title

      **parameters**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-parameters" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      HTTP params


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-path"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-path:

      .. rst-class:: ansible-option-title

      **path**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-path" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      url path, starting with /


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-service_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_service_serial"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-radkit_serial:
      .. _ansible_collections.cisco.radkit.swagger_module__parameter-radkit_service_serial:
      .. _ansible_collections.cisco.radkit.swagger_module__parameter-service_serial:

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
        <div class="ansibleOptionAnchor" id="parameter-status_code"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__parameter-status_code:

      .. rst-class:: ansible-option-title

      **status_code**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-status_code" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`list` / :ansible-option-elements:`elements=integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      A list of valid, numeric, HTTP status codes that signifies success of the request.


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`[200]`

      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    - name:  Get alarms from vManage
      cisco.radkit.swagger:
        device_name: vmanage1
        path: /alarms
        method: get
        status_code: [200]
        register: swagger_output
      delegate_to: localhost

    - name:  Register a new NMS partner in vManage
      cisco.radkit.swagger:
        device_name: vmanage1
        path: /partner/{partnerType}
        parameters: '{"partnerType": "dnac"}'
        method: post
        status_code: [200]
        json: '{"name": "DNAC-test","partnerId": "dnac-test","description": "dnac-test"}'
      register: swagger_output
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
        <div class="ansibleOptionAnchor" id="return-data"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__return-data:

      .. rst-class:: ansible-option-title

      **data**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-data" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      response body content as string


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-json"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__return-json:

      .. rst-class:: ansible-option-title

      **json**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-json" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      response body content decoded as json


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-status_code"></div>

      .. _ansible_collections.cisco.radkit.swagger_module__return-status_code:

      .. rst-class:: ansible-option-title

      **status_code**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-status_code" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      status


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
