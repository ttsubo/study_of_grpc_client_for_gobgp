import gobgp_pb2
import sys
import signal
import time
import os
from threading import Thread
from grpc.beta import implementations

_TIMEOUT_SECONDS = 1000

def run(gobgpd_addr, neighbor_addr):
    channel = implementations.insecure_channel(gobgpd_addr, 50051)
    with gobgp_pb2.beta_create_GobgpApi_stub(channel) as stub:
        peers = stub.MonitorPeerState(gobgp_pb2.Arguments(name=neighbor_addr), _TIMEOUT_SECONDS)

        if peers:
            def receive_signal(signum, stack):
                print('signal received:%d' % signum)
                peers.cancel()
                print('stream canceled')

            print('signal handler registered')

            for peer in peers:
                print("  BGP.info.bgp_state :%s" % ( peer.info.bgp_state))

def receive_signal(signum, stack):
    print('signal received:%d' % signum)
    print('exit')
    os._exit(0)

if __name__ == '__main__':
    gobgp = sys.argv[1]
    neighbor = sys.argv[2]

    signal.signal(signal.SIGINT, receive_signal)

    t = Thread(target=run, args=(gobgp, neighbor))
    t.daemon = True
    t.start()

    # sleep 1 sec forever to keep main thread alive
    while True:
        time.sleep(1)
