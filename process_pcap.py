import pandas as pd
from scapy.all import PcapReader
from scapy.layers.inet import IP, TCP, UDP
import numpy as np
import time
import os

def extract_features(pcap_reader):
    data = []

    for packet in pcap_reader:
        if packet.haslayer(IP):
            try:
                ts = packet.time
                ip_layer = packet[IP]
                src = ip_layer.src
                dst = ip_layer.dst
                protocol = ip_layer.proto
                header_length = ip_layer.ihl * 4
                size = len(ip_layer)

                flags = 0
                if packet.haslayer(TCP):
                    tcp_layer = packet[TCP]
                    flags = tcp_layer.flags

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
        elif packet.haslayer(TCP):
            ts = packet.time
            tcp_layer = packet[TCP]
            flags = tcp_layer.flags
            src = dst = protocol = header_length = size = None

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
        elif packet.haslayer(UDP):
            ts = packet.time
            udp_layer = packet[UDP]
            src = dst = protocol = header_length = size = flags = None

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

    df = pd.DataFrame(data)
    return df

def calculate_derived_features(df):
    epsilon = 1e-9  # Small value to prevent division by zero

    df['flow_duration'] = df['Timestamp'].diff().fillna(0).astype(float)
    df['Rate'] = df['Size'] / (df['flow_duration'] + epsilon)
    df['Srate'] = df.groupby('Source IP')['Size'].transform(lambda x: x / (df['flow_duration'] + epsilon))
    df['Drate'] = df.groupby('Destination IP')['Size'].transform(lambda x: x / (df['flow_duration'] + epsilon))
    df['Flags'] = df['Flags'].astype(str)
    df['IAT'] = df['Timestamp'].diff().fillna(0).astype(float)
    df['Number'] = df.groupby(['Source IP', 'Destination IP']).cumcount() + 1
    df['Magnitude'] = df['Size'] * df['Rate']
    df['Radius'] = (df['Size'] ** 2 + df['Rate'] ** 2) ** 0.5
    df['Covariance'] = df['Size'].rolling(window=2).cov()
    df['Variance'] = df['Size'].rolling(window=2).var()
    df['Weight'] = df['Size'] * df['Number']

    return df

def process_pcap_in_batches(pcap_file, output_csv, batch_size=10000):
    reader = PcapReader(pcap_file)
    batch_data = []

    while True:
        batch = []
        for _ in range(batch_size):
            packet = reader.read_packet()
            if packet is None:
                break
            batch.append(packet)

        if not batch:
            break

        df = extract_features(batch)
        if not df.empty:
            df = calculate_derived_features(df)
            batch_data.append(df)

        if len(batch) < batch_size:
            break

    if batch_data:
        final_df = pd.concat(batch_data, ignore_index=True)
        final_df.to_csv(output_csv, index=False)
        print(f'Processed {pcap_file} and updated {output_csv}')
    else:
        print(f'No valid data extracted from {pcap_file}')

def main():
    pcap_file = '/mnt/pcap/h1-eth0.pcap'
    output_csv = '/mnt/pcap/processed_traffic.csv'

    while True:
        if os.path.exists(pcap_file):
            try:
                process_pcap_in_batches(pcap_file, output_csv)
            except Exception as e:
                print(f'Error processing {pcap_file}: {e}')
        else:
            print(f'{pcap_file} not found. Waiting...')

        time.sleep(10)

if __name__ == '__main__':
    main()
