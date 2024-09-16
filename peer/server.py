# ESTE NO FUNCIONA XD
import grpc
import json
from concurrent import futures
import tracker_pb2 
import tracker_pb2_grpc

PEER_NUMBER = 1  # Starts from 1
PEER_PORT = 50050 + PEER_NUMBER
TRACKER_ADDRESS = "localhost:50050"

def register_peer_with_tracker(peer_address, file_info):
    channel = grpc.insecure_channel(TRACKER_ADDRESS)
    stub = tracker_pb2_grpc.TrackerServiceStub(channel)

    # Convert the JSON file_info to protobuf messages
    file_info_messages = []
    for file_entry in file_info:
        print(f"Processing file entry: {file_entry}")
        
        # Ensure pieces are added as a list
        pieces = [
            tracker_pb2.FilePiece(number=piece['number'], hash=piece['hash'])
            for piece in file_entry['pieces']
        ]

        # Create the FileInfo message with the pieces list
        file_info_message = tracker_pb2.FileInfo(
            file_name=file_entry['file_name'], 
            total=file_entry['total'], 
            pieces=pieces
        )
        
        file_info_messages.append(file_info_message)
    
    register_request = tracker_pb2.RegisterPeerRequest(
        peer_address=peer_address,
        file_info=file_info_messages   
    )
    print(f"Registering peer with request: {register_request}")
    
    try:
        response = stub.RegisterPeer(register_request)
        if response.success:
            print(f"Successfully registered peer {peer_address} with tracker.")
            return True
        else:
            print(f"Failed to register peer {peer_address} with tracker.")
            return False
    except grpc.RpcError as e:
        print(f"gRPC error occurred: {e.code()} - {e.details()}")
        return False
    
def deregister_peer_with_tracker(peer_address, file_info):
    channel = grpc.insecure_channel(TRACKER_ADDRESS)
    stub = tracker_pb2_grpc.TrackerServiceStub(channel)

    # Convert the JSON file_info to protobuf messages
    file_info_messages = []
    for file_entry in file_info:
        print(f"Processing file entry for deregistration: {file_entry}")

        # Ensure pieces are added as a list
        pieces = [
            tracker_pb2.FilePiece(number=piece['number'], hash=piece['hash'])
            for piece in file_entry['pieces']
        ]

        # Create the FileInfo message with the pieces list
        file_info_message = tracker_pb2.FileInfo(
            file_name=file_entry['file_name'], 
            total=file_entry['total'], 
            pieces=pieces
        )

        file_info_messages.append(file_info_message)

    deregister_request = tracker_pb2.RegisterPeerRequest(
        peer_address=peer_address,
        file_info=file_info_messages
    )
    print(f"Deregistering peer with request: {deregister_request}")

    try:
        response = stub.DeregisterPeer(deregister_request)
        if response.success:
            print(f"Successfully deregistered peer {peer_address} from tracker.")
            return True
        else:
            print(f"Failed to deregister peer {peer_address} from tracker.")
            return False
    except grpc.RpcError as e:
        print(f"gRPC error occurred: {e.code()} - {e.details()}")
        return False


class PeerService(tracker_pb2_grpc.PeerServiceServicer):
    def __init__(self, file_pieces):
        self.file_pieces = file_pieces
    
    def HasPiece(self, request, context):
        file_name = request.file_name
        piece_number = request.piece_number
        
        # Check if the peer holds this piece
        has_piece = False
        for piece in self.file_pieces:
            if piece['file_name'] != file_name: continue
            for p in piece['pieces']:
                if p['number'] != piece_number: continue
                has_piece = True
                break
        return tracker_pb2.PieceResponse(has_piece=has_piece)

def serve_peer_server(file_pieces):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    peer_service = PeerService(file_pieces)
    tracker_pb2_grpc.add_PeerServiceServicer_to_server(peer_service, server)
    
    # Bind the server to the peer port
    server.add_insecure_port(f'[::]:{PEER_PORT}')
    server.start()
    print(f"Peer server started at port {PEER_PORT}.")
    server.wait_for_termination()

# Function to load file info from a JSON file (simulates .torrent metadata)
def load_file_info(json_filename):
    with open(json_filename, 'r') as file:
        return json.load(file)

# Main function to register peer and start the peer server
def main():
    # Load the file pieces info (from a JSON file)
    file_info = load_file_info(f'./res/peer-{PEER_NUMBER}.json')  # Modify with your metadata file name
    
    # Peer address (could be its IP or 'localhost')
    peer_address = f"localhost:{PEER_PORT}"
    
    # Register this peer with the tracker
    register_peer_with_tracker(peer_address, file_info['file_info'])
    try:
        serve_peer_server(file_info['file_info'])
    except KeyboardInterrupt:
        deregister_peer_with_tracker(peer_address, file_info['file_info'])
    
if __name__ == "__main__":
    main()
