# Shovelware 
Una aplicacion de escritorio multiusuario con salas publicas y privadas, esta aplicacion se maneja mediante una conexion de red local (Puede ser mediante conexion lan o de wi-fi). Creado como proyecto para la materia de Programacion Orientada a Objetos

## Caracteristicas 
Conexion en tiempo real 
salas de chat (sala publica y privada)

## Requisitos previos para ejecutar este programa
*Mainframe*
wxPython
Python
pip

*Red*
websocket-client

*Servidor*
sqlite3
websocket-server


## Instalacion y configuracion
1. Para poder instalar este repositorio puedes clonarlo en una carpeta vacia de esta forma : 
Creas una nueva carpeta vacia
Dentro de esta carpeta das click derecho
selecionas la opcion "Abrir en terminal"
copia y pega esto para realizar la clonacion del repositorio : 
""" git clone https://github.com/Mashuu573/Shovelware.git """

Para pruebas locales en tu misma maquina, modifica la variable *DIRECCION_SERVIDOR* en red.py para que este configurado en "ws://127.0.0.1:6789"

si se prueba en red local con otros dispositivos, cambialo por la ip privada de tu maquina servidor

## Modo de uso 
python servidor.py (Para ejecutar el servidor y que pueda funcionar el envio de mensajes y las otras funciones)

python MainFrame.py (para abrir la interfaz grafica del chat)

## Tecnologias utilizadas 
Python - Lenguaje principal del desarrollo 
wxPython - Libreria para la interfaz grafia de usuario para tener una GUI nativa
Websocket - Libreria para la comunicacion asincrona cliente-servidor


