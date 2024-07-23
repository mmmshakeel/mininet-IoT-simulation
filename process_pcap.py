import pandas as pd
from scapy.all import rdpcap
from scapy.layers.inet import IP, TCP, UDP
import numpy as np

def extract_features(pcap_file):
    packets = rdpcap(pcap_file)
    data = []

    for packet in packets:
        if packet.haslayer(IP):
            row = {
                'flow_duration': packet.time,
                'Header_Length': len(packet[IP]),
                'Protocol Type': packet[IP].proto,
                'Duration': packet.time,  # Simplified
                'Rate': len(packet) / packet.time if packet.time > 0 else 0,
                'Srate': len(packet) / packet.time if packet.time > 0 else 0,
                'Drate': 0,  # To be calculated
                'fin_flag_number': packet[TCP].flags.F if packet.haslayer(TCP) else 0,
                'syn_flag_number': packet[TCP].flags.S if packet.haslayer(TCP) else 0,
                'rst_flag_number': packet[TCP].flags.R if packet.haslayer(TCP) else 0,
                'psh_flag_number': packet[TCP].flags.P if packet.haslayer(TCP) else 0,
                'ack_flag_number': packet[TCP].flags.A if packet.haslayer(TCP) else 0,
                'ece_flag_number': packet[TCP].flags.E if packet.haslayer(TCP) else 0,
                'cwr_flag_number': packet[TCP].flags.C if packet.haslayer(TCP) else 0,
                'Urg_flag_number': packet[TCP].flags.U if packet.haslayer(TCP) else 0,
                'Average Packet Size': len(packet) / packet.time if packet.time > 0 else 0,
                'Min Packet Length': len(packet),
                'Max Packet Length': len(packet),
                'Tot size': len(packet),
                'IAT': packet.time,  # Simplified
                'Number': 1,  # Count of packets
                'Magnitue': np.sqrt(len(packet)),  # Simplified
                'Radius': 0,  # Simplified
                'Covariance': 0,  # Simplified
                'Variance': np.var([len(packet)]),  # Simplified
                'Weight': len(packet),  # Simplified
                'label': 'Normal'  # Default label, to be updated based on attack
            }
            data.append(row)

    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    pcap_file = '/tmp/h1-eth0.pcap'
    df = extract_features(pcap_file)
    df.to_csv('/tmp/processed_traffic.csv', index=False)
