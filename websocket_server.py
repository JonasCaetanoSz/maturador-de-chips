import websockets
import asyncio

class WebSocketServer:
    def __init__(self):
        self.connections = set()
        self.server = None
        self.stop_requested = False

    async def handle_message(self, message):
        if message == "stop_server=True":
            self.stop_requested = True
            return

        for connection in self.connections:
            try:
                await connection.send(message)
            except:
                pass

    async def receive_message(self, websocket):
        async for message in websocket:
            await self.handle_message(message)

            if self.stop_requested:
                break

    async def receiver_message(self, websocket, path):
        self.connections.add(websocket)

        await self.receive_message(websocket)
        self.connections.remove(websocket)

    async def start_server(self):
        self.server = await websockets.serve(self.receiver_message, 'localhost', 5026)
        await self.server.wait_closed()

    def stop(self):
        if self.server:
            self.connections.clear()
            self.server.close()
            self.server = None

    def run(self):
        asyncio.run(self.start_server())

e = WebSocketServer()
e.run()

while True:
    if e.stop_requested:
        e.stop()
        break