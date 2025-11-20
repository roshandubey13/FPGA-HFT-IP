import socket
import struct

# -----------------------------
# Configuration
# -----------------------------
INTERFACE = "enp2s0"

MY_IP    = [10, 0, 0, 10]
FPGA_IP  = [10, 0, 0, 240]

MY_MAC   = b"\xe8\x6a\x64\xe7\xe8\x29"
FPGA_MAC = b"\xe8\x6a\x64\xe7\xe8\x30"

SRC_PORT = 53      # arbitrary, but must match FPGA core
DST_PORT = 45      # MUST match UDP port configured in the FPGA UDP core


# -----------------------------
# Helper: pack 32-bit big-endian
# -----------------------------
def u32_be(x):
    """Pack 32-bit unsigned integer into big-endian bytes."""
    return struct.pack(">I", x & 0xFFFFFFFF)


# -----------------------------
# Main function to send a 9-byte market packet
# -----------------------------
def send_market_packet(symbol, price_q16_16, volume_u32):
    """
    Send one market-style packet:
        Byte 0: symbol_id (0–255)
        Byte 1–4: price (Q16.16, big-endian)
        Byte 5–8: volume (u32 big-endian)
    """

    # ----------------------------------------------
    # Build Ethernet header
    # ----------------------------------------------
    eth_dst  = FPGA_MAC
    eth_src  = MY_MAC
    eth_type = b"\x08\x00"  # IPv4
    eth_hdr  = eth_dst + eth_src + eth_type

    # ----------------------------------------------
    # Build IPv4 header
    # ----------------------------------------------
    version_ihl = b"\x45"    # IPv4, IHL=5
    dscp_ecn    = b"\x00"

    total_length = 20 + 8 + 9       # IP header + UDP header + payload
    total_len_be = struct.pack(">H", total_length)

    identification = b"\x00\x00"
    flags_fragment = b"\x00\x00"
    ttl            = b"\x40"       # 64
    protocol       = b"\x11"       # UDP
    checksum       = b"\x00\x00"   # not computing checksum; okay for local link

    src_ip = bytes(MY_IP)
    dst_ip = bytes(FPGA_IP)

    ip_hdr = (
        version_ihl + dscp_ecn + total_len_be +
        identification + flags_fragment +
        ttl + protocol + checksum +
        src_ip + dst_ip
    )

    # ----------------------------------------------
    # Build UDP header
    # ----------------------------------------------
    udp_src = struct.pack(">H", SRC_PORT)
    udp_dst = struct.pack(">H", DST_PORT)
    udp_len = struct.pack(">H", 8 + 9)   # header + payload
    udp_chk = b"\x00\x00"                # no checksum

    udp_hdr = udp_src + udp_dst + udp_len + udp_chk

    # ----------------------------------------------
    # Build payload (9 bytes)
    # ----------------------------------------------
    payload  = bytearray()
    payload.append(symbol & 0xFF)
    payload += u32_be(price_q16_16)
    payload += u32_be(volume_u32)

    # Final Ethernet frame
    frame = eth_hdr + ip_hdr + udp_hdr + payload

    # ----------------------------------------------
    # Send frame using AF_PACKET
    # ----------------------------------------------
    ETH_P_ALL = 3
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
    s.bind((INTERFACE, 0))
    s.send(frame)

    print(f"Sent: symbol={symbol}, price={price_q16_16}, volume={volume_u32}")


# -----------------------------
# Example usage (stand-alone)
# -----------------------------
if __name__ == "__main__":
    # Example:
    symbol = 5

    price_float = 12.50
    price_q16 = int(price_float * (1 << 16))     # convert float → Q16.16

    volume = 100

    send_market_packet(symbol, price_q16, volume)
