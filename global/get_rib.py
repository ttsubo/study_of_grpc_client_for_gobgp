import gobgp_pb2
import sys
from ryu.lib.packet.bgp import LabelledVPNIPAddrPrefix
from ryu.lib.packet.bgp import _PathAttribute
from ryu.lib.packet.bgp import BGPPathAttributeMpReachNLRI
from ryu.lib.packet.bgp import BGPPathAttributeOrigin
from ryu.lib.packet.bgp import BGPPathAttributeAsPath
from ryu.lib.packet.bgp import BGPPathAttributeMultiExitDisc
from ryu.lib.packet.bgp import BGPPathAttributeExtendedCommunities
from ryu.lib.packet.bgp import BGPTwoOctetAsSpecificExtendedCommunity
from grpc.beta import implementations

_TIMEOUT_SECONDS = 10
Resource_VRF = 10
Resource_GLOBAL  = 0

AFI_IP = 1
SAFI_UNICAST = 1
RF_IPv4_UC = AFI_IP<<16 | SAFI_UNICAST

def run(gobgpd_addr):
    channel = implementations.insecure_channel(gobgpd_addr, 50051)
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:
        rib = stub.GetRib(gobgp_pb2.Table(type=Resource_GLOBAL, family=RF_IPv4_UC), _TIMEOUT_SECONDS)

        destinations_target = rib.destinations
        for destination_target in destinations_target:
            print (" Rib.prefix     : %s" % destination_target.prefix)


if __name__ == '__main__':
    gobgp = sys.argv[1]
    run(gobgp)


