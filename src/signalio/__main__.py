def setup_server(s):
    @s.Connected
    def handle_connection_on_server(conn):
        @conn.Signalled("/greet_server")
        def say_hello_on_server(signal):
            print("Hello, World!")

            conn.send(Signal("/respond_client", {
                "name": "John"
            }))


def setup_client(c):
    @c.Connected
    def handle_connection_on_client(conn):
        @conn.Signalled("/respond_client")
        def handle_response(signal):
            name = signal.data["name"]

            print(f"Greetings from {name}")

        conn.send(Signal("/greet_server"))


def main():
    s = Server(PORT)
    c = Client(IP, PORT)

    setup_server(s)
    setup_client(c)

    s.start()
    c.connect()

    wait(2)

    s.stop()


if __name__ == "__main__":
    from lib import Server, Client, Signal, get_host
    from time import sleep as wait

    IP = get_host()
    PORT = 7092

    main()
