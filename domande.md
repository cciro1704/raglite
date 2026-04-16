## L2 — Checkpoint 1

**1. Perché `documents` e `messages` non devono essere la stessa tabella?**

Perché rappresentano cose diverse. Un documento è un file o testo che viene caricato e indicizzato, mentre un messaggio è una cosa che viene scritta durante la conversazione. Mischiarli in una tabella sola renderebbe tutto più confuso e difficile da interrogare.

**2. Come eviti di aprire due connessioni se `get_db()` viene chiamata due volte?**

Si controlla se la connessione è già salvata in `g`. Se c'è già, la riusi, altrimenti la crei. Così al massimo ne esiste una per richiesta.

**3. Perché la connessione non dovrebbe stare in una variabile globale?**

Perché Flask gestisce più richieste, magari in parallelo, e se condividono la stessa connessione si creano problemi. Ogni richiesta deve avere la sua.

---

## L2 — Checkpoint 2

**1. In quale ordine vanno le `DROP TABLE`?**

Prima le tabelle figlie, poi le madri. Quindi: `embeddings`, `chunks`, `messages`, `documents`, `sessions`. Se lo fai al contrario SQLite si lamenta per i vincoli di foreign key.

**2. Quale clausola elimina automaticamente le righe figlie?**

`ON DELETE CASCADE`. Quando elimini una riga madre, le righe figlie collegate vengono eliminate automaticamente.

**3. Perché `chunk_id` può essere la chiave primaria di `embeddings`?**

Perché ogni chunk ha esattamente un embedding — è una relazione 1:1. Non ha senso avere un id separato quando `chunk_id` identifica già la riga in modo univoco.

---

## L2 — Checkpoint 3

**1. Come controlli se la connessione è già in `g`?**

Con `if 'db' not in g` — se la chiave non esiste ancora, la crei, altrimenti la salti.

**2. Perché `open_resource` è meglio di `open`?**

Perché `open_resource` cerca il file rispetto alla cartella del pacchetto Python, non rispetto a dove sei quando lanci il comando. Con `open` normale, se esegui Flask da una cartella diversa, non trova il file.

**3. Perché `init_db_command` e `init_db` restano separate?**

Perché `init_db` fa il lavoro vero, e `init_db_command` è solo il "gancio" da CLI che la chiama. Così se in futuro vuoi chiamare `init_db` dai test o da un altro punto del codice, puoi farlo senza passare dal comando CLI.

---

## L2 — Checkpoint 4

**1. Perché `docs_indexed` va contato da `documents` e non da `chunks`?**

Perché un documento potrebbe non avere ancora chunk (non ancora processato), oppure averne molti. Contare i chunk non ti dà il numero di documenti, ti dà qualcosa di diverso.

**2. Perché tre query semplici invece di una sola "furba"?**

Perché sono più leggibili e facili da capire. Una query complessa con join o subquery per ottenere tre conteggi sarebbe più difficile da mantenere e debuggare, senza nessun vantaggio reale.

**3. Perché il route handler non deve ricreare lo schema?**

Perché non è compito suo. Ogni cosa deve fare una cosa sola: il route handler legge i dati e risponde, `init_db` si occupa di creare le tabelle. Mischiarli creerebbe casino.

---

## L2 — Auto-verifica finale

**1. Differenza tra `documents` e `messages`?**

I documenti sono il contenuto caricato e indicizzato, quello su cui il sistema fa ricerca. I messaggi sono la cronologia della conversazione, quello che scrive l'utente e quello che risponde il sistema.

**2. Perché `sessions.id` è un intero e non un testo?**

Perché è un identificatore tecnico interno, non qualcosa che viene mostrato all'utente. Gli interi sono più efficienti per i join e gli indici rispetto alle stringhe.

**3. Flusso di una richiesta `GET /api/stats`:**

Flask riceve la richiesta e la passa al route handler `stats()` in `rag.py`. Lì viene chiamata `get_db()` che apre (o recupera) la connessione da `g`. Vengono eseguite tre query di conteggio sul database. Il risultato viene restituito come JSON. A fine richiesta Flask chiama automaticamente `close_db()` (registrata con `teardown_appcontext`) che chiude la connessione.

**4. Perché `PRAGMA foreign_keys = ON` va eseguito ad ogni connessione?**

Perché SQLite di default non rispetta i vincoli di foreign key — è una scelta di compatibilità storica. Non è una impostazione permanente del database, quindi va riattivata ogni volta che apri una nuova connessione.

---

## L1 — Note di laboratorio

**Checkpoint 1.1 — Le due istanze condividono stato?**

No, ogni chiamata a `create_app()` crea un'app nuova e indipendente. Con l'approccio globale invece c'è una sola istanza condivisa, e se un test la modifica, influenza anche gli altri test.

**Checkpoint 1.2 — Dove si forma il ciclo?**

Con l'approccio globale: `__init__.py` crea `app` e importa `db`, ma `db` importa `app` da `__init__.py` che non ha ancora finito di caricarsi. Con la factory non succede perché `app` viene creata dentro una funzione, non al momento dell'import.

**Checkpoint 1.3 — Come fa Flask a trovare `create_app`?**

Flask cerca automaticamente una funzione chiamata `create_app` nel modulo indicato con `--app`. È una convenzione di Flask: se trova quella funzione, la chiama per creare l'app.

**Parte 2 — Cosa cambia senza `instance_relative_config=True`?**

Flask cerca i file di config nella cartella del pacchetto invece che in `instance/`. Con `True` i file di config vanno in `instance/`, che è fuori dal codice sorgente e non viene committata.

**Parte 4 — Nome della route `GET /api/health`:**

È registrata come `rag.health` — il prefisso `rag.` viene dal nome del Blueprint. Flask aggiunge il nome del Blueprint per evitare conflitti tra route con lo stesso nome in Blueprint diversi.

**Parte 4 — Errore con `register_blueprint` commentato:**

Restituisce HTTP 404. Flask non sa che esiste quella route perché il Blueprint non è mai stato registrato sull'app, quindi quando arriva la richiesta non trova nessun handler.

**Auto-verifica 1 — Flusso da `flask run` a `health()`:**

Flask importa il modulo `raglite` (`__init__.py`), chiama `create_app()`, che importa `rag.py` e registra il Blueprint. Quando arriva una richiesta a `/api/health`, Flask cerca nell'`url_map`, trova la route registrata dal Blueprint e chiama `health()`.

**Auto-verifica 2 — Come aggiungere un Blueprint `auth`:**

Creo `raglite/auth.py` con `bp = Blueprint("auth", __name__)` e le route. In `__init__.py` aggiungo:
```python
from . import auth
app.register_blueprint(auth.bp)
```

**Auto-verifica 3 — `url_for("rag.health")` vs `url_for("health")`:**

`url_for("rag.health")` funziona e restituisce `/api/health`. `url_for("health")` dà errore perché la route è registrata sotto il Blueprint `rag`, quindi il nome corretto include il prefisso.