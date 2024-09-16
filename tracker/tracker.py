import grpc
import tracker_pb2
import tracker_pb2_grpc
from concurrent import futures

PORT = 50050

class TrackerServiceServicer(tracker_pb2_grpc.TrackerServiceServicer):
    info: dict[int, list[str]]

    def __init__(self) -> None:
        self.info = {}
        self.rr_index = {}

    def RegisterPeer(self, request, context):
        peer_address = request.peer_address
        file_info = request.file_info
        print(request.file_info)
        for file in file_info:
            for piece in file.pieces:
                number = piece.number
                if number not in self.info:
                    self.info[number] = []
                    self.rr_index[number] = 0
                self.info[number].append(peer_address)
        print(self.info)
        return tracker_pb2.RegisterPeerResponse(success=True)
    
    def DeregisterPeer(self, request, context):
        peer_address = request.peer_address
        file_info = request.file_info
        print(f"Deregistering peer: {peer_address}")

        for file in file_info:
            for piece in file.pieces:
                number = piece.number
                if number not in self.info or peer_address not in self.info[number]: continue
                self.info[number].remove(peer_address)
                self.rr_index[number].remove(peer_address)
                print(f"Removed {peer_address} from piece {number}")

                if self.info[number]: continue
                del self.info[number]
                del self.rr_index[number]
                print(f"No peers left for piece {number}, removed from tracker")

        print(self.info)
        return tracker_pb2.RegisterPeerResponse(success=True)

    def GetFilePieces(self, request, context):
        try:
            res = tracker_pb2.GetFilePiecesResponse() 
            
            for number, peers in self.info.items():
                curr_idx = self.rr_index[number]
                sel_peer = peers[curr_idx]
                self.rr_index[number] = (curr_idx + 1) % len(peers)

                addresses = tracker_pb2.PeerAddresses()
                addresses.addresses.append(sel_peer)

                res.pieces[number].CopyFrom(addresses)
        except Exception as e:
            print(f"Error: {e}") 
        return res


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tracker_pb2_grpc.add_TrackerServiceServicer_to_server(TrackerServiceServicer(), server)
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()
    print(f'Tracker Started [PORT={PORT}]')
    server.wait_for_termination()

if __name__ == "__main__":
    serve()