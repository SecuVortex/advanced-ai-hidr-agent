# Suspicious PowerShell Script for HIDR Demo
# Contains patterns HIDR will detect as threats

$windowstyle = "hidden"
$encodedcommand = "base64payload"
$url = "http://malicious.com/payload.exe"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("kernel32.dll")]
    public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
    [DllImport("kernel32.dll")]
    public static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out int lpNumberOfBytesWritten);
    [DllImport("kernel32.dll")]
    public static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
}
"@

$lsass = "lsass.exe"
$mimikatz = "sekurlsa::logonpasswords"
$regpath = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"

Write-Host "Demo script - HIDR will detect this"
Start-Sleep -Seconds 300
