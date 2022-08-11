import sys
import socket
import threading

from pip import main

HEX_FILTER= ''.join(
    [(len(repr(chr(i))) == 3 ) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i: i + length])

        printable = word.translate(HEX_FILTER)
        print(f"Printable: {printable}")

        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        print(f'Hexa: {hexa}')

        hexwidth = length * 3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
    

if __name__ == "__main__":
    print(HEX_FILTER)

    hexdump('python rocks\n and proxies roll\n')