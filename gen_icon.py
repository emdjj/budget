import struct, zlib

def create_png(width, height, color):
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            cx, cy = width//2, height//2
            r = min(width, height)//2 - 2
            dist = ((x-cx)**2 + (y-cy)**2) ** 0.5
            if dist < r:
                raw += bytes(color[:3])
            elif dist < r + 1:
                raw += bytes([100, 180, 255])
            else:
                raw += bytes([15, 15, 35])
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

with open('D:/budget/icon-192.png', 'wb') as f:
    f.write(create_png(192, 192, (79, 195, 247)))
with open('D:/budget/icon-512.png', 'wb') as f:
    f.write(create_png(512, 512, (79, 195, 247)))
print('PNG icons created')
