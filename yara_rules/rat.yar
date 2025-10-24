rule RAT_NjRAT {
    meta:
        description = "NjRAT remote access trojan"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "njRAT" nocase
        $s2 = "Yasser" nocase
        $s3 = "|'|'|" wide ascii
        $s4 = "SEE_YOU" wide ascii
    condition:
        any of them
}

rule RAT_DarkComet {
    meta:
        description = "DarkComet RAT detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "DarkComet" nocase
        $s2 = "#KCMDDC" wide ascii
        $s3 = "DCLIB" wide ascii
    condition:
        any of them
}

rule RAT_AsyncRAT {
    meta:
        description = "AsyncRAT detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "AsyncRAT" nocase
        $s2 = "Pastebin" wide ascii
        $s3 = "pong" wide ascii
        $mutex = "AsyncMutex_" wide ascii
    condition:
        any of them
}

rule RAT_Remcos {
    meta:
        description = "Remcos RAT detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "Remcos" nocase
        $s2 = "Breaking-Security" nocase
        $s3 = "remcos_" nocase
    condition:
        any of them
}

rule RAT_Generic_Keylogger_Hooks {
    meta:
        description = "Generic keylogger hook detection"
        severity = "high"
        mitre = "T1056"
    strings:
        $hook1 = "SetWindowsHookEx" nocase
        $hook2 = "GetAsyncKeyState" nocase
        $hook3 = "GetKeyState" nocase
        $log = "keylog" nocase
    condition:
        2 of ($hook*) or ($hook1 and $log)
}

rule RAT_Remote_Desktop_Access {
    meta:
        description = "Remote desktop access capabilities"
        severity = "high"
        mitre = "T1021"
    strings:
        $api1 = "BitBlt" nocase
        $api2 = "GetDC" nocase
        $api3 = "CreateCompatibleBitmap" nocase
        $net = "send" nocase
    condition:
        all of ($api*) and $net
}

rule RAT_Process_Injection {
    meta:
        description = "Process injection techniques"
        severity = "high"
        mitre = "T1055"
    strings:
        $api1 = "VirtualAllocEx" nocase
        $api2 = "WriteProcessMemory" nocase
        $api3 = "CreateRemoteThread" nocase
    condition:
        all of them
}

rule RAT_Reverse_Shell {
    meta:
        description = "Reverse shell connection"
        severity = "critical"
        mitre = "T1071"
    strings:
        $net1 = "WSAStartup" nocase
        $net2 = "connect" nocase
        $cmd1 = "cmd.exe" nocase
        $cmd2 = "CreateProcess" nocase
    condition:
        all of ($net*) and any of ($cmd*)
}

rule RAT_Persistence_Registry {
    meta:
        description = "Registry persistence mechanism"
        severity = "high"
        mitre = "T1547"
    strings:
        $reg1 = "RegSetValueEx" nocase
        $reg2 = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" nocase
        $reg3 = "HKEY_CURRENT_USER" nocase
    condition:
        $reg1 and ($reg2 or $reg3)
}

rule RAT_Data_Exfiltration {
    meta:
        description = "Data exfiltration capabilities"
        severity = "high"
        mitre = "T1041"
    strings:
        $file1 = "FindFirstFile" nocase
        $file2 = "ReadFile" nocase
        $net1 = "InternetOpen" nocase
        $net2 = "HttpSendRequest" nocase
    condition:
        all of ($file*) and any of ($net*)
}
