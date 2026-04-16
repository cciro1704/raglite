
---

## L1 — Checkpoint 1

**1. Nei test, ogni test chiama esplicitamente `create_app()`. Le due istanze di app condividono stato? Cosa succederebbe invece con l'approccio globale?**

No, ogni chiamata a `create_app()` crea un'app nuova e indipendente. Con l'approccio globale invece c'è una sola istanza condivisa, e se un test la modifica influenza anche gli altri test.

**2. Nell'approccio globale, `db.py` importa `app` da `__init__.py` e `__init__.py` importa `db.py`. Dove si forma il ciclo? Perché con la factory non si forma?**

Con l'approccio globale: `__init__.py` crea `app` e importa `db`, ma `db` importa `app` da `__init__.py` che non ha ancora finito di caricarsi. Con la factory non succede perché `app` viene creata dentro una funzione, non al momento dell'import.

**3. `flask --app raglite run` trova `create_app` automaticamente. Come fa Flask a sapere dove cercarla?**

Flask cerca automaticamente una funzione chiamata `create_app` nel modulo indicato con `--app`. È una convenzione di Flask: se trova quella funzione, la chiama per creare l'app.

---

## L1 — Parte 2

**Dopo aver aggiunto temporaneamente `print(app.instance_path)` e avviato il server:**

**Path stampato a runtime:**

```
/home/cirop/raglite/instance
```

**Cosa cambia se rimuovi `instance_relative_config=True`?**

Flask non userebbe più la cartella `instance/` per i file di config, ma cercherebbe tutto dentro la cartella del pacchetto `raglite/`. I file come `config.py` andrebbero dentro il codice sorgente, che è una cosa da evitare perché potrebbe finire committata con segreti e token.

---

## L1 — Parte 4 — Esplorazione `url_map`

**Dopo aver eseguito `print(app.url_map)` nella shell Flask:**

**Output di `app.url_map`:**

```
Map([<Rule '/static/<filename>' (OPTIONS, GET, HEAD) -> static>,
 <Rule '/api/health' (OPTIONS, GET, HEAD) -> rag.health>,
 <Rule '/api/stats' (OPTIONS, GET, HEAD) -> rag.stats>])
```

**Con quale nome è registrata la route `GET /api/health`? Perché compare un prefisso?**

È registrata come `rag.health` — il prefisso `rag.` viene dal nome del Blueprint. Flask aggiunge il nome del Blueprint per evitare conflitti tra route con lo stesso nome in Blueprint diversi.

---

## L1 — Parte 4 — Errore programmato: `register_blueprint` commentato

**Dopo aver commentato `app.register_blueprint(rag.bp)` e chiamato l'endpoint:**

**Status HTTP restituito da curl:**

```
HTTP 404
```

**Messaggio di Flask:**

```
<!doctype html>
<html lang=en>
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
```

**In una riga: cosa stava mancando e perché Flask non sapeva gestire la richiesta?**

Il Blueprint non era registrato sull'app, quindi Flask non sapeva che quella route esisteva e restituiva 404.

---

## L1 — Auto-verifica pre-commit

**1. Descrivi il flusso completo da `flask --app raglite run` fino all'esecuzione di `health()`: quanti file entrano in gioco e in che ordine?**

Flask importa il modulo `raglite` (`__init__.py`), chiama `create_app()`, che importa `rag.py` e registra il Blueprint. Quando arriva una richiesta a `/api/health`, Flask cerca nell'`url_map`, trova la route registrata dal Blueprint e chiama `health()`.

**2. Se dovessi aggiungere un Blueprint `auth` con route `/login`, dove lo creeresti e quali due righe dovresti aggiungere in `__init__.py`?**

Creo `raglite/auth.py` con `bp = Blueprint("auth", __name__)` e le route. In `__init__.py` aggiungo:
```python
from . import auth
app.register_blueprint(auth.bp)
```

**3. Cosa restituisce `url_for("rag.health")`? E `url_for("health")`? Perché il comportamento è diverso?**

`url_for("rag.health")` funziona e restituisce `/api/health`. `url_for("health")` dà errore perché la route è registrata sotto il Blueprint `rag`, quindi il nome corretto include il prefisso.

---

## L2 — Checkpoint 1

**1. Perché `documents` e `messages` non devono essere la stessa tabella, anche se entrambi appartengono a una `session`?**

