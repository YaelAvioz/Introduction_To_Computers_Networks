import socket
import time
import sys

system_arguments = sys.argv[1:]
my_port = int(system_arguments[0])
father_ip = system_arguments[1]
father_port = int(system_arguments[2])
file_name = system_arguments[3]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', my_port))


def del_outdated_ttl():
    # opens, read, and closes file
    f = open(file_name, "r")
    lines = f.readlines()
    f.close()
    # Return the time in seconds since the epoch as a floating point number
    this_time = time.time()
    # opens file to write
    f = open(file_name, "w")
    for line in lines:
        splitted = line.split(',')
        # if it is a dynamic URL then chack TTL
        if len(splitted) == 4:
            if splitted[3].strip('\n').replace('.', '', 1).isdigit():
                ttl = float(splitted[3].strip('\n'))
                # if ttl has not passed yet, write the same line
                if this_time < ttl:
                    f.write(line)
        else:
            f.write(line)
    f.close()


# find url in file and return the line
# if url wasn't found return false
def search_web(url):
    f = open(file_name, "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        splitted = line.split(',')
        if splitted[0] == url:
            return line
    return False


# adds a new URL and it's TTL to the file
def add_line_to_file(line):
    # cursor points to the end of the file
    f = open(file_name, "a")
    if line.split(",")[2].strip('\n').isnumeric():
        ttl = float(line.split(",")[2].strip('\n'))
        del_time = time.time() + ttl
        line = line.strip('\n') + "," + str(del_time)+"\n"
        # append new line at
        f.write(line)
    f.close()


while True:
    # waiting for client
    data, addr = s.recvfrom(1024)
    # first delete all out dated dynamic URLs
    del_outdated_ttl()
    line = search_web(data.decode())
    # if url was not found in the function above
    if line is False:
        # act like a client and ask father server for url
        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if father_ip != -1 and father_port != -1:
            s2.sendto(data, (father_ip, father_port))
            data, addr1 = s2.recvfrom(1024)
            line = data.decode()
            add_line_to_file(line)
            line = line.split(',')[1]
        s2.close()
    else:
        if father_ip != -1 and father_port != -1:
            line = line.split(',')[1]

    s.sendto(str.encode(line), addr)
