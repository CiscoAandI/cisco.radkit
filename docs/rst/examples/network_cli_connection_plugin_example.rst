:orphan:


Network CLI Connection Plugin
==============================
Example ansible one liner
*********************************
You can use the ansible command combined with this plugin to execute a command against multiple devices.

.. code-block:: bash

    $ ansible daa-csr1:daa-csr2:daa-csr3 -i radkit_devices.yml -e "ansible_network_os=ios" -m cisco.ios.ios_command -a "commands='show ip bgp sum'"  --connection cisco.radkit.network_cli
    daa-csr3 | SUCCESS => {
        "changed": false,
        "stdout": [
            "BGP router identifier 1.3.3.3, local AS number 602\nBGP table version is 49, main routing table version 49\n8 network entries using 1984 bytes of memory\n17 path entries using 2312 bytes of memory\n5/4 BGP path/bestpath attribute entries using 1400 bytes of memory\n1 BGP AS-PATH entries using 24 bytes of memory\n0 BGP route-map cache entries using 0 bytes of memory\n0 BGP filter-list cache entries using 0 bytes of memory\nBGP using 5720 total bytes of memory\nBGP activity 29/21 prefixes, 114/97 paths, scan interval 60 secs\n\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n10.10.10.1      4          601    9756    9743       49    0    0 6d03h           4\n10.10.11.1      4          601    9761    9756       49    0    0 6d03h           4\n10.10.30.2      4          602  150548  150601       49    0    0 13w4d           6"
        ],
        "stdout_lines": [
            [
                "BGP router identifier 1.3.3.3, local AS number 602",
                "BGP table version is 49, main routing table version 49",
                "8 network entries using 1984 bytes of memory",
                "17 path entries using 2312 bytes of memory",
                "5/4 BGP path/bestpath attribute entries using 1400 bytes of memory",
                "1 BGP AS-PATH entries using 24 bytes of memory",
                "0 BGP route-map cache entries using 0 bytes of memory",
                "0 BGP filter-list cache entries using 0 bytes of memory",
                "BGP using 5720 total bytes of memory",
                "BGP activity 29/21 prefixes, 114/97 paths, scan interval 60 secs",
                "",
                "Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd",
                "10.10.10.1      4          601    9756    9743       49    0    0 6d03h           4",
                "10.10.11.1      4          601    9761    9756       49    0    0 6d03h           4",
                "10.10.30.2      4          602  150548  150601       49    0    0 13w4d           6"
            ]
        ]
    }
    daa-csr1 | SUCCESS => {
        "changed": false,
        "stdout": [
            "BGP router identifier 192.0.2.1, local AS number 601\nBGP table version is 9, main routing table version 9\n8 network entries using 1984 bytes of memory\n19 path entries using 2584 bytes of memory\n5/4 BGP path/bestpath attribute entries using 1400 bytes of memory\n1 BGP AS-PATH entries using 24 bytes of memory\n0 BGP route-map cache entries using 0 bytes of memory\n0 BGP filter-list cache entries using 0 bytes of memory\nBGP using 5992 total bytes of memory\nBGP activity 30/22 prefixes, 137/118 paths, scan interval 60 secs\n\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n10.10.10.2      4          602    9743    9756        9    0    0 6d03h           5\n10.10.11.2      4          602    9756    9761        9    0    0 6d03h           5\n14.3.68.62      4          601    1993    1999        9    0    0 1d06h           6\n192.0.2.10      4        64496       0       0        1    0    0 never    Idle\n192.0.2.15      4        64496       0       0        1    0    0 never    Idle\n203.0.113.5     4        64511       0       0        1    0    0 never    Idle"
        ],
        "stdout_lines": [
            [
                "BGP router identifier 192.0.2.1, local AS number 601",
                "BGP table version is 9, main routing table version 9",
                "8 network entries using 1984 bytes of memory",
                "19 path entries using 2584 bytes of memory",
                "5/4 BGP path/bestpath attribute entries using 1400 bytes of memory",
                "1 BGP AS-PATH entries using 24 bytes of memory",
                "0 BGP route-map cache entries using 0 bytes of memory",
                "0 BGP filter-list cache entries using 0 bytes of memory",
                "BGP using 5992 total bytes of memory",
                "BGP activity 30/22 prefixes, 137/118 paths, scan interval 60 secs",
                "",
                "Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd",
                "10.10.10.2      4          602    9743    9756        9    0    0 6d03h           5",
                "10.10.11.2      4          602    9756    9761        9    0    0 6d03h           5",
                "14.3.68.62      4          601    1993    1999        9    0    0 1d06h           6",
                "192.0.2.10      4        64496       0       0        1    0    0 never    Idle",
                "192.0.2.15      4        64496       0       0        1    0    0 never    Idle",
                "203.0.113.5     4        64511       0       0        1    0    0 never    Idle"
            ]
        ]
    }
    daa-csr2 | SUCCESS => {
        "changed": false,
        "stdout": [
            "BGP router identifier 1.2.2.2, local AS number 601\nBGP table version is 9, main routing table version 9\n8 network entries using 1984 bytes of memory\n15 path entries using 2040 bytes of memory\n5/4 BGP path/bestpath attribute entries using 1400 bytes of memory\n1 BGP AS-PATH entries using 24 bytes of memory\n0 BGP route-map cache entries using 0 bytes of memory\n0 BGP filter-list cache entries using 0 bytes of memory\nBGP using 5448 total bytes of memory\nBGP activity 8/0 prefixes, 15/0 paths, scan interval 60 secs\n\nNeighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n10.10.20.2      4          602    1990    1994        9    0    0 1d06h           5\n14.3.68.61      4          601    1999    1993        9    0    0 1d06h           7"
        ],
        "stdout_lines": [
            [
                "BGP router identifier 1.2.2.2, local AS number 601",
                "BGP table version is 9, main routing table version 9",
                "8 network entries using 1984 bytes of memory",
                "15 path entries using 2040 bytes of memory",
                "5/4 BGP path/bestpath attribute entries using 1400 bytes of memory",
                "1 BGP AS-PATH entries using 24 bytes of memory",
                "0 BGP route-map cache entries using 0 bytes of memory",
                "0 BGP filter-list cache entries using 0 bytes of memory",
                "BGP using 5448 total bytes of memory",
                "BGP activity 8/0 prefixes, 15/0 paths, scan interval 60 secs",
                "",
                "Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd",
                "10.10.20.2      4          602    1990    1994        9    0    0 1d06h           5",
                "14.3.68.61      4          601    1999    1993        9    0    0 1d06h           7"
            ]
        ]
    }



Example Playbook
*********************************
..  literalinclude:: ../../../playbooks/network_cli_connection_plugin_example.yml
    :language: yaml
