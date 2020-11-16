import socket
import sys

system_arguments = sys.argv[1:]
father_ip = system_arguments[0]
father_port = int(system_arguments[1])

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
url = input()
while(True):
    s.sendto(url.encode(), (father_ip, father_port))
    data, addr = s.recvfrom(1024)
    print(str(data.decode()))
    url = input()
s.close()