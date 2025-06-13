.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.http_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.http module -- Execute HTTP/HTTPS requests on devices via Cisco RADKit
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 1.8.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.http_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.http`.

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

- Executes HTTP and HTTPS requests on devices or services managed by Cisco RADKit
- Supports all standard HTTP methods with comprehensive request configuration
- Provides structured response data including status, headers, and content
- Handles authentication, cookies, and custom headers professionally


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.http_module_requirements:

Requirements
------------
The below requirements are needed on the host that executes this module.

- cisco-radkit-client






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

      .. _ansible_collections.cisco.radkit.http_module__parameter-client_ca_path:

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

      .. _ansible_collections.cisco.radkit.http_module__parameter-client_cert_path:

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

      .. _ansible_collections.cisco.radkit.http_module__parameter-client_key_password_b64:
      .. _ansible_collections.cisco.radkit.http_module__parameter-radkit_client_private_key_password_base64:

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

      .. _ansible_collections.cisco.radkit.http_module__parameter-client_key_path:

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
        <div class="ansibleOptionAnchor" id="parameter-content"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-content:

      .. rst-class:: ansible-option-title

      **content**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-content" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Raw request body content as string

      Mutually exclusive with 'json' parameter


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-cookies"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-cookies:

      .. rst-class:: ansible-option-title

      **cookies**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-cookies" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Cookie values to include in the request

      Provided as a dictionary of cookie names and values


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-device_name"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-device_name:

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

      Name of the device or service as it appears in RADKit inventory

      Must be a valid device accessible through RADKit


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-headers"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-headers:

      .. rst-class:: ansible-option-title

      **headers**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-headers" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Custom HTTP headers to include in the request

      Common headers include 'Content-Type', 'Authorization', etc.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-identity"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_identity"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-identity:
      .. _ansible_collections.cisco.radkit.http_module__parameter-radkit_identity:

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

      .. _ansible_collections.cisco.radkit.http_module__parameter-json:

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

      Request body to be JSON-encoded and sent with appropriate Content-Type

      Mutually exclusive with 'content' parameter


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-method"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-method:

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

      HTTP method to use for the request

      Supports all standard REST API methods


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry:`"GET"`
      - :ansible-option-choices-entry:`"POST"`
      - :ansible-option-choices-entry:`"PUT"`
      - :ansible-option-choices-entry:`"PATCH"`
      - :ansible-option-choices-entry:`"DELETE"`
      - :ansible-option-choices-entry:`"OPTIONS"`
      - :ansible-option-choices-entry:`"HEAD"`
      - :ansible-option-choices-entry:`"get"`
      - :ansible-option-choices-entry:`"post"`
      - :ansible-option-choices-entry:`"put"`
      - :ansible-option-choices-entry:`"patch"`
      - :ansible-option-choices-entry:`"delete"`
      - :ansible-option-choices-entry:`"options"`
      - :ansible-option-choices-entry:`"head"`


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-params"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-params:

      .. rst-class:: ansible-option-title

      **params**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-params" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      URL parameters to append to the request

      Will be properly URL-encoded and appended to the path


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-path"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-path:

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

      URL path for the HTTP request, must start with '/'

      Can include query parameters or use the 'params' option separately


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-service_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_service_serial"></div>

      .. _ansible_collections.cisco.radkit.http_module__parameter-radkit_serial:
      .. _ansible_collections.cisco.radkit.http_module__parameter-radkit_service_serial:
      .. _ansible_collections.cisco.radkit.http_module__parameter-service_serial:

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

      .. _ansible_collections.cisco.radkit.http_module__parameter-status_code:

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

      List of valid HTTP status codes that indicate successful requests

      Request will be considered failed if response code is not in this list


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

    # Simple GET request
    - name: Execute HTTP GET request
      cisco.radkit.http:
        device_name: api-server-01
        path: /api/v1/status
        method: GET
      register: status_response
      delegate_to: localhost

    # POST request with JSON payload
    - name: Create new resource via POST
      cisco.radkit.http:
        device_name: api-server-01
        path: /api/v1/resources
        method: POST
        headers:
          Content-Type: application/json
          Authorization: Bearer {{ api_token }}
        json:
          name: "new-resource"
          type: "configuration"
          enabled: true
        status_code: [201, 202]
      register: create_response
      delegate_to: localhost

    # GET request with query parameters
    - name: Fetch filtered data
      cisco.radkit.http:
        device_name: monitoring-server
        path: /metrics
        method: GET
        params:
          start_time: "2024-01-01T00:00:00Z"
          end_time: "2024-01-02T00:00:00Z"
          format: json
        headers:
          Accept: application/json
      register: metrics_data
      delegate_to: localhost

    # PUT request with authentication cookies
    - name: Update configuration
      cisco.radkit.http:
        device_name: config-server
        path: /api/config/network
        method: PUT
        cookies:
          sessionid: "{{ login_session.cookies.sessionid }}"
          csrftoken: "{{ csrf_token }}"
        content: |
          interface GigabitEthernet0/1
           ip address 192.168.1.1 255.255.255.0
           no shutdown
        headers:
          Content-Type: text/plain
        status_code: [200, 204]
      register: config_update
      delegate_to: localhost

    # Display response data
    - name: Show HTTP response
      debug:
        msg: "Status: {{ status_response.status_code }}, Data: {{ status_response.json }}"

    # Handle different response types
    - name: Process API response
      debug:
        msg: "{{ create_response.json.id if create_response.json is defined else create_response.data }}"



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
        <div class="ansibleOptionAnchor" id="return-changed"></div>

      .. _ansible_collections.cisco.radkit.http_module__return-changed:

      .. rst-class:: ansible-option-title

      **changed**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-changed" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Whether any changes were made (depends on HTTP method used)


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`false`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-cookies"></div>

      .. _ansible_collections.cisco.radkit.http_module__return-cookies:

      .. rst-class:: ansible-option-title

      **cookies**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-cookies" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Response cookies as dictionary


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when cookies are present in response

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`{"sessionid": "abc123", "token": "xyz789"}`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-data"></div>

      .. _ansible_collections.cisco.radkit.http_module__return-data:

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

      Response body content as string


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` success

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`"{\\"result\\": \\"success\\", \\"message\\": \\"Operation completed\\"}"`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-headers"></div>

      .. _ansible_collections.cisco.radkit.http_module__return-headers:

      .. rst-class:: ansible-option-title

      **headers**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-headers" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`dictionary`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Response headers as dictionary


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`{"content-type": "application/json", "server": "nginx/1.18"}`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-json"></div>

      .. _ansible_collections.cisco.radkit.http_module__return-json:

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

      Response body content parsed as JSON (if valid JSON)


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` when response contains valid JSON

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`{"message": "Operation completed", "result": "success"}`


      .. raw:: html

        </div>


  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="return-status_code"></div>

      .. _ansible_collections.cisco.radkit.http_module__return-status_code:

      .. rst-class:: ansible-option-title

      **status_code**

      .. raw:: html

        <a class="ansibleOptionLink" href="#return-status_code" title="Permalink to this return value"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`integer`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      HTTP response status code


      .. rst-class:: ansible-option-line

      :ansible-option-returned-bold:`Returned:` always

      .. rst-class:: ansible-option-line
      .. rst-class:: ansible-option-sample

      :ansible-option-sample-bold:`Sample:` :ansible-rv-sample-value:`200`


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
