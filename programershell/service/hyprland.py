import socket
from threading import Thread
import os

terminator = b"\n"


def getTerminator():
    return terminator


def getData(clientsocket) -> None | bytes:
    received_data = b""

    try:
        # Receive data character by character until the terminator sequence is found
        while True:
            char = clientsocket.recv(1)  # Receive one byte at a time
            if not char:  # If no more data is received, exit the loop
                break
            received_data += char  # Append the received character to the received data
            ##print(received_data)
            if (
                received_data[-len(terminator) :] == terminator
            ):  # Check if the terminator sequence is present
                break
        if (
            received_data[-len(terminator) :] == terminator
        ):  # Check if the terminator sequence is present
            return received_data.rstrip(getTerminator())
    except Exception as SocketError:
        print("Socket Error: ", SocketError)
        return None

class Hyprland(Thread):
    def __init__(self):
        super().__init__()
    def run(self) -> None:
        try:
            hyprland_socket = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{os.environ['HYPRLAND_INSTANCE_SIGNATURE']}/.socket2.sock"  # Adjust the socket path as needed
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(hyprland_socket)
            client.send(b'getcurrentworkspace')
            #response = client.recv(1024).decode('utf-8').strip()
            while True:
                response = getData(client)
                msg = response.decode('utf-8').strip()
                print(msg)
        except Exception as e:
            print( f'Error: {e}')

def main():
    hypr = Hyprland()
    hypr.start()


if __name__ == "__main__":
    main()
