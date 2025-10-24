rule Cryptominer_XMRig {
    meta:
        description = "XMRig cryptocurrency miner"
        severity = "high"
        mitre = "T1496"
    strings:
        $s1 = "xmrig" nocase
        $s2 = "stratum+tcp" nocase
        $s3 = "donate-level" nocase
        $s4 = "randomx" nocase
    condition:
        2 of them
}

rule Cryptominer_Monero {
    meta:
        description = "Monero mining activity"
        severity = "high"
        mitre = "T1496"
    strings:
        $s1 = "monero" nocase
        $s2 = "cryptonight" nocase
        $s3 = "pool.minexmr" nocase
        $s4 = "xmr-stak" nocase
    condition:
        any of them
}

rule Cryptominer_High_CPU_Usage {
    meta:
        description = "Mining with high CPU usage"
        severity = "medium"
        mitre = "T1496"
    strings:
        $api1 = "SetThreadPriority" nocase
        $api2 = "GetSystemInfo" nocase
        $api3 = "CreateThread" nocase
        $mining = /mining|miner|hashrate/i
    condition:
        all of ($api*) and $mining
}

rule Cryptominer_Pool_Connection {
    meta:
        description = "Mining pool connection"
        severity = "high"
        mitre = "T1071"
    strings:
        $pool1 = "stratum+tcp://" nocase
        $pool2 = "pool." nocase
        $pool3 = "mining" nocase
        $port = /:3333|:4444|:5555|:7777|:8888/
    condition:
        ($pool1 or $pool2) and ($pool3 or $port)
}

rule Cryptominer_Coinhive {
    meta:
        description = "Coinhive browser miner"
        severity = "high"
        mitre = "T1496"
    strings:
        $s1 = "coinhive" nocase
        $s2 = "CoinHive.Anonymous" nocase
        $s3 = "authedmine" nocase
    condition:
        any of them
}

rule Cryptominer_Hidden_Process {
    meta:
        description = "Hidden mining process"
        severity = "high"
        mitre = "T1564.001"
    strings:
        $hide = "ShowWindow" nocase
        $mining = /mining|miner|xmrig/i
        $cpu = "GetSystemInfo" nocase
    condition:
        all of them
}

rule Cryptominer_Persistence {
    meta:
        description = "Miner persistence mechanism"
        severity = "high"
        mitre = "T1547"
    strings:
        $reg = "RegSetValueEx" nocase
        $run = "CurrentVersion\\Run" nocase
        $mining = /mining|miner|xmrig/i
    condition:
        all of them
}
