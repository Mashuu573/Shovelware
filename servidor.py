import json
import sqlite3  
from simple_websocket_server import WebSocket, WebSocketServer

HOST = "0.0.0.0"
PORT = 6789
DB_NAME = "chat.db"

# Diccionario para mapear {nombre_usuario: instancia_de_conexion}
usuarios_conectados = {}


# Funciones de base de datos
def inicializar_db():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT,
            destino TEXT,
            texto TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conexion.commit()
    conexion.close()
    print("Base de datos SQLite inicializada")


def guardar_mensaje(remitente, destino, texto):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO mensajes (remitente, destino, texto) VALUES (?, ?, ?)",
        (remitente, destino, texto),
    )
    conexion.commit()
    conexion.close()


def enviar_historial_global(client_ws):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute(
        """
        SELECT remitente, destino, texto FROM mensajes 
        WHERE destino = 'General' 
        ORDER BY id DESC LIMIT 30
    """
    )
    filas = cursor.fetchall()
    conexion.close()

    # Invertimos el orden para mandarlos cronológicamente
    for remitente, destino, texto in reversed(filas):
        paquete = json.dumps(
            {
                "accion": "mensaje_entrante",
                "remitente": remitente,
                "destino": destino,
                "texto": texto,
            }
        )
        client_ws.send_message(paquete)


class GestorChat(WebSocket):

    def handle(self):
        # Este método se ejecuta automaticamente cada vez que llega un mensaje
        datos = json.loads(self.data)
        accion = datos.get("accion")

        # Recuperar el nombre de usuario asociado a la conexion si existe
        usuario_actual = getattr(self, "nombre_usuario", None)

        if accion == "registrar":
            nombre = datos.get("nombre")
            if nombre in usuarios_conectados or nombre.lower() == "general":
                self.send_message(
                    json.dumps(
                        {"accion": "error", "texto": "Nombre inválido o en uso"}
                    )
                )
            else:
                self.nombre_usuario = nombre  # Guardamos el nombre en la conexión
                usuarios_conectados[nombre] = self
                print(f"{nombre} se ha unido a la red.")
                enviar_historial_global(self)

        elif accion == "enviar_mensaje":
            destino = datos.get("destino")
            texto = datos.get("texto")

            guardar_mensaje(usuario_actual, destino, texto)

            paquete = json.dumps(
                {
                    "accion": "mensaje_entrante",
                    "remitente": usuario_actual,
                    "destino": destino,
                    "texto": texto,
                }
            )

            if destino == "General":
                # Bucle 'for' para enviar a todos
                for cliente in usuarios_conectados.values():
                    cliente.send_message(paquete)
            else:
                # Chat Privado: Enviar al destino y a nosotros mismos
                if destino in usuarios_conectados:
                    usuarios_conectados[destino].send_message(paquete)
                if usuario_actual in usuarios_conectados:
                    usuarios_conectados[usuario_actual].send_message(paquete)

        elif accion == "verificar_usuario":
            nombre_a_verificar = datos.get("nombre")
            existe = False

            if nombre_a_verificar in usuarios_conectados:
                existe = True
            else:
                # Busqueda en SQLite
                conexion = sqlite3.connect(DB_NAME)
                cursor = conexion.cursor()
                cursor.execute(
                    "SELECT 1 FROM mensajes WHERE remitente = ? OR destino = ? LIMIT 1",
                    (nombre_a_verificar, nombre_a_verificar),
                )
                if cursor.fetchone():
                    existe = True
                conexion.close()

            self.send_message(
                json.dumps(
                    {
                        "accion": "resultado_verificacion",
                        "existe": existe,
                        "nombre": nombre_a_verificar,
                    }
                )
            )


    def handle_close(self):
        # Se ejecuta automáticamente si el cliente se desconecta 
        usuario_actual = getattr(self, "nombre_usuario", None)
        if usuario_actual in usuarios_conectados:
            del usuarios_conectados[usuario_actual]
            print(f"{usuario_actual} abandonó la red.")


if __name__ == "__main__":
    inicializar_db()
    server = WebSocketServer(HOST, PORT, GestorChat)
    print(f"Servidor activo en ws://0.0.0.0:{PORT}")
    server.serve_forever()