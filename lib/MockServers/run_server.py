import MockServers.Mocky as mocky
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the mock server")
    parser.add_argument("--host", help="The hostname for the server")
    parser.add_argument("--port", type=int, help="The port number for the server")
    args = parser.parse_args()

    server = mocky.ServerController(args.host, args.port)
    server.start()

    # server_class = mocky.MockServer
    # handler_class = mocky.JSONRPCHandler
    # httpd = server_class((HOST, PORT), handler_class)
    # print(time.asctime(), 'JSON RPC Server Starting at %s:%s' % (HOST, PORT))
    # try:
    #     httpd.serve_forever()
    # except KeyboardInterrupt:
    #     pass
    # httpd.server_close()
    # print(time.asctime(), 'JSON RPC Server Stopping at %s:%s' % (HOST, PORT))
