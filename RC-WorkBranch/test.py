import socket

# baddr = 'dc:71:96:4d:1b:5f' 
baddr = 'a4:75:b9:d1:97:29' # Association Endpoint address for S23
channel = 4
with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
    s.connect((baddr,channel))
    # s_sock = server_sock.accept()
    # print ("Accepted connection from "+address)

    data = s.recv(1024)
    print ("received [%s]" % data)
