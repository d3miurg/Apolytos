from fastapi import WebSocket


class ConnectionManager():
    def __init__(self):
        self.connections = []

    async def add_connection(self, socket: WebSocket):
        await socket.accept()
        self.connections.append(socket)

    def discard_connection(self, socket: WebSocket):
        self.connections.remove(socket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)
