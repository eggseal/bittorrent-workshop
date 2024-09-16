pip install -r ./requirements.txt
python -m grpc_tools.protoc -I. --python_out=./peer --grpc_python_out=./peer tracker.proto
python -m grpc_tools.protoc -I. --python_out=./tracker --grpc_python_out=./tracker tracker.proto