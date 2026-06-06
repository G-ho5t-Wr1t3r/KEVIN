# Hash Cracking (John/Hashcat)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `john` (John the Ripper), `hashcat`, `ssh2john`, `ssh` |
| **SO Target** | Qualsiasi (Hash da Linux/Windows) |
| **Quando effettuare** | Dopo aver ottenuto hash da database, file di configurazione o shadow copy |
| **Info Utili** | Cracking offline di password utilizzando wordlist come RockYou |

### John the Ripper
Ottimo per cracking rapido e conversione di formati.

**Cracking Base:**
```bash
john <HASH_FILE> --wordlist=<PATH_TO_WORDLIST>
```
*Esempio:*
```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

**Visualizzare Password Trovate:**
```bash
john --show <HASH_FILE>
```
*Esempio:*
```bash
john --show hash.txt
```

### Hashcat
Più potente e veloce (GPU support), richiede la specifica del formato hash.

**Cracking Base:**
```bash
hashcat -m <MODE_NUMBER> <HASH_FILE> <PATH_TO_WORDLIST>
```
*Esempio (SHA-256):*
```bash
hashcat -m 1400 hash.txt /usr/share/wordlists/rockyou.txt
```

### Casi Specifici
**SSH Key Cracking:**
Se trovi una chiave `.key` protetta da passphrase.
1. Convertire in hash:
```bash
ssh2john <PRIVATE_KEY> > <KEY_HASH>
```
*Esempio:*
```bash
ssh2john id_rsa > id_rsa.hash
```
2. Crackare con John:
```bash
john --wordlist=/usr/share/wordlists/rockyou.txt <KEY_HASH>
```

**Mirth Connect Hash Format:**
Esempio di formato specifico `sha256:600000:salt:hex`.
```bash
hashcat -m 10900 <HASH_FILE> <PATH_TO_WORDLIST>
```

### Wordlist
La più comune è **RockYou.txt**.
- Scaricabile da: [RockYou.txt (GitHub)](https://github.com/dw0rsec/rockyou.txt)

### URL Fondamentali
- [Hashcat Example Hashes](https://hashcat.net/wiki/doku.php?id=example_hashes)
- [John the Ripper Wiki](https://github.com/openwall/john/wiki)
- [RockYou.txt GitHub](https://github.com/dw0rsec/rockyou.txt)
