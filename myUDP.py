# My transport protocol with different implementation
import random

RANDOM = 4

# Send a packet across to the receiver/sender
# Lose a random packet implementation
def send(segment, sock, addr):
    if random.randint(0, RANDOM) > 0:
        sock.sendto(segment, addr)
    return

# Receive a packet from the receiver/sender
def recv(sock):
    segment, addr = sock.recvfrom(1024)
    return segment, addr
