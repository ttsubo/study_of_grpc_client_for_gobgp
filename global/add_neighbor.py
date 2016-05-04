import gobgp_pb2
import sys
from netaddr.ip import IPNetwork
from ryu.lib.packet.bgp import BGPPathAttributeOrigin
from ryu.lib.packet.bgp import IPAddrPrefix
from ryu.lib.packet.bgp import BGPPathAttributeNextHop
from grpc.beta import implementations


_TIMEOUT_SECONDS = 10
Operation_ADD = 0
PEER_TYPE_INTERNAL = 0
PEER_TYPE_EXTERNAL = 1

AFI_IP = 1
SAFI_UNICAST = 1
SAFI_MPLS_VPN = 128
RF_IPv4_UC = AFI_IP<<16 | SAFI_UNICAST
RF_IPv4_VPN = AFI_IP<<16 | SAFI_MPLS_VPN

def run(gobgpd_addr, neighbor_address, local_as, peer_as):
    channel = implementations.insecure_channel(gobgpd_addr, 50051)
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:

        conf = {}
        if local_as == peer_as:
            conf['peer_type'] = PEER_TYPE_INTERNAL
        else:
            conf['peer_type'] = PEER_TYPE_EXTERNAL

        conf['neighbor_address'] = neighbor_address
        conf['local_as'] = local_as
        conf['peer_as'] = peer_as

        families = []
        families.append(RF_IPv4_UC)

	

        peer = {}
        peer['conf'] = conf
	peer['families'] = families

        uuid = stub.ModNeighbor(gobgp_pb2.ModNeighborArguments(operation=Operation_ADD, peer=peer), _TIMEOUT_SECONDS)

        if uuid:
            print "Success!"
        else:
            print "Error!"


if __name__ == '__main__':
    gobgp = sys.argv[1]
    neighbor_address = sys.argv[2]
    local_as = int(sys.argv[3])
    peer_as = int(sys.argv[4])
    run(gobgp, neighbor_address, local_as, peer_as)
