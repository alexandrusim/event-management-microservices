from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import grpc
import auth_pb2
import auth_pb2_grpc
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

IDM_CHANNEL_ADDRESS = os.getenv("IDM_GRPC_ADDRESS", 'localhost:50051')

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        with grpc.insecure_channel(IDM_CHANNEL_ADDRESS) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            response = stub.ValidateToken(auth_pb2.ValidateRequest(token=token))

            if not response.valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalid sau expirat"
                )

            return {
                "user_id": int(response.userId),
                "role": response.role
            }

    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviciul de autentificare nu este disponibil."
        )