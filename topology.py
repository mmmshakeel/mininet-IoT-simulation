from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import os

def custom_topology():
    net = Mininet(controller=Controller, link=TCLink)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')

    info('*** Adding switch\n')
    s1 = net.addSwitch('s1')

    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)

    info('*** Starting network\n')
    net.start()

    # Get IP addresses
    h1_ip = h1.IP()
    h2_ip = h2.IP()
    h3_ip = h3.IP()
    h4_ip = h4.IP()
    h5_ip = h5.IP()

    # Print IP addresses
    info(f'*** Host h1 IP: {h1_ip}\n')
    info(f'*** Host h2 IP: {h2_ip}\n')
    info(f'*** Host h3 IP: {h3_ip}\n')
    info(f'*** Host h4 IP: {h4_ip}\n')
    info(f'*** Host h5 IP: {h5_ip}\n')

    info('*** Starting tcpdump on host h1\n')
    h1.cmd('tcpdump -i h1-eth0 -w /mnt/pcap/h1-eth0.pcap &')

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    custom_topology()
