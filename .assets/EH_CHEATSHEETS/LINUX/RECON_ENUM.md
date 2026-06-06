# Reconnaissance & Enumeration (Linux)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `curl`, `grep`, `cut`, `sed`, `host`, `ping`, `whois`, `gobuster` |
| **SO Target** | Linux / Web Server |
| **Quando effettuare** | Fase iniziale (Reconnaissance) |
| **Info Utili** | Mappatura superficie d'attacco, scoperta sottodomini e IP |

### Ricognizione Passiva e Sottodomini
L'obiettivo è trovare sottodomini che sembrerebbero trascurati o sottodomini in http.

**Comando Generico:**
```bash
curl -s "<URL>"
```
*Esempio:*
```bash
curl -s http://target.htb
```

**Filtraggio con Regex:**
```bash
grep -oP "<REGEX>" <FILE>
```
*Esempio:*
```bash
grep -oP '(http|https)://[a-zA-Z0-9.-]+\.[a-z]{2,}' index.html
```

**Grep pipe Cut:**
```bash
grep -oP "<REGEX>" <FILE> | cut -d '"' -f 2
```
*Esempio:*
```bash
grep -oP 'src="[^"]*"' index.html | cut -d '"' -f 2
```

**Verifica dei certificati (Cert.sh):**
È molto utile per trovare tutti i sotto-domini di un `url` principale.
```bash
curl -s "https://crt.sh/?q=<TARGET>&output=json" > subdomains_crt.txt
```
*Esempio:*
```bash
curl -s "https://crt.sh/?q=wingdata.htb&output=json" > subdomains_crt.txt
```

### HTTPS Header Fingerprint
Verifica degli header per ottenere informazioni su webserver e versione.
```bash
for domain in $(cat <SUBDOMAINS_FILE>); do curl -sI -m 5 echo %domain 2>/dev/null; done > header_subdomain.txt
```
*Esempio:*
```bash
for domain in $(cat subs.txt); do curl -sI -m 5 echo %domain 2>/dev/null; done > header_subdomain.txt
```

### Risalire agli IP
```bash
host <HOSTNAME>
ping -c 4 <HOSTNAME>
whois <HOSTNAME>
```
*Esempio:*
```bash
host wingdata.htb
ping -c 4 wingdata.htb
whois wingdata.htb
```

### Enumerazione Web (Gobuster)
**Directory Brute-forcing:**
```bash
gobuster dir -u <URL> -w <WORDLIST>
```
*Esempio:*
```bash
gobuster dir -u http://wingdata.htb -w /usr/share/wordlists/dirb/common.txt
```

**VHost Enumeration:**
```bash
gobuster vhost -u <URL> -w <WORDLIST> --append-domain
```
*Esempio:*
```bash
gobuster vhost -u http://wingdata.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain
```

### URL Fondamentali
- [Cert.sh](https://crt.sh/)
- [Regex101](https://regex101.com/)
- [CVE MITRE](https://www.cve.org/)
- [Hacktricks](https://book.hacktricks.wiki/en/index.html)
