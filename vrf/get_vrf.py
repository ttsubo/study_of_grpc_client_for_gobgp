import gobgp_pb2
import sys
from ryu.lib.packet.bgp import _RouteDistinguisher
from ryu.lib.packet.bgp import _ExtendedCommunity
from ryu.lib.packet.bgp import BGPTwoOctetAsSpecificExtendedCommunity
from grpc.beta import implementations

_TIMEOUT_SECONDS = 10

def run(gobgpd_addr):
    channel = implementations.insecure_channel(gobgpd_addr, 50051)
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:
        vrfs = stub.GetVrfs(gobgp_pb2.Arguments(), _TIMEOUT_SECONDS)
        for vrf in vrfs:
            print(" Vrf.name : %s" % ( vrf.name))
            routeDist = _RouteDistinguisher.parser(vrf.rd)
            if routeDist.type == 0:
                print(" Vrf.rd   : %s:%s" % ( routeDist.admin, routeDist.assigned))
            else:
                print(" Vrf.rd   : ???")

            import_rt = vrf.import_rt
            for import_route_target in import_rt:
                import_rt_tmp = _ExtendedCommunity.parse(import_route_target)
                import_rt = import_rt_tmp[0]

                if isinstance(import_rt, BGPTwoOctetAsSpecificExtendedCommunity):
                    print(" Vrf.import_rt   : %s:%s" % ( import_rt.as_number, import_rt.local_administrator))
                else:
                    print(" Vrf.import_rt   : ???")

            export_rt = vrf.export_rt
            for export_route_target in export_rt:
                export_rt_tmp = _ExtendedCommunity.parse(export_route_target)
                export_rt = export_rt_tmp[0]

                if isinstance(export_rt, BGPTwoOctetAsSpecificExtendedCommunity):
                    print(" Vrf.export_rt   : %s:%s" % ( export_rt.as_number, export_rt.local_administrator))
                else:
                    print(" Vrf.export_rt   : ???")
            print "----------------------------"



if __name__ == '__main__':
    gobgp = sys.argv[1]
    run(gobgp)
