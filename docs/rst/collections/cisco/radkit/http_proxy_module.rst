.. Document meta

:orphan:

.. |antsibull-internal-nbsp| unicode:: 0xA0
    :trim:

.. meta::
  :antsibull-docs: 2.16.3

.. Anchors

.. _ansible_collections.cisco.radkit.http_proxy_module:

.. Anchors: short name for ansible.builtin

.. Title

cisco.radkit.http_proxy module -- Starts a local HTTP (and SOCKS) proxy through RADKIT for use with modules that can utilize a proxy
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. Collection note

.. note::
    This module is part of the `cisco.radkit collection <https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible>`_ (version 1.8.1).

    It is not included in ``ansible-core``.
    To check whether it is installed, run :code:`ansible-galaxy collection list`.

    To install it, use: :code:`ansible-galaxy collection install git+https://wwwin-github.cisco.com/scdozier/cisco.radkit-ansible.git`.
    You need further requirements to be able to use this module,
    see :ref:`Requirements <ansible_collections.cisco.radkit.http_proxy_module_requirements>` for details.

    To use it in a playbook, specify: :code:`cisco.radkit.http_proxy`.

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

- This modules starts a local HTTP (and SOCKS) proxy through RADKIT for use with modules that can utilize a proxy.
- RADKIT can natively create a SOCKS proxy, but most Ansible modules only support HTTP proxy if at all, so this module starts both.
- Note that the proxy will ONLY forward connections to devices that have a forwarded port in RADKIT AND to hosts in format of \<hostname\>.\<serial\>.proxy.


.. Aliases


.. Requirements

.. _ansible_collections.cisco.radkit.http_proxy_module_requirements:

Requirements
------------
The below requirements are needed on the host that executes this module.

- radkit
- python-proxy






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

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-client_ca_path:

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

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-client_cert_path:

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

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-client_key_password_b64:
      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-radkit_client_private_key_password_base64:

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

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-client_key_path:

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
        <div class="ansibleOptionAnchor" id="parameter-http_proxy_port"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-http_proxy_port:

      .. rst-class:: ansible-option-title

      **http_proxy_port**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-http_proxy_port" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      HTTP proxy port opened by module


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"4001"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-identity"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_identity"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-identity:
      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-radkit_identity:

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
        <div class="ansibleOptionAnchor" id="parameter-proxy_password"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-proxy_password:

      .. rst-class:: ansible-option-title

      **proxy_password**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-proxy_password" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Password for use with both http and socks proxy

      If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_PROXY\_PASSWORD will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-proxy_username"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-proxy_username:

      .. rst-class:: ansible-option-title

      **proxy_username**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-proxy_username" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string` / :ansible-option-required:`required`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Username for use with both http and socks proxy.

      If the value is not specified in the task, the value of environment variable RADKIT\_ANSIBLE\_PROXY\_USERNAME will be used instead.


      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-service_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_serial"></div>
        <div class="ansibleOptionAnchor" id="parameter-radkit_service_serial"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-radkit_serial:
      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-radkit_service_serial:
      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-service_serial:

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
        <div class="ansibleOptionAnchor" id="parameter-socks_proxy_port"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-socks_proxy_port:

      .. rst-class:: ansible-option-title

      **socks_proxy_port**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-socks_proxy_port" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`string`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      SOCKS proxy port opened by RADKIT client


      .. rst-class:: ansible-option-line

      :ansible-option-default-bold:`Default:` :ansible-option-default:`"4000"`

      .. raw:: html

        </div>

  * - .. raw:: html

        <div class="ansible-option-cell">
        <div class="ansibleOptionAnchor" id="parameter-test"></div>

      .. _ansible_collections.cisco.radkit.http_proxy_module__parameter-test:

      .. rst-class:: ansible-option-title

      **test**

      .. raw:: html

        <a class="ansibleOptionLink" href="#parameter-test" title="Permalink to this option"></a>

      .. ansible-option-type-line::

        :ansible-option-type:`boolean`

      .. raw:: html

        </div>

    - .. raw:: html

        <div class="ansible-option-cell">

      Tests your proxy configuration before trying to run in async


      .. rst-class:: ansible-option-line

      :ansible-option-choices:`Choices:`

      - :ansible-option-choices-entry-default:`false` :ansible-option-choices-default-mark:`← (default)`
      - :ansible-option-choices-entry:`true`


      .. raw:: html

        </div>


.. Attributes


.. Notes


.. Seealso


.. Examples

Examples
--------

.. code-block:: yaml+jinja

    # The idea of this module is to start the module once and run on localhost for duration of the play.
    # Any other module running on the localhost can utilize it to connect to devices over HTTPS.
    #
    # Note that connecting through the proxy in radkit is of format <device name>.<serial>.proxy
    ---
    - hosts: all
      gather_facts: no
      vars:
        radkit_service_serial: xxxx-xxxx-xxxx
        http_proxy_username: radkit
        http_proxy_password: Radkit999
        http_proxy_port: 4001
        socks_proxy_port: 4000
      environment:
        http_proxy: "http://{{ http_proxy_username }}:{{ http_proxy_password }}@127.0.0.1:{{ http_proxy_port }}"
        https_proxy: "http://{{ http_proxy_username }}:{{ http_proxy_password }}@127.0.0.1:{{ http_proxy_port }}"
      pre_tasks:

        - name: Test HTTP Proxy RADKIT To Find Potential Config Errors (optional)
          cisco.radkit.http_proxy:
            http_proxy_port: "{{ http_proxy_port }}"
            socks_proxy_port: "{{ socks_proxy_port }}"
            proxy_username: "{{ http_proxy_username }}"
            proxy_password: "{{ http_proxy_password }}"
            test: True
          delegate_to: localhost
          run_once: true

        - name: Start HTTP Proxy Through RADKIT And Leave Running for 300 Seconds (adjust time based on playbook exec time)
          cisco.radkit.http_proxy:
            http_proxy_port: "{{ http_proxy_port }}"
            socks_proxy_port: "{{ socks_proxy_port }}"
            proxy_username: "{{ http_proxy_username }}"
            proxy_password: "{{ http_proxy_password }}"
          async: 300
          poll: 0
          delegate_to: localhost
          run_once: true

        - name: Wait for http proxy port to become open (it takes a little bit for proxy to start)
          ansible.builtin.wait_for:
            port: "{{ http_proxy_port }}"
            delay: 1
          delegate_to: localhost
          run_once: true

      tasks:

        - name: Example ACI Task that goes through http proxy
          cisco.aci.aci_system:
            hostname:  "{{ inventory_hostname }}.{{ radkit_service_serial }}.proxy"
            username: admin
            password: "password"
            state: query
            use_proxy: yes
            validate_certs: no
          delegate_to: localhost
          failed_when: False



.. Facts


.. Return values


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
