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
        print(request.file_info)
        for file in file_info:
            for piece in file.pieces:
                number = piece.number
                if number not in self.info:
                    self.info[number] = []
                self.info[number].append(peer_address)
        print(self.info)
        return tracker_pb2.RegisterPeerResponse(success=True)
    
    def GetFilePieces(self, request, context):
        try:
            print("H")
            res = tracker_pb2.GetFilePiecesResponse()  # Create the response message
            print("H")
            
            for number, peers in self.info.items():
                addresses = tracker_pb2.PeerAddresses()  # Create a new PeerAddresses message
                
                # Use add() method to append each peer address
                for peer in peers:
                    print(peer)
                    addresses.addresses.append(peer)  # Correct way to add address to the repeated field

                res.pieces[number].CopyFrom(addresses)  # Assign to the map using CopyFrom
            print(res)  # Print the entire response for debugging
        except Exception as e:
            print(f"Error: {e}")  # Print any errors that occur
        return res  # Return the constructed response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tracker_pb2_grpc.add_TrackerServiceServicer_to_server(TrackerServiceServicer(), server)
    server.add_insecure_port(f'[::]:{PORT}')
    server.start()
    print(f'Tracker Started [PORT={PORT}]')
    server.wait_for_termination()

if __name__ == "__main__":
    serve()