rule Ransomware_Generic_Encryption {
    meta:
        description = "Detects generic ransomware encryption behavior"
        severity = "critical"
        mitre = "T1486"
    strings:
        $crypt1 = "CryptEncrypt" nocase
        $crypt2 = "CryptDecrypt" nocase
        $crypt3 = "CryptAcquireContext" nocase
        $file1 = "CreateFile" nocase
        $file2 = "WriteFile" nocase
        $ext1 = ".encrypted"
        $ext2 = ".locked"
        $ext3 = ".crypto"
    condition:
        2 of ($crypt*) and 2 of ($file*) or any of ($ext*)
}

rule Ransomware_WannaCry {
    meta:
        description = "WannaCry ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "WNcry@2ol7" wide ascii
        $s2 = "WANACRY!" wide ascii
        $s3 = "tasksche.exe" nocase
        $s4 = "msg/m_bulgarian.wnry"
    condition:
        any of them
}

rule Ransomware_Locky {
    meta:
        description = "Locky ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "_Locky_recover_instructions.txt"
        $s2 = ".locky" nocase
        $s3 = "HELP_YOUR_FILES"
    condition:
        any of them
}

rule Ransomware_Cerber {
    meta:
        description = "Cerber ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = ".cerber" nocase
        $s2 = "# CERBER RANSOMWARE"
        $s3 = "_R_E_A_D___T_H_I_S_"
    condition:
        any of them
}

rule Ransomware_File_Extension_Change {
    meta:
        description = "Detects mass file extension changes"
        severity = "high"
        mitre = "T1486"
    strings:
        $api1 = "MoveFileEx" nocase
        $api2 = "SetFileAttributes" nocase
        $loop = { 8B ?? ?? ?? ?? ?? 83 ?? ?? 7? ?? }
    condition:
        all of ($api*) and $loop
}

rule Ransomware_Ransom_Note {
    meta:
        description = "Detects ransom note creation"
        severity = "critical"
        mitre = "T1486"
    strings:
        $note1 = "YOUR FILES ARE ENCRYPTED" nocase
        $note2 = "PAY BITCOIN" nocase
        $note3 = "DECRYPT YOUR FILES" nocase
        $note4 = "RANSOM" nocase
        $bitcoin = /[13][a-km-zA-HJ-NP-Z1-9]{25,34}/
    condition:
        2 of ($note*) or $bitcoin
}

rule Ransomware_Shadow_Copy_Delete {
    meta:
        description = "Detects shadow copy deletion (ransomware behavior)"
        severity = "high"
        mitre = "T1490"
    strings:
        $cmd1 = "vssadmin delete shadows" nocase
        $cmd2 = "wmic shadowcopy delete" nocase
        $cmd3 = "bcdedit /set {default} recoveryenabled no" nocase
    condition:
        any of them
}

rule Ransomware_Crypto_API_Usage {
    meta:
        description = "Heavy crypto API usage (encryption)"
        severity = "medium"
        mitre = "T1486"
    strings:
        $api1 = "CryptGenKey"
        $api2 = "CryptEncrypt"
        $api3 = "CryptImportKey"
        $api4 = "CryptExportKey"
    condition:
        3 of them
}

rule Ransomware_Mass_File_Modification {
    meta:
        description = "Detects rapid file modification patterns"
        severity = "high"
        mitre = "T1486"
    strings:
        $find1 = "FindFirstFile" nocase
        $find2 = "FindNextFile" nocase
        $write = "WriteFile" nocase
        $close = "CloseHandle" nocase
    condition:
        all of them
}

rule Ransomware_Network_Encryption_Key {
    meta:
        description = "Detects network communication for encryption keys"
        severity = "high"
        mitre = "T1071"
    strings:
        $net1 = "InternetOpen" nocase
        $net2 = "HttpSendRequest" nocase
        $crypt = "CryptEncrypt" nocase
        $key = "encryption_key" nocase
    condition:
        2 of ($net*) and ($crypt or $key)
}

rule Ransomware_Ryuk {
    meta:
        description = "Ryuk ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "UNIQUE_ID_DO_NOT_REMOVE" wide ascii
        $s2 = "RyukReadMe.txt" nocase
        $s3 = "Ryuk" nocase
    condition:
        any of them
}

rule Ransomware_Maze {
    meta:
        description = "Maze ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "DECRYPT-FILES.txt" nocase
        $s2 = "maze" nocase
        $s3 = "Your files are encrypted" nocase
    condition:
        2 of them
}

rule Ransomware_Conti {
    meta:
        description = "Conti ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "CONTI" nocase
        $s2 = "R3ADM3.txt" nocase
        $s3 = ".CONTI" nocase
    condition:
        any of them
}

rule Ransomware_Backup_Deletion {
    meta:
        description = "Backup deletion behavior"
        severity = "high"
        mitre = "T1490"
    strings:
        $cmd1 = "wbadmin delete catalog" nocase
        $cmd2 = "wbadmin delete backup" nocase
        $cmd3 = "vssadmin resize shadowstorage" nocase
    condition:
        any of them
}

rule Ransomware_LockBit {
    meta:
        description = "LockBit ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "LockBit" nocase
        $s2 = "Restore-My-Files.txt" nocase
        $s3 = ".lockbit" nocase
    condition:
        any of them
}

rule Ransomware_BlackCat {
    meta:
        description = "BlackCat/ALPHV ransomware detection"
        severity = "critical"
        mitre = "T1486"
    strings:
        $s1 = "BlackCat" nocase
        $s2 = "ALPHV" nocase
        $s3 = "RECOVER-" nocase
    condition:
        any of them
}
