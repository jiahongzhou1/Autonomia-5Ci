# Lavagna condivisa

La nostra applicazione offre una lavagna condivisa tramite un launcher. Dal launcher puoi scegliere dei disegni in formato json salvati in locale e puoi streamarli agli altri client, oppure puoi collegarti alle lavagne di altre persone inserendo loro indirizzo ip e porta

## Tecnologie usate

### risorse "native" di python

-`os / sys` -`os`
Interagisci con il sistema operativo per operazioni su file, directory, processi, ecc. -`sys`
Accedi a variabili e funzionalità specifiche dell'interprete Python (argomenti riga di comando, percorsi, ecc.). -`threading`
Esegui codice in parallelo usando i thread all'interno di un singolo processo. Utile per migliorare la reattività e sfruttare CPU multi-core. -`socket`
Crea applicazioni di rete (client e server) per comunicare tramite protocolli come TCP/IP. Fornisce un'interfaccia di basso livello per le reti. -`json`
Serializza oggetti Python in formato JSON (stringhe) e deserializza stringhe JSON in oggetti Python. Fondamentale per lo scambio di dati. -`math`
Offre un insieme di funzioni matematiche standard (trigonometriche, logaritmiche, ecc.) e costanti (pi greco, e). -`time`
Fornisce strumenti per misurare il tempo, mettere in pausa l'esecuzione e lavorare con date e orari. -`errno`
Definisce costanti simboliche per i codici di errore restituiti da chiamate di sistema, utili per una gestione più precisa degli errori di basso livello.

### libreri esterne

-`pyqt5`
Binding Python per la libreria Qt v5, usata per creare interfacce grafiche (GUI) multipiattaforma con widget, segnali/slot, grafica 2D e altro. Fondamentale per applicazioni desktop con Python.

## Interazione con applicazione

La nostra applicazione è formato da un launcher, e un Canva

### Launcher (GUI.py)

Nel launcher è il punto di ingresso della nostra applicazione, permette di:

- Scegliere disegni esistenti: selezionare il file Json da drive locale per iniziare una sessione.a
- Avviare una sessione di condivisione (Server): trasforma tua applicazione in un server, cosi altri possono connetterti inserendo tuo ip e porta
- Connetterti a una sessione (Client): inserendo ip e porta di altro client che sta condividendo la sua lavagna

#### Variabili Globali

- `SCRIPT_DIR`
  path assoluta della directory dove si trova attualmente lo script

- `SAVED_IR`
  path assoluta della directoru dove si trovano i file salvati

#### Classe FileBrowserWindow(QMainWindow)

- `FileBrowserWindow(QMainWindow)`

