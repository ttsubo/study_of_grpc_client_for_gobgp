import gobgp_pb2
import sys
import signal
import time
import os
from threading import Thread
from ryu.lib.packet.bgp import IPAddrPrefix
from ryu.lib.packet.bgp import _PathAttribute
from ryu.lib.packet.bgp import BGPPathAttributeOrigin
from ryu.lib.packet.bgp import BGPPathAttributeAsPath
from ryu.lib.packet.bgp import BGPPathAttributeMultiExitDisc
from ryu.lib.packet.bgp import BGPPathAttributeNextHop
from ryu.lib.packet.bgp import BGPPathAttributeCommunities

_TIMEOUT_SECONDS = 1000

AFI_IP = 1
SAFI_UNICAST = 1
RF_IPv4_UC = AFI_IP<<16 | SAFI_UNICAST

def run(gobgpd_addr, routefamily):
    with gobgp_pb2.early_adopter_create_GobgpApi_stub(gobgpd_addr, 8080) as stub:

        ribs = stub.MonitorBestChanged(gobgp_pb2.Arguments(rf=routefamily),
                                                           _TIMEOUT_SECONDS)

        for rib in ribs:
            paths_target = rib.paths
            for path_target in paths_target:
                nlri = IPAddrPrefix.parser(path_target.nlri)
                print "----------------------------"
                print (" Rib.prefix     : %s" % nlri[0].prefix)
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
                    elif isinstance(path_attr[0], BGPPathAttributeNextHop):
                        print (" Rib.nexthop    : %s" % path_attr[0].value)
                    elif isinstance(path_attr[0], BGPPathAttributeCommunities):
                        for community in path_attr[0].communities:
                            print(" Rib.community  : %s" % community)

                print (" Rib.is_withdraw : %s" % path_target.is_withdraw)


def receive_signal(signum, stack):
    print('signal received:%d' % signum)
    print('exit')
    os._exit(0)

if __name__ == '__main__':
    gobgp = sys.argv[1]
    rf = sys.argv[2]
    if rf == "ipv4":
        routefamily = RF_IPv4_UC 
    else:
        exit(1)

    signal.signal(signal.SIGINT, receive_signal)

    t = Thread(target=run, args=(gobgp, routefamily))
    t.daemon = True
    t.start()

    # sleep 1 sec forever to keep main thread alive
    while True:
        time.sleep(1)


