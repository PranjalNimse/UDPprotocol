#!/usr/bin/python

import sys
import Segment
import socket
import myUDP

# Receive segments from the sender
def receive(client, filename):
    # Open the file for writing
    try:
        file = open(filename, 'wb')
    except IOError:
        print('Unable to open', filename)
        return
    
    expected_num = 0
    while True:
        # Get the next packet from the sender
        segment, addr = myUDP.recv(client)
        if not segment:
            break
        seq_num, data = Segment.disintegrate_seg(segment)
        print('Received segment: ', seq_num)
        
        # Send back an ACK
        if seq_num == expected_num:
            file.write(data)
            print('Received expected segment')
            print('Sending ACK', expected_num)
            segment = Segment.create_seg(expected_num)
            myUDP.send(segment, client, addr)
            expected_num += 1
            
        else:
            print('Sending ACK', expected_num - 1)
            segment = Segment.create_seg(expected_num - 1)

            myUDP.send(segment, client, addr)

    file.close()

# Main function
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Required cmd arguments are missing')
        exit()
    
    listen_port_num = sys.argv[1]
    window_size = sys.argv[2]
    output_file = sys.argv[3]
        
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # listening port number should be same as the one in server's receiver address port (here, 8080)
    client.bind(('localhost', int(listen_port_num))) 

    filename = sys.argv[3]
    receive(client, filename)
    client.close()