rule Keylogger_Generic {
    meta:
        description = "Generic keylogger detection"
        severity = "high"
        mitre = "T1056.001"
    strings:
        $api1 = "GetAsyncKeyState" nocase
        $api2 = "GetKeyboardState" nocase
        $api3 = "SetWindowsHookEx" nocase
        $log = "keylog" nocase
    condition:
        2 of ($api*) or ($api1 and $log)
}

rule Keylogger_Hook_Based {
    meta:
        description = "Hook-based keylogger"
        severity = "high"
        mitre = "T1056.001"
    strings:
        $hook = "SetWindowsHookEx" nocase
        $wh_keyboard = { 0D 00 00 00 }
        $callback = "CallNextHookEx" nocase
    condition:
        $hook and ($wh_keyboard or $callback)
}

rule Keylogger_Clipboard_Monitor {
    meta:
        description = "Clipboard monitoring"
        severity = "medium"
        mitre = "T1115"
    strings:
        $api1 = "GetClipboardData" nocase
        $api2 = "OpenClipboard" nocase
        $api3 = "SetClipboardViewer" nocase
    condition:
        2 of them
}

rule Keylogger_Screenshot_Capture {
    meta:
        description = "Screenshot capture capability"
        severity = "medium"
        mitre = "T1113"
    strings:
        $api1 = "BitBlt" nocase
        $api2 = "GetDC" nocase
        $api3 = "CreateCompatibleBitmap" nocase
        $save = "SaveBitmap" nocase
    condition:
        all of ($api*) or ($api1 and $save)
}

rule Keylogger_File_Logging {
    meta:
        description = "Keylogger with file logging"
        severity = "high"
        mitre = "T1056.001"
    strings:
        $key = "GetAsyncKeyState" nocase
        $file1 = "CreateFile" nocase
        $file2 = "WriteFile" nocase
        $log = /keylog|keys\.txt|log\.txt/i
    condition:
        $key and (all of ($file*) or $log)
}

rule Keylogger_Network_Exfil {
    meta:
        description = "Keylogger with network exfiltration"
        severity = "critical"
        mitre = "T1041"
    strings:
        $key = "GetAsyncKeyState" nocase
        $net1 = "InternetOpen" nocase
        $net2 = "HttpSendRequest" nocase
        $net3 = "send" nocase
    condition:
        $key and any of ($net*)
}

rule Keylogger_Hidden_Window {
    meta:
        description = "Hidden window keylogger"
        severity = "high"
        mitre = "T1564.003"
    strings:
        $hide1 = "ShowWindow" nocase
        $hide2 = "SW_HIDE" nocase
        $key = "GetAsyncKeyState" nocase
    condition:
        all of them
}

rule Keylogger_Stealth_Techniques {
    meta:
        description = "Keylogger with stealth techniques"
        severity = "high"
        mitre = "T1027"
    strings:
        $key = "GetAsyncKeyState" nocase
        $stealth1 = "IsDebuggerPresent" nocase
        $stealth2 = "VirtualProtect" nocase
        $stealth3 = "GetModuleHandle" nocase
    condition:
        $key and 2 of ($stealth*)
}
