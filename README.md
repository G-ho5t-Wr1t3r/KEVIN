# KEVIN (Offensive Toolsuite)

<center><img src=".assets/.imgs/kevin_logo.jpg" width="700" height="350"></center>

*Language Selection*
<details>
  <summary><b>IT</b></summary>

**AVVISO: Questo progetto è IN FASE DI SVILUPPO ed è attualmente in fase di sviluppo attivo. Alcune funzionalità potrebbero essere incomplete o soggette a modifiche significative.**

KEVIN è una suite di strumenti di sicurezza offensiva progettata per automatizzare la fase di ricognizione e configurazione iniziale delle attività di penetration testing. Semplifica la creazione di uno spazio di lavoro strutturato, l’identificazione dei target, la scansione della rete e l’enumerazione web.

## Caratteristiche principali
- **Configurazione automatizzata**: gestisce `/etc/hosts` e le connessioni VPN (OpenVPN/WireGuard).
- **Scansione di rete**: routine Nmap integrate per l’individuazione completa delle porte, il versioning dei servizi e il rilevamento del sistema operativo.
- **Enumerazione web**: fuzzing automatizzato di directory e vhost tramite Gobuster (modulo Dora).
- **Analisi intelligente**: mappatura porta-servizio con approfondimenti contestuali e suggerimenti da cheat sheet (modulo Frank).
- **Gestione delle credenziali**: archiviazione strutturata e recupero delle credenziali individuate (modulo Cesare).
- **Organizzazione dell’area di lavoro**: crea una struttura di directory standard per log, scansioni e proof of concept.
- **Doppia interfaccia**: funzionalità complete disponibili tramite interfaccia a riga di comando (CLI) e interfaccia grafica utente (GUI).

## Requisiti
### Strumenti di sistema
- Nmap
- Gobuster
- OpenVPN
- WireGuard

### Ambiente Python
- Python 3.x
- Librerie Python: `rich`, `requests`, `tkinter`

## Installazione
1. Installare le dipendenze di sistema:
   ```bash
   chmod +x scripts/install_requirements.sh
   ./scripts/install_requirements.sh
   ```
2. Installare le dipendenze Python:
   ```bash
   pip install -r requirements.txt
   ```

## Utilizzo

### Modalità CLI
Per eseguire KEVIN in modalità CLI, specificare l'IP di destinazione, il nome host e il percorso dell'area di lavoro:
```bash
python3 kevin.py --ip <IP> --host-name <NAME> --workspace <PATH> [opzioni]
```


**Opzioni comuni:**
- `--common-name <NAME>`: Nome comune del computer.
- `--nmap`: Esegue una scansione completa con nmap.
- `--udp`: Esegue una scansione UDP con nmap.
- `--dora <dvf>`: Avvia l'enumerazione Dora (d: directory, v: vhost, f: fuzz).
- `--frank`: Esegue il motore di analisi Frank.
- `--vpn <PERCORSO>`: Percorso del file di configurazione .ovpn o WireGuard.
- `--alias <FILE>`: Crea l'alias “kevin” nel file specificato (ad es., ~/.bashrc).
- `--debug`: Abilita la registrazione dei log di debug.

### Modalità GUI
Per avviare l’interfaccia grafica, eseguire lo script senza argomenti o con il flag `--gui`:
```bash
python3 kevin.py
# oppure
python3 kevin.py [altri] --gui
```

## Struttura dell’area di lavoro
KEVIN crea un ambiente strutturato per ciascun target nel percorso specificato dell’area di lavoro:
- `nmap/`: Risultati della scansione.
- `gobuster/`: output del fuzzing.
- `PoCs/`: file Proof of Concept.
- `misc/`: note generali e archiviazione strutturata delle credenziali.

## Licenza
Questo progetto è concesso in licenza ai sensi della [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Ciò significa che sei libero di condividere e modificare il materiale, a condizione che tu mi attribuisca il merito, non lo utilizzi per scopi commerciali e distribuisca eventuali versioni modificate sotto la stessa licenza.

</details>

<details>
  <summary><b>EN</b></summary>

**WARNING: This project is a WORK IN PROGRESS and is currently under active development. Some features may be incomplete or subject to significant changes.**

KEVIN is an offensive security toolsuite designed to automate the reconnaissance and initial setup phase of penetration testing engagements. It streamlines the creation of a structured workspace, target identification, network scanning, and web enumeration.

## Key Features
- **Automated Setup**: Manages `/etc/hosts` and VPN connections (OpenVPN/WireGuard).
- **Network Scanning**: Integrated Nmap routines for full port discovery, service versioning, and OS detection.
- **Web Enumeration**: Automated directory and vhost fuzzing using Gobuster (Dora module).
- **Intelligent Analysis**: Port-to-service mapping with contextual insights and cheatsheet suggestions (Frank module).
- **Credential Management**: Structured storage and retrieval of discovered credentials (Cesare module).
- **Workspace Organization**: Creates a standard directory structure for logs, scans, and proofs of concept.
- **Dual Interface**: Full functionality available via Command Line Interface (CLI) and Graphical User Interface (GUI).

## Requirements
### System Tools
- Nmap
- Gobuster
- OpenVPN
- WireGuard

### Python Environment
- Python 3.x
- Python libraries: `rich`, `requests`, `tkinter`

## Installation
1. Install system dependencies:
   ```bash
   chmod +x scripts/install_requirements.sh
   ./scripts/install_requirements.sh
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### CLI Mode
To run KEVIN in CLI mode, specify the target IP, host name, and workspace path:
```bash
python3 kevin.py --ip <IP> --host-name <NAME> --workspace <PATH> [options]
```

**Common Options:**
- `--common-name <NAME>`: Machine's Common Name.
- `--nmap`: Runs full nmap scan.
- `--udp`: Runs nmap UDP scan.
- `--dora <dvf>`: Call Dora enumeration (d: dir, v: vhost, f: fuzz).
- `--frank`: Run Frank analysis engine.
- `--vpn <PATH>`: Path to .ovpn or wireguard config.
- `--alias <FILE>`: Create "kevin" alias in specified file (e.g., ~/.bashrc).
- `--debug`: Enable debug logging.

### GUI Mode
To launch the graphical interface, run the script without arguments or with the `--gui` flag:
```bash
python3 kevin.py
# or
python3 kevin.py [others] --gui
```

## Workspace Structure
KEVIN creates a structured environment for each target at the specified workspace path:
- `nmap/`: Scan results.
- `gobuster/`: Fuzzing outputs.
- `PoCs/`: Proof of Concept files.
- `misc/`: General notes and structured credential storage.

## License
This project is licensed under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
This means you are free to share and modify the material, provided that you credit me, do not use it for commercial purposes, and distribute any modified versions under the same license.

</details>
