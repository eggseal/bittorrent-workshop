import grpc
import tracker_pb2
import tracker_pb2_grpc
from concurrent import futures

PORT = 50050

class TrackerServiceServicer(tracker_pb2_grpc.TrackerServiceServicer):
    info: dict[int, list[str]]

    def __init__(self) -> None:
        self.info = {}

    def RegisterPeer(self, request, context):
        peer_address = request.peer_address
        file_info = request.file_info
        for piece in file_info.pieces:
            number = piece.number
            if number not in self.info: self.info[number] = []
            self.info[number].append(peer_address)
        return tracker_pb2.RegisterPeerResponse(success=True)
    
    def GetFilePieces(self, request, context):
        res = tracker_pb2.GetFilePiecesResponse()
        for number, peers in self.info.items():
            for peer in peers:
                res.pieces[number] = peer
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