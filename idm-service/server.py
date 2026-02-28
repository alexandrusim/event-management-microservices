import grpc
from concurrent import futures
import time
import os
import hashlib
import jwt
import datetime
import uuid
from dotenv import load_dotenv


import auth_pb2 as auth_pb2
import auth_pb2_grpc as auth_pb2_grpc


from auth_db import SessionLocal, Utilizator

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")


class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        self.blocklist = set()

    def get_db(self):
        return SessionLocal()

    def Register(self, request, context):
        db = self.get_db()
        try:
            # Vf email existent
            existing_user = db.query(Utilizator).filter(Utilizator.email == request.email).first()
            if existing_user:
                return auth_pb2.RegisterResponse(success=False, message="Email already registered")

            hashed_password = hashlib.sha256(request.password.encode()).hexdigest()

            if request.role not in ['admin', 'owner-event', 'client']:
                return auth_pb2.RegisterResponse(success=False, message="Invalid role")

            new_user = Utilizator(
                email=request.email,
                parola=hashed_password,
                rol=request.role
            )
            db.add(new_user)
            db.commit()
            return auth_pb2.RegisterResponse(success=True, message="User registered successfully")
        except Exception as e:
            print(f"Error registering: {e}")
            return auth_pb2.RegisterResponse(success=False, message="Internal error")
        finally:
            db.close()

    def Login(self, request, context):
        email_login = request.username
        password_login = request.password

        db = self.get_db()
        try:
            user = db.query(Utilizator).filter(Utilizator.email == email_login).first()

            if not user:
                return auth_pb2.LoginResponse(token="", error="Invalid credentials")

            hashed_password = hashlib.sha256(password_login.encode()).hexdigest()
            if user.parola != hashed_password:
                return auth_pb2.LoginResponse(token="", error="Invalid credentials")

            payload = {
                "iss": "http://localhost:50051",
                "sub": str(user.ID),
                "email": user.email,
                "role": user.rol,
                "jti": str(uuid.uuid4()),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }

            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            return auth_pb2.LoginResponse(token=token, error="")

        except Exception as e:
            print(f"Login error: {e}")
            return auth_pb2.LoginResponse(token="", error="Internal server error")
        finally:
            db.close()

    def ValidateToken(self, request, context):
        # Verificare blacklist
        if request.token in self.blocklist:
            return auth_pb2.ValidateResponse(valid=False, error="Token invalidated/blacklisted")

        try:
            # Decodare si validare semnatura + expirare
            payload = jwt.decode(request.token, JWT_SECRET, algorithms=["HS256"])

            return auth_pb2.ValidateResponse(
                valid=True,
                error="",
                userId=payload.get("sub"),
                role=payload.get("role")
            )

        except jwt.ExpiredSignatureError:
            return auth_pb2.ValidateResponse(valid=False, error="Token expired")
        except jwt.InvalidTokenError:
            return auth_pb2.ValidateResponse(valid=False, error="Invalid token")
        except Exception as e:
            return auth_pb2.ValidateResponse(valid=False, error=f"Validation error: {str(e)}")

    def InvalidateToken(self, request, context):
        # Adaugare in blacklist (Logout)
        self.blocklist.add(request.token)
        return auth_pb2.InvalidateResponse(success=True, error="")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    server.add_insecure_port('[::]:50051')
    print("IDM gRPC Server started on port 50051...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()