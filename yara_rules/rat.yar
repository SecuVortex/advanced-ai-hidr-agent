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

rule RAT_QuasarRAT {
    meta:
        description = "QuasarRAT detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "Quasar" nocase
        $s2 = "Client.exe" nocase
        $s3 = "xRAT" nocase
    condition:
        any of them
}

rule RAT_NetWire {
    meta:
        description = "NetWire RAT detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "NetWire" nocase
        $s2 = "HostId" wide ascii
        $s3 = "[Keylogger]" wide ascii
    condition:
        any of them
}

rule RAT_Screen_Capture {
    meta:
        description = "Screen capture functionality"
        severity = "high"
        mitre = "T1113"
    strings:
        $api1 = "BitBlt" nocase
        $api2 = "GetDIBits" nocase
        $api3 = "CreateDIBSection" nocase
        $api4 = "GetDesktopWindow" nocase
    condition:
        3 of them
}

rule RAT_Webcam_Access {
    meta:
        description = "Webcam access capabilities"
        severity = "high"
        mitre = "T1125"
    strings:
        $api1 = "capCreateCaptureWindow" nocase
        $api2 = "capGetDriverDescription" nocase
        $api3 = "avicap32.dll" nocase
    condition:
        any of them
}

rule RAT_Audio_Recording {
    meta:
        description = "Audio recording capabilities"
        severity = "high"
        mitre = "T1123"
    strings:
        $api1 = "waveInOpen" nocase
        $api2 = "waveInStart" nocase
        $api3 = "waveInAddBuffer" nocase
    condition:
        2 of them
}

rule RAT_CobaltStrike {
    meta:
        description = "CobaltStrike beacon detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "beacon.dll" nocase
        $s2 = "cobaltstrike" nocase
        $s3 = "malleable" nocase
    condition:
        any of them
}

rule RAT_Meterpreter {
    meta:
        description = "Metasploit Meterpreter detection"
        severity = "critical"
        mitre = "T1219"
    strings:
        $s1 = "meterpreter" nocase
        $s2 = "ReflectiveLoader" nocase
        $s3 = "stdapi_" nocase
    condition:
        any of them
}
