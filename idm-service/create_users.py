import grpc
import auth_pb2 as auth_pb2
import auth_pb2_grpc as auth_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = auth_pb2_grpc.AuthServiceStub(channel)


        users_to_create = [
            ("admin@test.com", "admin123", "admin"),
            ("owner1@test.com", "owner123", "owner-event"),
            ("client1@test.com", "client123", "client")
        ]

        print("1. Inregistrare Utilizatori ")

        for email, password, role in users_to_create:
            print(f"Se inregistreaza: {email} ({role})...")
            try:
                request = auth_pb2.RegisterRequest(
                    username=email,
                    password=password,
                    email=email,
                    role=role
                )

                response = stub.Register(request)

                if response.success:
                    print(f" SUCCES: {response.message}")
                else:
                    print(f" INFO: {response.message}")

            except grpc.RpcError as e:
                print(f" EROARE CONEXIUNE: {e.details()}")
                return

        print("\n2. Autentificare")
        # login dummy owner1
        try:
            print("Se incearca login pentru 'owner1@test.com'...")
            login_resp = stub.Login(auth_pb2.LoginRequest(
                username="owner1@test.com",
                password="owner123"
            ))

            if login_resp.token:
                print("\nTOKEN AUTENTIFICARE:\n")
                print(login_resp.token)

            else:
                print(f"Login esuat: {login_resp.error}")

        except Exception as e:
            print(f"Eroare la login: {e}")


if __name__ == '__main__':
    run()