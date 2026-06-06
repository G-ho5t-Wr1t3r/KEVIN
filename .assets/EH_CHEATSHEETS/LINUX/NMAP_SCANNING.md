# Nmap Scanning & Host Discovery

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `nmap`, `ping` |
| **SO Target** | Qualsiasi (Linux/Windows) |
| **Quando effettuare** | Dopo la ricognizione IP iniziale |
| **Info Utili** | Identificazione host attivi, porte aperte e servizi |

### Host Discovery
Prima di passare al comando `nmap` vogliamo verificare quali sono gli host attivi.

**Ping sweep manuale:**
```bash
ping -c 4 <IP_OR_HOSTNAME>
```
*Esempio:*
```bash
ping -c 4 10.129.3.48
```

**Nmap Ping Sweep:**
```bash
nmap -sn <IP_TARGET>/<MASK>
```
*Esempio:*
```bash
nmap -sn 172.20.0.0/24
```

**Host Discovery (ARP):**
```bash
nmap -PR <IP_TARGET>/<MASK>
```
*Esempio:*
```bash
nmap -PR 172.20.0.0/24
```

### Scansione Porte e Servizi
Non conviene runnare `nmap` troppe volte per evitare di generare troppo rumore.

**Scansione Iniziale (Default scripts + Version detection):**
```bash
nmap -sV -sC <IP_TARGET> -oA <OUTPUT_PATH>
```
*Esempio:*
```bash
nmap -sV -sC 10.129.3.48 -oA nmap/initial
```

**Scansione Full Range (Tutte le porte):**
Solitamente conviene prima runnare il comando precedente e poi lanciare una scansione full range.
```bash
nmap -p- <IP_TARGET> -oA <OUTPUT_PATH>
```
*Esempio:*
```bash
nmap -p- 10.129.3.48 -oA nmap/full_ports
```

### URL Fondamentali
- [Nmap Official Site](https://nmap.org/)
- [Hacktricks Nmap](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-network/index.html)
