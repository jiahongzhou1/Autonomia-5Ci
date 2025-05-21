# Lavagna condivisa
La nostra applicazione offre una lavagna condivisa tramite un launcher. Dal launcher puoi scegliere dei disegni in formato json salvati in locale e puoi streamarli agli altri client, oppure puoi collegarti alle lavagne di altre persone inserendo loro indirizzo ip e porta
## Interazione con applicazione
La nostra applicazione è formato da un launcher, e paintclient
### Launcher
Nel launcher è il punto di ingresso della nostra applicazione, permette di: 
- Scegliere disegni esistenti: selezionare il file Json da drive locale per iniziare una sessione.a
- Avviare una sessione di condivisione (Server): trasforma tua applicazione in un server, cosi altri possono connetterti inserendo tuo ip e porta.a
- Connetterti a una sessione (Client): inserendo ip e porta di altro client che sta condividendo
### PainClient
Il paint client è composto da 2 componenti, ToolStatusPanel e Canva.agli
Dal ToolStatusPanel puoi scegliere colore, brush size, e modalità di disegno
Mentre canva è una carta bianca scrollabile con altezza e larghezza entrambi fixati a 2000 di default, premendo tasto destro sulla canva puoi scrollare.
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
message_type, start_x, start_y, end_x, end_y, color, size
message_type sta per il tipo di messaggio, per esempio "freehand", "square", "circle".agli
start_x e start_y indicano il punto di partenza dello tratto/oggetto. 
end_x, end_y indicano il punto di fine dello tratto/oggetto.
mentre colore indica il colore che viene usato dai oggetti/tratti, e il size indica la grandezza dello tratto quando siamo in modalità freehand.