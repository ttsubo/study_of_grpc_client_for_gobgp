import gobgp_pb2
import sys
from ryu.lib.packet.bgp import BGPTwoOctetAsRD
from ryu.lib.packet.bgp import BGPTwoOctetAsSpecificExtendedCommunity
from ryu.lib.packet.bgp import _RouteDistinguisher
from ryu.lib.packet.bgp import _ExtendedCommunity


_TIMEOUT_SECONDS = 10
Operation_ADD = 0

def run(gobgpd_addr, vrf_name, route_dist, import_rt, export_rt):
    with gobgp_pb2.early_adopter_create_GobgpApi_stub(gobgpd_addr, 8080) as stub:
        bin_rd = str_to_bin_for_rd(route_dist)
        import_rts = []
        bin_import_rt = str_to_bin_for_rt(import_rt)
        import_rts.append(str(bin_import_rt))

        export_rts = []
        bin_export_rt = str_to_bin_for_rt(export_rt)
        export_rts.append(str(bin_export_rt))

        vrf = {}
        vrf['name'] = vrf_name
        vrf['rd'] = str(bin_rd)
        vrf['import_rt'] = import_rts
        vrf['export_rt'] = export_rts


        ret = stub.ModVrf(gobgp_pb2.ModVrfArguments(operation=Operation_ADD, vrf=vrf), _TIMEOUT_SECONDS)
        if ret.code == 0:
            print "Success!"
        else:
            print "Error!"


def str_to_bin_for_rd(route_dist):
        rd = route_dist.split(":")
        admin = int(rd[0])
        assigned = int(rd[1])
        rd_tmp = BGPTwoOctetAsRD(admin=admin, assigned=assigned)
        bin_rd = rd_tmp.serialize()
        return bin_rd

def str_to_bin_for_rt(route_target):
        rt = route_target.split(":")
        as_number = int(rt[0])
        local_administrator = int(rt[1])
        rt_tmp = BGPTwoOctetAsSpecificExtendedCommunity(subtype=2, as_number=as_number, local_administrator=local_administrator)
        bin_rt = rt_tmp.serialize()
        return bin_rt



if __name__ == '__main__':
    gobgp = sys.argv[1]
    vrf_name = sys.argv[2]
    route_dist = sys.argv[3]
    import_rt = sys.argv[4]
    export_rt = sys.argv[5]
    run(gobgp, vrf_name, route_dist, import_rt, export_rt)