Perché rappresentano cose diverse. Un documento è un file o testo che viene caricato e indicizzato, mentre un messaggio è quello che viene scritto durante la conversazione. Mischiarli in una tabella sola renderebbe tutto più confuso e difficile da interrogare.

**2. Se `get_db()` viene chiamata due volte nella stessa richiesta, come puoi evitare di aprire due connessioni?**

Si controlla se la connessione è già salvata in `g`. Se c'è già, la riusi, altrimenti la crei. Così al massimo ne esiste una per richiesta.

**3. Perché una connessione SQLite non dovrebbe stare in una variabile globale di modulo?**

Perché Flask gestisce più richieste, magari in parallelo, e se condividono la stessa connessione si creano problemi. Ogni richiesta deve avere la sua.

---

## L2 — Checkpoint 2

**1. In quale ordine vanno eliminate le tabelle con `DROP TABLE IF EXISTS`?**

Prima le tabelle figlie, poi le madri. Quindi: `embeddings`, `chunks`, `messages`, `documents`, `sessions`. Se lo fai al contrario SQLite si lamenta per i vincoli di foreign key.

**2. Quale clausola SQL ti serve per eliminare automaticamente le righe figlie quando elimini una riga madre?**

`ON DELETE CASCADE`. Quando elimini una riga madre, le righe figlie collegate vengono eliminate automaticamente.

**3. Perché `chunk_id` può essere la chiave primaria di `embeddings`?**

Perché ogni chunk ha esattamente un embedding — è una relazione 1:1. Non ha senso avere un id separato quando `chunk_id` identifica già la riga in modo univoco.

---

## L2 — Checkpoint 3

**1. Come controlli se la connessione è già stata salvata in `g`?**

Con `if 'db' not in g` — se la chiave non esiste ancora, la crei, altrimenti la salti.

**2. Perché `current_app.open_resource("schema.sql")` è più robusto di `open("schema.sql")`?**

Perché `open_resource` cerca il file rispetto alla cartella del pacchetto Python, non rispetto a dove sei quando lanci il comando. Con `open` normale, se esegui Flask da una cartella diversa, non trova il file.

**3. Perché `init_db_command()` e `init_db()` dovrebbero restare separate?**

Perché `init_db` fa il lavoro vero, e `init_db_command` è solo il gancio da CLI che la chiama. Così se in futuro vuoi chiamare `init_db` dai test o da un altro punto del codice, puoi farlo senza passare dal comando CLI.

---

## L2 — Checkpoint 4

**1. Perché ora `docs_indexed` va contato da `documents` e non da `chunks`?**

Perché un documento potrebbe non avere ancora chunk, oppure averne molti. Contare i chunk non ti dà il numero di documenti, ti dà qualcosa di diverso.

**2. Perché qui tre query semplici sono più adatte del tentativo di comprimere tutto in una query più "furba"?**

Perché sono più leggibili e facili da capire. Una query complessa per ottenere tre conteggi sarebbe più difficile da mantenere e debuggare, senza nessun vantaggio reale.

**3. Perché il route handler deve limitarsi a leggere dal database e non a ricrearne lo schema?**

Perché non è compito suo. Ogni cosa deve fare una cosa sola: il route handler legge i dati e risponde, `init_db` si occupa di creare le tabelle. Mischiarli creerebbe casino.

---

## L2 — Auto-verifica finale

**1. Qual è la differenza di ruolo tra `documents` e `messages`?**

I documenti sono il contenuto caricato e indicizzato, quello su cui il sistema fa ricerca. I messaggi sono la cronologia della conversazione, quello che scrive l'utente e quello che risponde il sistema.

**2. Perché `sessions.id` qui ha senso come intero e non come testo?**

Perché è un identificatore tecnico interno, non qualcosa che viene mostrato all'utente. Gli interi sono più efficienti per i join e gli indici rispetto alle stringhe.

**3. Descrivi il flusso di una richiesta `GET /api/stats` dal route handler alla chiusura della connessione.**

Flask riceve la richiesta e la passa al route handler `stats()` in `rag.py`. Lì viene chiamata `get_db()` che apre o recupera la connessione da `g`. Vengono eseguite tre query di conteggio. Il risultato viene restituito come JSON. A fine richiesta Flask chiama automaticamente `close_db()` che chiude la connessione.

**4. Perché `PRAGMA foreign_keys = ON` va eseguito ad ogni nuova connessione?**

Perché SQLite di default non rispetta i vincoli di foreign key. Non è una impostazione permanente del database, quindi va riattivata ogni volta che apri una nuova connessione.
