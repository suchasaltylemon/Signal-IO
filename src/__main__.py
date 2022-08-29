from signalio import Signal, SecureClient, SecureServer, SecureConnection

do_server = input("Server? ") == "y"

if do_server:
    s = SecureServer("0.0.0.0", 7777)

    usernames = {}


    @s.Connected()
    def h(conn: SecureConnection):
        @conn.Signalled("/username/set")
        def set_username(signal):
            username = signal.data["username"]
            usernames[conn] = username

            s.send_to_all(Signal("/message/echo", {
                "author": "SERVER",
                "message": f"{username} has joined"
            }))

        @conn.Signalled("/message")
        def handle_message(signal):
            username = usernames[conn]
            message = signal.data["message"]

            s.send_to_all(Signal("/message/echo", {
                "message": message,
                "author": username
            }))


    s.start()

else:

    c = SecureClient("127.0.0.1", 7777)


    @c.Connected()
    def handle_connection(conn):
        if not conn.secure:
            conn.Secured.wait()

        print("Connected")

        username = input("Enter username: ")

        conn.send(Signal("/username/set", {
            "username": username
        }))

        @conn.Signalled("/message/echo")
        def echo_message(signal):
            recv_message = signal.data["message"]
            author = signal.data["author"]

            print(f"{author}) {recv_message}")

        while True:
            send_message = input(" > ")

            conn.send(Signal("/message", {
                "message": send_message
            }))


    c.connect()
