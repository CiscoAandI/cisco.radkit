:orphan:

.. meta::
  :antsibull-docs: 2.16.3

.. _list_of_collection_env_vars:

Index of all Collection Environment Variables
=============================================

The following index documents all environment variables declared by plugins in collections.
Environment variables used by the ansible-core configuration are documented in :ref:`ansible_configuration_settings`.

.. envvar:: ANSIBLE_INVENTORY_USE_EXTRA_VARS

    Merge extra vars into the available variables for composition (highest precedence).

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_CLIENT_CA_PATH

    The path to the issuer chain for the identity certificate

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_CLIENT_CERT_PATH

    The path to the identity certificate

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_CLIENT_KEY_PATH

    The path to the private key for the identity certificate

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_CLIENT_PRIVATE_KEY_PASSWORD_BASE64

    The private key password in base64 for radkit client

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_DEVICE_FILTER_ATTR

    Filter RADKit inventory by this attribute (ex name)

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_DEVICE_FILTER_PATTERN

    Filter RADKit inventory by this pattern combined with filter\_attr

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_IDENTITY

    The Client ID (owner email address) present in the RADKit client certificate.

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
.. envvar:: RADKIT_ANSIBLE_SERVICE_SERIAL

    The serial of the RADKit service you wish to connect through

    *Used by:*
    :ansplugin:`cisco.radkit.radkit inventory plugin <cisco.radkit.radkit#inventory>`
