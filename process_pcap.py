import pandas as pd
from scapy.all import rdpcap
from scapy.layers.inet import IP, TCP, UDP
import numpy as np
import time
import os

def extract_features(pcap_file):
    packets = rdpcap(pcap_file)
    data = []

    for packet in packets:
        try:
            ts = packet.time
            ip_layer = packet[IP]
            src = ip_layer.src
            dst = ip_layer.dst
            protocol = ip_layer.proto
            header_length = ip_layer.ihl * 4
            size = len(ip_layer)

            flags = 0
            if protocol == 6:  # TCP
                tcp = packet[TCP]
                flags = tcp.flags
            elif protocol == 17:  # UDP
                udp = packet[UDP]

            row = {
                'Timestamp': ts,
                'Source IP': src,
                'Destination IP': dst,
                'Protocol': protocol,
                'Header Length': header_length,
                'Size': size,
                'Flags': flags,
            }
            data.append(row)
        except Exception as e:
            print(f"Error processing packet: {e}")

    df = pd.DataFrame(data)
    return df

def calculate_derived_features(df):
    df['flow_duration'] = df['Timestamp'].diff().fillna(0)
    df['Rate'] = df['Size'] / df['flow_duration']
    df['Srate'] = df.groupby('Source IP')['Size'].transform(lambda x: x / df['flow_duration'])
    df['Drate'] = df.groupby('Destination IP')['Size'].transform(lambda x: x / df['flow_duration'])
    df['Flags'] = df['Flags'].astype(str)
    df['IAT'] = df['Timestamp'].diff().fillna(0)
    df['Number'] = df.groupby(['Source IP', 'Destination IP']).cumcount() + 1
    df['Magnitude'] = df['Size'] * df['Rate']
    df['Radius'] = (df['Size'] ** 2 + df['Rate'] ** 2) ** 0.5
    df['Covariance'] = df['Size'].rolling(window=2).cov()
    df['Variance'] = df['Size'].rolling(window=2).var()
    df['Weight'] = df['Size'] * df['Number']

    return df

def main():
    pcap_file = '/mnt/pcap/h1-eth0.pcap'
    output_csv = '/mnt/pcap/processed_traffic.csv'

    while True:
        if os.path.exists(pcap_file):
            try:
                df = extract_features(pcap_file)
                if not df.empty:
                    df = calculate_derived_features(df)
                    df.to_csv(output_csv, index=False)
                    print(f'Processed {pcap_file} and updated {output_csv}')
                else:
                    print(f'No valid data extracted from {pcap_file}')
            except Exception as e:
                print(f'Error processing {pcap_file}: {e}')
        else:
            print(f'{pcap_file} not found. Waiting...')

        time.sleep(10)

if __name__ == '__main__':
    main()
