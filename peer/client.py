import grpc
import requests 
import tracker_pb2
import tracker_pb2_grpc

def get_file_metadata(file_name):
    response = requests.get(f"http://localhost:5000/files/{file_name}")
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch file metadata for {file_name}")

def get_peers_from_tracker(tracker_address, file_name):
    channel = grpc.insecure_channel(tracker_address)
    
    # Corrected the stub name
    stub = tracker_pb2_grpc.TrackerServiceStub(channel)  # Updated from TrackerStub to TrackerServiceStub
    request = tracker_pb2.GetFilePiecesRequest(file_name=file_name)  # Ensure correct request type
    
    response = stub.GetFilePieces(request)
    return response.pieces  # Assuming 'pieces' is a field in the response

def request_piece_from_peer(peer_address, file_name, piece_number):
    channel = grpc.insecure_channel(peer_address)
    stub = tracker_pb2_grpc.PeerServiceStub(channel)  # Ensure this is correct for your peer
    request = tracker_pb2.PieceRequest(file_name=file_name, piece_number=piece_number)
    
    # Call the peer to check if they have the piece
    response = stub.HasPiece(request)
    return response.has_piece

def main(file_name, tracker_address):
    # Fetch the metadata from the web server
    metadata = get_file_metadata(file_name)
    file_name = metadata["file_name"]
    
    # Step 1: Contact the tracker to get the list of peers
    piece_owners = get_peers_from_tracker(tracker_address, file_name)
    
    # Step 2: For each piece, request from peers
    for piece in metadata["pieces"]:
        piece_number = piece["number"]
        peers = piece_owners.get(piece_number, [])

        print(peers)
        
        # Step 3: Try each peer to see if they have the piece
        for peer_address in peers:
            print(f"Requesting piece {piece_number} from {peer_address}...")
            has_piece = request_piece_from_peer(peer_address, file_name, piece_number)
            
            if has_piece: 
                print(f"Peer {peer_address} confirmed having piece {piece_number}")
            else: 
                print(f"Peer {peer_address} does not have piece {piece_number}")

if __name__ == "__main__":
    tracker_address = "localhost:50050"
    
    while True:
        file_name = input("Download File: ")
        if file_name == "quit": break
        main(file_name, tracker_address)
