import sys
import socket
import threading


# Server Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000


def encode_message(message_type, start_x, start_y, end_x, end_y, color, size):
    """Encodes drawing data into a string format."""
    return f"{message_type},{start_x},{start_y},{end_x},{end_y},{color},{size};"

def decode_message(data):
    """Decodes a string into drawing data."""
    parts = data.split(',')
    if len(parts) == 7:
        message_type, start_x, start_y, end_x, end_y, color, size = parts
        return (message_type, int(start_x), int(start_y), int(end_x), int(end_y), color, int(size))
    else:
        return None  # Handle invalid format

# Using a custom, simple string-based protocol instead of JSON.
# Format: "type,start_x,start_y,end_x,end_y,color,size"
# Example: "draw,100,200,150,250,#ff0000,5"


# Server Code
def handle_client(conn, addr):
    """Handles communication with a single client."""
    print(f"[+] New connection from {addr}")
    while True:
        try:
            data = conn.recv(4096).decode('utf-8') # Receive as string directly
            if not data:
                break

            # Process each message in the received data
            print(f"RAW DATA{data}")
            messages = data.split(';')  # Split by message separator
            for message in messages:
                if message: # make sure message is not empty
                    decoded_message = decode_message(message.strip()) #remove leading/trailing spaces
                    if decoded_message:
                        broadcast((message+";").encode('utf-8'), conn) #send the raw string
                    else:
                        print(f"[SERVER] Invalid message format from {addr}: {message}")

        except Exception as e:
            print(f"[SERVER] Error handling client {addr}: {e}")
            break
    print(f"[-] Connection closed: {addr}")
    try:
        clients.remove(conn)
        conn.close()
    except ValueError:
        print(f"[SERVER] Error removing client {addr} from list.")

def broadcast(data, sender_conn):
    """Broadcasts data to all connected clients except the sender."""
    for client in clients:
        if client != sender_conn:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"[SERVER] Error sending to a client: {e}")
                # Remove the client if sending fails.
                try:
                    clients.remove(client)
                    client.close()
                except ValueError:
                    print("[SERVER] Client already removed")

def start_server():
    """Starts the server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
    except Exception as e:
        print(f"[SERVER] Error binding to {HOST}:{PORT}: {e}")
        print("[SERVER] Try using a different port, or check if another application is using the same port.")
        sys.exit(1)
    server.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}")
    global clients
    clients = []
    while True:
        try:
            conn, addr = server.accept()
            clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
        except Exception as e:
            print(f"[SERVER] Error accepting connection: {e}")
            break
    server.close()




if __name__ == "__main__":
    # Start the server in a separate thread
    start_server()


