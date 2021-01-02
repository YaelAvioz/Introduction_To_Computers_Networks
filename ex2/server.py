import socket
import os
import sys

server_port = int(sys.argv[1])
BUFFER_SIZE = 1024
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', server_port))
server.listen(5)

while True:
    client_socket, client_address = server.accept()
    client_socket.settimeout(1.0)
    text_data = ''
    while True:
        try:
            if text_data.find('\r\n\r\n') == -1:
                data = client_socket.recv(BUFFER_SIZE)
                text_data += data.decode()
            # extract message from data that was read from buffer
            message = text_data[:text_data.find('\r\n\r\n')]
            # keep track of reminding data read from buffer
            text_data = text_data[text_data.find('\r\n\r\n') + 4:]
            print(message + '\r\n\r\n')
            # here we will handle each message
            # each message will init it's flag variables
            file_path = ''
            connection_info = 'close'   # default value, this will help us handle null messages

            if 'Connection: ' in message:
                # extract connection info
                if ' close' in message:
                    connection_info = 'close'
                if ' keep-alive' in message:
                    connection_info = 'keep-alive'

            if 'GET /' in message:
                # extract file_path name
                file_path = message[message.find('GET /') + len('GET '):message.find(' HTTP/')]

                if file_path == '/redirect':
                    connection_info = 'close'
                    HTTP_header = 'HTTP/1.1 301 Moved Permanently\r\n'
                    HTTP_header += 'Connection: ' + connection_info + '\r\n'
                    HTTP_header += 'Location: /result.html\r\n\r\n'
                    client_socket.send(HTTP_header.encode())
                    break

                if file_path == '/':
                    file_path = 'files/index.html'
                else:
                    # add files/ to file_path
                    file_path = 'files' + file_path
                # check if file exists
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        file_size = os.stat(file_path).st_size
                        HTTP_header = 'HTTP/1.1 200 OK\r\n'
                        HTTP_header += 'Connection: ' + connection_info + '\r\n'
                        HTTP_header += 'Content-Length: ' + str(file_size) + '\r\n\r\n'
                        client_socket.send(HTTP_header.encode() + file_content)
                else:
                    connection_info = 'close'
                    HTTP_header = 'HTTP/1.1 404 Not Found\r\n'
                    HTTP_header += 'Connection: ' + connection_info + '\r\n'
                    client_socket.send(HTTP_header.encode())

            if connection_info == 'keep-alive':
                continue
            elif connection_info == 'close':
                break

        except socket.timeout:
            break
    client_socket.close()
