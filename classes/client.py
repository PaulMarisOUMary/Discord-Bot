import asyncio
import argparse

class ClientProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport: asyncio.Transport):
        transport.write(self.message.encode())

    def data_received(self, data: bytes):
        if not data == bytes(self.message, encoding="utf-8"):
            raise ValueError("Data received seems corruped.")

    def connection_lost(self, exc):
        self.on_con_lost.set_result(True)

async def main(args):
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    message = args.message

    transport, _ = await loop.create_connection(
        protocol_factory = lambda: ClientProtocol(message, on_con_lost),
        host = args.host, 
        port = args.port
    )

    try:
        await on_con_lost
    finally:
        transport.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for discord socket transport cog.")
    parser.add_argument("--host", dest="host", type=str, default="127.0.0.1", help="Host to connect to.")
    parser.add_argument("--port", dest="port", type=int, default=50000, help="Port to connect to.")
    parser.add_argument("--message", dest="message", type=str, default="ping", help="Message to send to the socket server.")

    args = parser.parse_args()

    asyncio.run(main(args))