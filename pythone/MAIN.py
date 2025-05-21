import sys
import socket
import threading
import time # Import time for sleep in the server loop

class WhiteboardServer:
    """
    A simple TCP server for a collaborative whiteboard application.
    It handles client connections, decodes drawing messages,
    and broadcasts them to all other connected clients.
    """

    def __init__(self, drawing_history, host='0.0.0.0', port=5000):
        """
        Initializes the WhiteboardServer with a specified host and port.

        Args:
            drawing_history (list): A list to store drawing commands.
            host (str): The IP address the server will listen on.
                        '0.0.0.0' means listen on all available interfaces.
            port (int): The port number the server will listen on.
        """
        self.drawing_history = drawing_history
        self.host = host
        self.port = port
        self.clients = []  # List to keep track of connected client sockets
        self.server_socket = None # To hold the main server socket

    def encode_message(self, message_type, start_x, start_y, end_x, end_y, color, size):
        """
        Encodes drawing data into a string format for transmission.
        This is now an instance method.

        Args:
            message_type (str): Type of message (e.g., "draw").
            start_x (int): Starting X coordinate.
            start_y (int): Starting Y coordinate.
            end_x (int): Ending X coordinate.
            end_y (int): Ending Y coordinate.
            color (str): Color of the drawing (e.g., "#ff0000").
            size (int): Size/thickness of the drawing line.

        Returns:
            str: The encoded message string.
        """
        return f"{message_type},{start_x},{start_y},{end_x},{end_y},{color},{size};"

    def decode_message(self, data):
        """
        Decodes a string received from a client into drawing data components.
        This is now an instance method.

        Args:
            data (str): The raw message string received from a client.

        Returns:
            tuple or None: A tuple containing (message_type, start_x, start_y,
                           end_x, end_y, color, size) if decoding is successful,
                           otherwise None.
        """
        parts = data.split(',')
        if len(parts) == 7:
            message_type, start_x, start_y, end_x, end_y, color, size = parts
            try:
                return (message_type, int(start_x), int(start_y), int(end_x), int(end_y), color, int(size))
            except ValueError:
                # Handle cases where numeric parts are not valid integers
                print(f"[SERVER] Decoding error: Invalid numeric data in message: {data}")
                return None
        else:
            return None  # Handle invalid format (e.g., wrong number of parts)

    def broadcast(self, data, sender_conn):
        """
        Broadcasts data to all connected clients except the sender.

        Args:
            data (bytes): The encoded message data to be sent.
            sender_conn (socket.socket): The socket of the client who sent the data.
        """
        # Create a list of clients to iterate over to avoid issues if clients are removed during iteration
        clients_to_broadcast = list(self.clients)
        for client in clients_to_broadcast:
            if client != sender_conn:
                try:
                    client.sendall(data)
                except Exception as e:
                    self.remove_client(client)

    def remove_client(self, client_socket):
        """
        Removes a client socket from the list of connected clients and closes it.

        Args:
            client_socket (socket.socket): The socket of the client to remove.
        """
        try:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
                client_socket.close()
        except Exception as e:
            print(f"[SERVER] Error removing client: {e}")


    def handle_client(self, conn, addr):
        """
        Handles communication with a single client.
        Receives data, decodes it, and broadcasts it.

        Args:
            conn (socket.socket): The socket object for the client connection.
            addr (tuple): The address (IP, port) of the client.
        """
        print(f"[+] New connection from {addr}")
        # Send existing drawing history to the newly connected client
        ipAdd , _ = addr
        if(ipAdd != "127.0.0.1"):
            tmp = ""
            tmpInt = 0
            for item in self.drawing_history:
                tmp += self.encode_message(item['type'], item['start_x'], item['start_y'],
                                        item['end_x'], item['end_y'], item['color'], item['size'])
                if(tmpInt == 18):
                    print(tmp)
                    try:
                        # Send directly to the new client, not broadcast
                        conn.sendall(tmp.encode('utf-8'))
                        tmpInt = 0
                        tmp = ""
                    except Exception as e:
                        print(f"[SERVER] Error sending history to new client {addr}: {e}")
                        break # Stop sending history if there's an error
                tmpInt += 1
        while True:
            try:
                data = conn.recv(4096).decode('utf-8')
            except Exception as e:
                continue
            print(data)
            if(not data):
                continue
            # Process each message in the received data
            messages = data.split(';')
            for message in messages:
                if message:
                    decoded_message = self.decode_message(message.strip())
                    if decoded_message:
                        # Add to drawing history
                        message_type, start_x, start_y, end_x, end_y, color, size = decoded_message
                        self.drawing_history.append({
                            'type': message_type,
                            'start_x': start_x, 'start_y': start_y,
                            'end_x': end_x, 'end_y': end_y,
                            'color': color, 'size': size
                        })
                        # Broadcast the raw string message (plus separator) to other clients
                        self.broadcast((message + ";").encode('utf-8'), conn)
                    else:
                        print(f"[SERVER] Invalid message format from {addr}: {message}")

        print(f"[-] Connection closed for: {addr}")
        self.remove_client(conn) # Ensure client is removed on graceful or error-based disconnect

    def start_server(self):
        """
        Starts the main server loop, binding to the specified host and port,
        and accepting incoming client connections.
        Each new connection is handled in a separate thread.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((self.host, self.port))
        except Exception as e:
            print(f"[SERVER] Error binding to {self.host}:{self.port}: {e}")
            print("[SERVER] Try using a different port, or check if another application is using the same port.")
            return # Exit the thread if binding fails

        self.server_socket.listen()
        print(f"[SERVER] Listening on {self.host}:{self.port}")



        while True:
            try:
                conn, addr = self.server_socket.accept()
                self.clients.append(conn)
                # Start a new thread to handle the client connection
                thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                thread.start()
            except socket.timeout:
                # No new connection within the timeout, check stop_event again
                continue
            except Exception as e:
                    print(f"[SERVER] Error accepting connection: {e}")
                    break
