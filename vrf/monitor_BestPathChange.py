import gobgp_pb2
import sys
import signal
import time
import os
from threading import Thread
from ryu.lib.packet.bgp import LabelledVPNIPAddrPrefix
from ryu.lib.packet.bgp import _PathAttribute
from ryu.lib.packet.bgp import BGPPathAttributeMpReachNLRI
from ryu.lib.packet.bgp import BGPPathAttributeOrigin
from ryu.lib.packet.bgp import BGPPathAttributeAsPath
from ryu.lib.packet.bgp import BGPPathAttributeMultiExitDisc
from ryu.lib.packet.bgp import BGPPathAttributeExtendedCommunities
from ryu.lib.packet.bgp import BGPTwoOctetAsSpecificExtendedCommunity
from grpc.beta import implementations

_TIMEOUT_SECONDS = 1000

AFI_IP = 1
SAFI_UNICAST = 1
SAFI_MPLS_VPN = 128
RF_IPv4_UC = AFI_IP<<16 | SAFI_UNICAST
RF_IPv4_VPN = AFI_IP<<16 | SAFI_MPLS_VPN

def run(gobgpd_addr, routefamily):
    channel = implementations.insecure_channel(gobgpd_addr, 50051)
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:

        if routefamily:
            ribs = stub.MonitorBestChanged(gobgp_pb2.Arguments(family=routefamily), _TIMEOUT_SECONDS)
        else:
            ribs = stub.MonitorBestChanged(gobgp_pb2.Arguments(), _TIMEOUT_SECONDS)

        for rib in ribs:
            paths_target = rib.paths
            for path_target in paths_target:
                for pattr in path_target.pattrs:
                    path_attr = _PathAttribute.parser(pattr)
                    if isinstance(path_attr[0], BGPPathAttributeOrigin):
                        print (" Rib.origin     : %s" % path_attr[0].value)
                    elif isinstance(path_attr[0], BGPPathAttributeAsPath):
                        if path_attr[0].type == 2:
                            print(" Rib.aspath     : %s" % path_attr[0].value)
                        else:
                            print(" Rib.aspath     : ???")
                    elif isinstance(path_attr[0], BGPPathAttributeMultiExitDisc):
                        print (" Rib.med        : %s" % path_attr[0].value)
                    elif isinstance(path_attr[0], BGPPathAttributeExtendedCommunities):
                        for community in path_attr[0].communities:
                            if isinstance(community, BGPTwoOctetAsSpecificExtendedCommunity):
                                print(" Rib.community  : %s:%s" % ( community.as_number,
                                                                    community.local_administrator))
                            else:
                                print(" Rib.community  : ???")
                    elif isinstance(path_attr[0], BGPPathAttributeMpReachNLRI):
                        print (" Rib.prefix     : %s" % path_attr[0].nlri[0].prefix)
                        print (" Rib.route_dist : %s" % path_attr[0].nlri[0].route_dist)
                        print (" Rib.label_list : %s" % path_attr[0].nlri[0].label_list)
                        print (" Rib.nexthop    : %s" % path_attr[0].next_hop)
  

                print (" Rib.is_withdraw : %s" % path_target.is_withdraw)
                print (" Rib.best       : %s" % path_target.best)
                print "----------------------------"


def receive_signal(signum, stack):
    print('signal received:%d' % signum)
    print('exit')
    os._exit(0)

if __name__ == '__main__':
    gobgp = sys.argv[1]
    rf = sys.argv[2]
    if rf == "ipv4":
        routefamily = RF_IPv4_UC 
    elif rf == "vpnv4":
        routefamily = RF_IPv4_VPN
    elif rf == "all":
        routefamily = None
    else:
        exit(1)

    signal.signal(signal.SIGINT, receive_signal)

    t = Thread(target=run, args=(gobgp, routefamily))
    t.daemon = True
    t.start()

    # sleep 1 sec forever to keep main thread alive
    while True:
        time.sleep(1)


