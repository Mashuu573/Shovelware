import asyncio
import websockets
import json
import aiosqlite

host = "0.0.0.0"
port = 6789

# Diccionario para mapear {nombre_usuario: conexion_ws}
usuarios_conectados = {}
DB_NAME = "chat.db"

async def inicializar_db():
    #Crea el archivo chat.db y la tabla si no existen
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                remitente TEXT,
                destino TEXT,
                texto TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    print("Base de datos SQLite inicializada")

async def enviar_historial_global(ws):
    #Carga los últimos 30 mensajes generales para los nuevos usuarios
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT remitente, destino, texto FROM mensajes 
            WHERE destino = 'Global' 
            ORDER BY id DESC LIMIT 30
        """) as cursor:
            filas = await cursor.fetchall()
            for remitente, destino, texto in reversed(filas):
                paquete = json.dumps({
                    "accion": "mensaje_entrante",
                    "remitente": remitente,
                    "destino": destino,
                    "texto": texto
                })
                await ws.send(paquete)

async def guardar_mensaje(remitente, destino, texto):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO mensajes (remitente, destino, texto) VALUES (?, ?, ?)",
            (remitente, destino, texto)
        )
        await db.commit()

async def handle(ws):
    usuario_actual = None
    try:
        async for msg in ws:
            datos = json.loads(msg)
            accion = datos.get("accion")

            if accion == "registrar":
                nombre = datos.get("nombre")
                if nombre in usuarios_conectados or nombre.lower() == "global":
                    await ws.send(json.dumps({"accion": "error", "texto": "Nombre inválido o en uso"}))
                else:
                    usuario_actual = nombre
                    usuarios_conectados[nombre] = ws
                    print(f"{nombre} se ha unido a la red.")
                    await enviar_historial_global(ws)

            elif accion == "enviar_mensaje":
                destino = datos.get("destino")
                texto = datos.get("texto")
                
                await guardar_mensaje(usuario_actual, destino, texto)

                paquete = json.dumps({
                    "accion": "mensaje_entrante",
                    "remitente": usuario_actual,
                    "destino": destino,
                    "texto": texto
                })

                if destino == "Global":
                    if usuarios_conectados:
                        await asyncio.gather(*[c.send(paquete) for c in usuarios_conectados.values()], return_exceptions=True)
                else:
                    # Direccionamiento uno a uno (Privado)
                    if destino in usuarios_conectados:
                        await usuarios_conectados[destino].send(paquete)
                    if usuario_actual in usuarios_conectados:
                        await usuarios_conectados[usuario_actual].send(paquete)

            elif accion == "verificar_usuario":
                nombre_a_verificar = datos.get("nombre")
                existe = False
            
                # Comprobación rápida: ¿Está conectado?
                if nombre_a_verificar in usuarios_conectados:
                    existe = True
                else:
                    # ¿Existe registro de él usuario en SQLite?
                    async with aiosqlite.connect(DB_NAME) as db:
                        async with db.execute(
                            "SELECT 1 FROM mensajes WHERE remitente = ? OR destino = ? LIMIT 1",
                            (nombre_a_verificar, nombre_a_verificar)
                        ) as cursor:
                            fila = await cursor.fetchone()
                            if fila:
                                existe = True

                # Le respondemos únicamente al usuario que hizo la pregunta
                await ws.send(json.dumps({
                    "accion": "resultado_verificacion",
                    "existe": existe,
                    "nombre": nombre_a_verificar
                }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if usuario_actual in usuarios_conectados:
            del usuarios_conectados[usuario_actual]
            print(f"{usuario_actual} abandonó la red.")

async def main():
    await inicializar_db()
    async with websockets.serve(handle, host, port):
        print(f"Servidor activo en ws://0.0.0.0:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())