#!/usr/bin/python

import sys
import socket
import Segment
import myUDP
import _thread
import time
from timer import Timer

global window_size

# Shared resources for threads we create to run send and receive functionality simultaneously
sendTime = Timer(1)
base = 0
mutex = _thread.allocate_lock()

# Set the sliding window size
def set_window_size(num_segments, win_size):
    return min(int(win_size), num_segments - base)

def send(window_size, filename):

    # Add all segment to collection
    segments = []
    seq_num = 0

    # Open the file
    try:
        file = open(filename, 'rb')
    except IOError:
        print('Error while opening file: ', filename)
        return

    while True:
        # All DATA segments contain a payload with 512 bytes of data, except the last DATA segment of a transfer that can be shorter.
        data = file.read(512)
        if not data:
            break
        segments.append(Segment.create_seg(seq_num, data))
        seq_num += 1

    num_segments = len(segments)
    print('Total segments formed: ', num_segments)
    window_size = set_window_size(num_segments,window_size)
    next_to_send = 0
    base = 0

    _thread.start_new_thread(receive, (server,))

    while base < num_segments:
        mutex.acquire()
        # Send all the segments in the window
        while next_to_send < base + window_size:
            print('Sending segment', next_to_send)
            myUDP.send(segments[next_to_send], server, ('localhost', 8080))
            next_to_send += 1

        # Start the timer
        if not sendTime.running():
            print('Start timer')
            sendTime.start()

        # Wait until a timer goes off or we receive an ACK
        while sendTime.running() and not sendTime.timeout():
            mutex.release()
            print('Waiting')
            time.sleep(1)
            mutex.acquire()

        if sendTime.timeout():
            
            print('Timeout')
            sendTime.stop();
            next_to_send = base
        else:
            print('Sliding the window')
            window_size = set_window_size(num_segments,window_size)
        mutex.release()

    # Send empty packet as sentinel
    myUDP.send(Segment.create_empty_seg(), server, ('localhost', 8080))
    file.close()
    
# Receiving thread
def receive(server):
    global mutex
    global base
    global sendTime

    while True:
        segment, _ = myUDP.recv(server);
        ack, _ = Segment.disintegrate_seg(segment);

        print('Received ACK number ', ack)
        if (ack >= base):
            mutex.acquire()
            base = ack + 1
            sendTime.stop()
            mutex.release()


# Main function
if __name__ == '__main__':
    global window_size

    if len(sys.argv) != 5:
        print('Required cmd arguments are missing')
        exit()

    dest_DNS_name = sys.argv[1]
    dest_port_num = sys.argv[2]
    window_size = sys.argv[3]
    input_file = sys.argv[4]

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (dest_DNS_name, int (dest_port_num))
    server.bind(addr)

    send(window_size, input_file)

    server.close()