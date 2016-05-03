import gobgp_pb2
import sys
from netaddr.ip import IPNetwork
from ryu.lib.packet.bgp import BGPPathAttributeOrigin
from ryu.lib.packet.bgp import IPAddrPrefix
from ryu.lib.packet.bgp import BGPPathAttributeNextHop
from grpc.beta import implementations


_TIMEOUT_SECONDS = 10
Resource_VRF = 4

def run(gobgpd_addr, vrf_name, prefix, nexthop):
    channel = implementations.insecure_channel(gobgpd_addr, 50051)
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:

        subnet = IPNetwork(prefix)
        ipaddr = subnet.ip
        masklen = subnet.prefixlen

        nlri = IPAddrPrefix(addr=ipaddr, length=masklen)
        bin_nlri = nlri.serialize()

        nexthop = BGPPathAttributeNextHop(value=nexthop)
        bin_nexthop = nexthop.serialize()

        origin = BGPPathAttributeOrigin(value=2)
        bin_origin = origin.serialize()

        pattrs = []
        pattrs.append(str(bin_nexthop))
        pattrs.append(str(bin_origin))

        path = {}
        path['nlri'] = str(bin_nlri)
        path['pattrs'] = pattrs

        uuid = stub.ModPath(gobgp_pb2.ModPathArguments(resource=Resource_VRF, name=vrf_name, path=path), _TIMEOUT_SECONDS)

        if uuid:
            print "Success!"
        else:
            print "Error!"


if __name__ == '__main__':
    gobgp = sys.argv[1]
    vrf_name = sys.argv[2]
    prefix = sys.argv[3]
    nexthop = sys.argv[4]
    run(gobgp, vrf_name, prefix, nexthop)
