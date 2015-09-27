import gobgp_pb2
import sys
from netaddr.ip import IPNetwork
from ryu.lib.packet.bgp import BGPPathAttributeOrigin
from ryu.lib.packet.bgp import IPAddrPrefix
from ryu.lib.packet.bgp import BGPPathAttributeNextHop


_TIMEOUT_SECONDS = 10
Resource_VRF = 10

def run(gobgpd_addr, vrf_name, prefix, nexthop):
    with gobgp_pb2.early_adopter_create_GobgpApi_stub(gobgpd_addr, 8080) as stub:

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

        paths = []
        paths.append(path)

        args = []
        args.append(gobgp_pb2.ModPathArguments(resource=Resource_VRF, name=vrf_name, paths=paths))
        ret = stub.ModPath(args, _TIMEOUT_SECONDS)

        if ret.code == 0:
            print "Success!"
        else:
            print "Error!"


if __name__ == '__main__':
    gobgp = sys.argv[1]
    vrf_name = sys.argv[2]
    prefix = sys.argv[3]
    nexthop = sys.argv[4]
    run(gobgp, vrf_name, prefix, nexthop)