Classe principale del Launcher da cui vengono inizializzate tutte le variabili e sottoclassi necessarie, esso estende la classe QMainWindow di pyqt (QMainWindow è un "oggetto" di pyqt che ci da in dietro una finestra bianca attraverso l'estensione di questi "template" possiamo crearci blocchi personalizzati)

##### Funzionamento dei metodi presenti

- `__init__(self)`
  non accetta nessun parametro , anchesso fa estensione di un componente pyqt(QMainWindow) e per tanto fa `super().__init__()`.
  dentro esso viene fatto anche un cheack dell'esistenza della directory dove vengono salvati i file , in caso negativo viene generato la firectori

- `set_server_details(self, suppress_message=False)`
  metodo che scatta al click del pulsante di connesione al server, esso fa il check della validita di IP e PORTA, una volta validata richiamera il metodo `file_box_clicked(IP=ip,PORT=port)` e fa startare il client

- `refresh_file_list(self)`
  metodo che fa il check dei eleemnti presenti nella cartella `Saves` e fa il rerendering dei componenti presenti nel `ClickableFrame(QFrame)`, questo metodo viene richiamato alla creazione della classe e alla cancellazione creazione di nuovi file

- `file_box_clicked(self, filename = "tmp.json" , filepath = "Saves/tmp.json" , IP = "127.0.0.1" , PORT = "5000")`
  questo metodo serve per far partire il `client.py` con i dati necessari (filename/filepath/IP/Port), questo metodo parte quando viene cliccato uno dei blocchi generati sopra

- `create_new_file(self)`
  una volta immesso un nome valido esso crea un nuovo file con quel nome nella directory `Saves` , salvera tutti i file come .json , viene richiamato dal click di un pulsante

- `delete_existing_file(self)`
  una volta immesso un nome di un file esistente , cancellera quel file dalla directory `Saves`, viene richiamato dal click di un pulsante

#### Classe ClickableFrame(QFrame)

- `ClickableFrame(QFrame)`

Classe che viene istanziato da `FileBrowserWindow(QMainWindow)`e serve per la generazione di componenti cliccabili che verranno usati per aprire i file presenti nella cartella `Saves`

##### Funzionamento dei metodi presenti

- `clicked = pyqtSignal()`
  rendiamo clicked in un pyqt signal ovvero in un "campanello" che avvisera tutti i componenti in ascolto di esso che è avvenuto un cambiamento ad esso questo è utile per la comunicazione tra componenti che non hanno "diretto" accesso tra loro

- `__init__(self, filename, parent=None)`
  all'inizio dell init facciamo `super().__init__(parent)` ovvero facciamo si che la classe `ClickableFrame(QFrame)` erediti i `init` del suo padre

  all'istanzazione della classe possiamo inserire 2 parametri :

  - `filename`
    nome del file che verra posto all'interno di un blocco "cliccabile"
  - parent
    reference dell'oggetto che fungera da padre ad esso (creare relazione padre e figlio per i widget di pyqt permettendo propagazione di eventi e ownership dei componenti [Es se padre viene eliminato anche figlio viene eliminato])

- `mousePressEvent(self, event)`
  metodo che ci serve per catturare l'evento di `click` con tasto sinistro sui componenti di `ClickableFrame(QFrame)`

### Il Canva (client.py)

Il paint client è composto da 2 componenti, ToolStatusPanel e Canva.
ToolStatusPanel è situato nella parte superiore dell'interfaccia, questo pannello permette di:

- Selezionare colore
- Cambiare la dimensione del brush
- Scegliere la modalità di disegno
- Salvare i file e avviare la modalità 'stream file'
  Mentre Canvas è situato nella parte inferiore dell'interfaccia che si tratta di un area di grandezza 2000x2000 che puoi:
- Trascinare area premendo premuto tasto destro del mouse per visualizzare tutta canva.

#### PaintClient

PaintClient è la classe principale, e contiene seguenti metodi

- `__init__(self)`
  Costruttore che inizializza la classe PaintClass, definisce titolo della finestra, e grandezza iniziale della finestra.
- `resizeEvent(self)`
  Questo metodo viene chiamato automaticamente quando la finestra vien ridimensionata.
- `update_canvas(self, preview=False)`
  Una funzione molto importante che converte le informazoni salvati nel array drawing_history in disegno, offre anche il preview delle forme geometriche quando lo stai creando, questa implementazione funziana perche quando fai il preview, le informazioni sul shape temporaneo non vengono salvati nel drawing_history, vengono salvati solo quando lasci il tasto sinistro del mouse, le informazioni vengono aggiunti al drwaing_history, e
  iene chiamato update_canvas per disegnare il vero e proprio oggetto sulla canva.
- `onDisconnect(self)`
  Questa funzione viene attivata quando socketLost emette un segnale, che ci dice la connessione con il server è persa.
- `listen_server(self)`
  Questa funzione lavora su un thread separato che riceve i messaggi da server e li appende all'array drawing_history, e chiama update_canvas per disegnare informazione aggiunta.
- `is_socket_alive(self)`
  serve per verificare la connessione TCP, mandando un messagio vuoto per vedere se c'è ancora la connessione
- `mousePressEvent(self, event: QMouseEvent)`
  viene chiamato quando un tasto del mouse viene cliccato, fa controlli del freehand draw(tasto sinistro), shape draw(tasto sinistro), oppure un drag(tasto destro)
- `mouseMoveEvent(self, event: QMouseEvent)`
  viene chiamato quando muoviamo il mouse, fa il controllo sulla nostra modalita di disegno, se è freehand modifica drawing_history, se è una forma geometrica, modifica il temp_end_point, temp_end_point serve per la fuzionalità del preview della figura.
- `mouseReleaseEvent(self, event: QMouseEvent)`
  Questa funzione viene chiamata quando un tasto del mouse viene rilasciato
- `on_color_changed(self, color: QColor)`
  viene attivato quando il colore cambia(connesso al signal)
- `on_brush_size_changed(self, size: int)`
  viene attivato quando il brush size cambia(connesso al signal)
- `on_shape_changed(self, shape: str)`
  viene attivato quando il shape cambia(connesso al signal)
- `closeEvent(self, event: QCloseEvent)`
  viene chiamato quando la finestra sta per chiudere, e serve per gestire dei popup che chiede all'utente se vogliono salvare i file etc.
- `clear_file(self, filepath): `
  serve per cancellare i contenuti di un file

#### ToolStatusPanel

- `__init__(self, parent_instance, parent=None)`
  inizializza pannello degli strumenti
- `choose_color(self)`
  apre una finestra dialogo che permette di scegliere i colori
- `update_color(self, color: QColor)`
  aggiorna il colore sul pannello, e manda un segnale che dice il colore è stato cambiato
- `change_brush_size(self, value: int)`
  aggiorna il testo sul pannello che mostra la grandezza del brush corrente, e poi emette un segnale.
- `get_color(self)`
  serve al server per inizializzare i suoi valori
- `get_brush_size(self)`
  serve al server per inizializzare i suoi valori
- `get_shape(self)`
  serve al server per inizializzare i suoi valori
- `on_button1_clicked(self)`
  si occupa di salvare il file di disegno
- `on_button2_clicked(self)`
  si occupa di inizializzare e avviare il server di lavagna passando drawing_history tramite reference della classe padre(PaintClient)che parte in un thread separato.

### Feature

La nostra applicazione offre la scelta dei colori e la grandezza della penna per la modalità freehand
Applicazione offre 4 modalità di disegno:

- Freehand
- Square
- Rectangle
- Circle
  Per modalità di disegno Square, Rectangle, Circle offriamo un visualizzazione anteprima della forma geometrica. La forma viene realmente disegnata sulla canva quando

### Il Server Locale (LocalServer.py)

Il local Server è un componente il cui viene gestito autonomamente dal programma e il end user non avra nessuna interazione con essa,egli ha il compito di:

- gestione dei vari client che si collegheranno
- l'inoltrazione di messaggi(dati) tra i vari client
- controllo della "qualita" dati (eliminazione in caso di dati corrotti)

##### Funzionamento delle classi presenti

- `class WhiteboardServer`
  unica classe di local server dove troviamo tutti i metodi necessari per la comunicazione tra clients

##### Funzionamento dei metodi presenti

- `__init__(self, drawing_history, host='0.0.0.0', port=5000)`
  alla creazione della classe vengono accettati tre parametri:

  - `drawing_history`
    un array di dizionari (fromato [{a:v}{c:d}]) che contiene la "storia" di tutte le azioni compiute (Es : un tratteggio verra salvato la dentro)
  - `host`
    la interfaccia di rete che il server ascoltera (di default `0.0.0..0`)
  - `port`
    la porta la quale il server ascoltera (di default `5000`)

  oltre ai tre parametri verranno inizializati anche :`client` un array per che
  terra traccia di tutti i client che si collegheranno , `server_socket` il socket che verra usato dal server per ascoltare

- `decode_message(self, data)`
  metodo per la decodifica dei messaggi in arrivo , formattera il testo in arrivo in una tupla (forma => `(message_type, int(start_x), int(start_y), int(end_x), int(end_y), color, int(size))`)

- `encode_message(self, message_type, start_x, start_y, end_x, end_y, color, size)`
  prende i dati in formato testo e li ricodifica per la trasmissione via socket

- `broadcast(self, data, sender_conn)`
  all'arrivo di un dato da parte di un client , emaneremo il dato arrivato a il resto dei client collegati

- `remove_client(self, client_socket)`
  metodo che viene richiamato dal broadcast dove quando cerca di mandare messaggio ad un sockeet e trova errore , rimuovera quel socket dalla lista di client in ascolto

- `handle_client(self, conn, addr)`
  metodo che viene fatto partire come un thread da start server, esso ha il compito di ascoltare i dati in arrivo dai client (ce un handler per ogni client) e si impegna a propagarli al resto dei client

- `start_server(self)`
  metodo principale della classe WhiteBoardServer , quando viene fatto un'istanza di questa classe si fa partire subito questo metodo che si mettera in subito in ascolto dei client che si vorranno collegare aggiungendole nella lista e facendo partire il loro corrispettivo `handle_client(self, conn, addr)`

## Trasmissione del messaggio

ogni tratto sulla canva viene salvato in formato json con dei parametri. questi parametri sono mandati tramite broadcast ai altri client
<br>
Il formato del messaggio è il seguente:

`message_type, start_x, start_y, end_x, end_y, color, size;`

- `message_type`: Indica il tipo di elemento disegnato (es. "draw" per freehand, "square", "rectangle", "circle").
- `start_x`, `start_y`: Rappresentano le coordinate X e Y del punto di partenza del tratto o dell'oggetto.
- `end_x`, `end_y`: Rappresentano le coordinate X e Y del punto di fine del tratto o dell'oggetto. Per le forme, questi punti definiscono la dimensione e la posizione della forma (es. l'angolo opposto per un rettangolo, o un punto sulla circonferenza per un cerchio).
- `color`: Indica il colore utilizzato per disegnare l'oggetto o il tratto, solitamente in formato esadecimale (es. "AAAAAA").
- `size`: Indica la grandezza (spessore) del tratto per la modalità freehand o lo spessore del bordo per le forme geometriche.

#### FONTI

- [Componenti pyqt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/api/qtwidgets/qtwidgets-module.html)
- [tutorial pyqt5](https://www.pythonguis.com/pyqt5-tutorial/)
- [Gemini](https://gemini.google.com/app)
- [Chat-GPT](https://chatgpt.com/)
- [Tutorial_YT_MOLTO_NOIOSO](https://www.youtube.com/watch?v=92zx_U9Nzf4)
- [Altro_Tutorial_YT](https://www.youtube.com/watch?v=E4WlUXrJgy4)
