import asyncio
import websockets

#codigo sacado de la pagina :
#https://www.geeksforgeeks.org/python/simple-chat-room-using-python/
#solo cambie el host para que sea la red local

host = "0.0.0.0"

clients = set()

async def handle(ws):
    clients.add(ws)
    try:
        async for msg in ws:
            await asyncio.gather(*[
                c.send(msg) for c in clients if c != ws
            ])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(ws)

async def main():
    async with websockets.serve(handle, host, 6789):
        print("Server running at ws://localhost:6789")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())