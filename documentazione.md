# Lavagna condivisa
La nostra applicazione offre una lavagna condivisa tramite un launcher. Dal launcher puoi scegliere dei disegni in formato json salvati in locale e puoi streamarli agli altri client, oppure puoi collegarti alle lavagne di altre persone inserendo loro indirizzo ip e porta
## Interazione con applicazione
La nostra applicazione è formato da un launcher, e paintclient
### Launcher
Nel launcher è il punto di ingresso della nostra applicazione, permette di: 
- Scegliere disegni esistenti: selezionare il file Json da drive locale per iniziare una sessione.a
- Avviare una sessione di condivisione (Server): trasforma tua applicazione in un server, cosi altri possono connetterti inserendo tuo ip e porta
- Connetterti a una sessione (Client): inserendo ip e porta di altro client che sta condividendo la sua lavagna
### PainClient
Il paint client è composto da 2 componenti, ToolStatusPanel e Canva.
ToolStatusPanel è situato nella parte superiore dell'interfaccia, questo pannello permette di:
- Selezionare colore
- Cambiare la dimensione del brush
- Scegliere la modalità di disegno
- Salvare i file e avviare la modalità 'stream file'
Mentre Canvas è situato nella parte inferiore dell'interfaccia che si tratta di un area di grandezza 2000x2000 che puoi:
- Trascinare area premendo premuto tasto destro del mouse per visualizzare tutta canva.
## Modalità di disegno
La nostra applicazione offre la scelta dei colori e la grandezza della penna per la modalità freehand
Applicazione offre 4 modalità di disegno:
- Freehand
- Square
- Rectangle
- Circle
Per modalità di disegno Square, Rectangle, Circle offriamo un visualizzazione anteprima della forma geometrica. La forma viene realmente disegnata sulla canva quando


## Trasmissione del messaggio
ogni tratto sulla canva viene salvato in formato json con dei parametri. questi parametri sono mandati tramite broadcast ai altri client
<br>
Il formato del messaggio è il seguente:

`message_type, start_x, start_y, end_x, end_y, color, size;`

* `message_type`: Indica il tipo di elemento disegnato (es. "draw" per freehand, "square", "rectangle", "circle").
* `start_x`, `start_y`: Rappresentano le coordinate X e Y del punto di partenza del tratto o dell'oggetto.
* `end_x`, `end_y`: Rappresentano le coordinate X e Y del punto di fine del tratto o dell'oggetto. Per le forme, questi punti definiscono la dimensione e la posizione della forma (es. l'angolo opposto per un rettangolo, o un punto sulla circonferenza per un cerchio).
* `color`: Indica il colore utilizzato per disegnare l'oggetto o il tratto, solitamente in formato esadecimale (es. "#RRGGBB").
* `size`: Indica la grandezza (spessore) del tratto per la modalità freehand o lo spessore del bordo per le forme geometriche.
