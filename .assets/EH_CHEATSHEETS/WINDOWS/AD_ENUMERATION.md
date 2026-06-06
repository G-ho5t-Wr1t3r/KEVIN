# Active Directory Enumeration (NetExec)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `NetExec` (nxc), `smbclient`, `ldapsearch`, `BloodHound`, `RustHound` |
| **SO Target** | Windows (Active Directory) |
| **Quando effettuare** | Dopo aver identificato un Domain Controller (DC) |
| **Info Utili** | Mappatura utenti, gruppi, share e relazioni di dominio |

### Identificazione DC
Il DC espone solitamente la porta **53** (DNS), **88** (Kerberos), **389** (LDAP), **445** (SMB).

### NetExec (nxc) - Il coltellino svizzero
**Sintassi Base:**
```bash
nxc <PROTOCOL> <IP> -u "<USER>" -p "<PASSWORD>"
```
*Esempio:*
```bash
nxc smb 10.10.10.105 -u "jsmith" -p "Password123"
```

**Null Session:**
```bash
nxc <PROTOCOL> <IP> -u "" -p "" --shares
```
*Esempio:*
```bash
nxc smb 10.10.10.105 -u "" -p "" --shares
```

**Anonymous Access:**
```bash
nxc <PROTOCOL> <IP> -u "anonymous" -p "" --shares
```
*Esempio:*
```bash
nxc smb 10.10.10.105 -u "anonymous" -p "" --shares
```

**Enumerazione Utenti (LDAP):**
```bash
nxc ldap <IP> -u "<USER>" -p "<PASSWORD>" --users
```
*Esempio:*
```bash
nxc ldap 10.10.10.105 -u "anonymous" -p "" --users
```

**Spider Plus (Mappatura Share):**
```bash
nxc smb <IP> -u "<USER>" -p "<PASSWORD>" -M spider_plus
```

### SMBClient
Per navigare e scaricare file dalle cartelle condivise.
```bash
smbclient //<IP>/<SHARE_NAME> -U "<USER>"
```
*Esempio:*
```bash
smbclient //10.10.10.105/software$ -U "anonymous"
```
*(Comandi interni: `ls`, `get <FILE>`, `exit`)*

### Analisi dei Grafi (BloodHound/RustHound)
Mappa le relazioni e i path di attacco per la Privilege Escalation.

**RustHound (Collector):**
```bash
rusthound-ce -i <IP> --domain <DOMAIN> -u <USER> -p <PASSWORD> -z
```
*Esempio:*
```bash
rusthound-ce -i 10.10.10.105 --domain eh.local -u 'svc-db' -p 'L3gac1P4ss' -z
```

### URL Fondamentali
- [NetExec Wiki](https://www.netexec.wiki/)
- [Hacktricks LDAP](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-ldap.html)
- [BloodHound GitHub](https://github.com/SpecterOps/BloodHound)
- [RustHound-CE GitHub](https://github.com/g0h4n/RustHound-CE)
