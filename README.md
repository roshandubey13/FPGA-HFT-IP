# FPGA-Low Latency Market Compute

## Project Overview  
This repository contains a learning project designed to implement a simple
**FPGA-based system for real-time market-data feed handling**.
The project receives simulated market-data packets [`symbol` | `price` | `volume`] from a Python-based feed, parses them entirely in hardware, and outputs threshold-based BUY/SELL triggers via LEDs.

This design demonstrates **low-latency, deterministic data processing** and **FPGA pipeline concepts** relevant to high-performance trading systems.  

---

## Key Features  
- **Python-based feed simulation** generating market data [`symbol` | `price` | `volume`].
- **Hardware parser** implemented in Verilog to decode and process incoming feed data.
- **Threshold-based decision logic** producing BUY/SELL triggers mapped to LEDs or GPIOs.
- Achieved **faster market data parsing and trade signal generation** than a CPU-based software implementation.
- Demonstrated **sub-microsecond deterministic latency** and **low jitter** due to OS-independent FPGA execution.
- Modular and parameterized Verilog design for extensibility.
- Includes clean testbenches for parser and decision logic simulation.

---

## Module Descriptions  

### Python Feed Simulator  
A simple Python script (`market_feed_simulator.py`) generates simulated market-data packets with fields: `symbol`, `price`, and `volume`.  
**Usage:** Configure symbols, price ranges, volume, and send rate to emulate real-time market updates.  
**Purpose:** Provides a software baseline and feed input to the FPGA through the UDP socket.  

### Market Data Parser (Verilog)  
Implements a hardware AXI component to receive and decode data fields from the incoming AXI feed which intern comes from RMII from the PHY to AXi converter in 2bits per clk.  
- AXi stream is inputes as (`Tdata[7:0] `, `tvalid`, `tready`, `tlast`).
- Parses structured packet fields (`symbol`, `price`, `volume`).
- FSM to encoded  (`W_h`,`R_SYMBOL`,`R_PRICE`,`R_VOL`, `R_SIGNAL`,).    
- Outputs parsed fields for real-time decision logic to LED0-BUY & LED1-SELL.  

### Decision Logic (Verilog)  
Implements a **threshold-based trading rule**, with prestoreed values:  
- If `price < THRESHOLD` → assert `BUY_TRIGGER`.  
- If `price > THRESHOLD` → assert `SELL_TRIGGER`.  
Trigger outputs are mapped to LEDs later on can be packed back to Ethernet frame to view on PC.  
**Latency Measurement:** Internal counters or timestamps record the delay between data arrival and trigger assertion.  

---

## Usage Notes  
1. Clone the repository:  
   ```bash
   git clone https://github.com/roshandubey13/FPGA-HFT-IP.git
