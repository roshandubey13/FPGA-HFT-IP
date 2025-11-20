import struct
# Helper to pack 32-bit unsigned in big-endian
def pack_u32_be(x):
 return struct.pack('>I', x & 0xFFFFFFFF)
def send_market_packet(self, symbol_id, price_q16_16, volume_u32):
 """
 symbol_id: int 0..255
 price_q16_16: int 32-bit unsigned representing Q16.16 fixed point
 volume_u32: int 32-bit unsigned
 """
 # Base packet template copied/derived from your earlier packet
 # Keep the same header bytes scenario as your working packet, but replace payload
portion.
 packet = bytearray(b"\xe8\x6a\x64\xe7\xe8\x30\xec\x08\x6b\x0d\xfc\x31\x08\x00"
 b"\x45\x00\x00\x41\x00\x00\x00\x00\x40\x11\x65\xb3"
 b"\x0a\x00\x00\x0a\x0a\x00\x00\xf0" # IP src/dst placeholders
continue...
 b"\xff\xff\xff\xff\x00\x2d\x00\x00") # UDP header placeholders
 # The exact header lengths in the original were longer; safe approach:
 # Rebuild minimal Ethernet(14) + IPv4 + UDP headers to avoid index-matching errors.
 # Build Ethernet header
 eth_dst = self.fpga_mac # 6 bytes
 eth_src = self.my_mac # 6 bytes
 eth_type = b'\x08\x00' # IPv4
 eth_hdr = eth_dst + eth_src + eth_type
 # IPv4 header (20 bytes) - minimal fields:
 ver_ihl = b'\x45' # v4 + IHL=5
 dscp_ecn = b'\x00'
 total_length = 20 + 8 + 9 # IP header + UDP header + payload (9 bytes)
 total_length_be = struct.pack('>H', total_length)
 identification = b'\x00\x00'
 flags_frag = b'\x00\x00'
 ttl = b'\x40'
 proto = b'\x11' # UDP
 checksum = b'\x00\x00' # kernel/sender might not validate IP checksum but ok for
demo
 src_ip = bytes(self.my_ip) # 4 bytes
 dst_ip = bytes(self.fpga_ip) # 4 bytes
 ip_hdr = ver_ihl + dscp_ecn + total_length_be + identification + flags_frag + ttl +
proto + checksum + src_ip + dst_ip
 # UDP header (8 bytes). We'll set ports to something static: src=0x0035 (53),
dst=0x002d (45) like original
 src_port = struct.pack('>H', 53)
 dst_port = struct.pack('>H', 45)
 udp_length = struct.pack('>H', 8 + 9) # UDP header + payload
 udp_checksum = b'\x00\x00' # optional; many local demos set 0
 udp_hdr = src_port + dst_port + udp_length + udp_checksum
 # Payload construction (9 bytes)
 payload = bytearray()
 payload.append(symbol_id & 0xFF) # byte 0
 payload += pack_u32_be(price_q16_16) # bytes 1..4
 payload += pack_u32_be(volume_u32) # bytes 5..8
 # Final packet = eth_hdr + ip_hdr + udp_hdr + payload
 packet = eth_hdr + ip_hdr + udp_hdr + payload
 # bind/send
 self.s_inst.send(packet)
