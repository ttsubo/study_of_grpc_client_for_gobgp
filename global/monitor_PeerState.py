import gobgp_pb2
import sys
import signal

_TIMEOUT_SECONDS = 1000

def run(gobgpd_addr, neighbor_addr):
    with gobgp_pb2.early_adopter_create_GobgpApi_stub(gobgpd_addr, 8080) as stub:
        peers = stub.MonitorPeerState(gobgp_pb2.Arguments(name=neighbor_addr), _TIMEOUT_SECONDS)

        if peers:
            def receive_signal(signum, stack):
                print('signal received:%d' % signum)
                peers.cancel()
                print('stream canceled')

            signal.signal(signal.SIGINT, receive_signal)
            print('signal handler registered')

            for peer in peers:
                print("  BGP.info.bgp_state :%s" % ( peer.info.bgp_state))


if __name__ == '__main__':
    gobgp = sys.argv[1]
    neighbor = sys.argv[2]
    run(gobgp, neighbor)
