from tkinter import *
import os
import cv2
from mtcnn.mtcnn import MTCNN
from datetime import datetime
import winsound

# Función para registrar el rostro del usuario
def registro_facial():
    cap = cv2.VideoCapture(0)
    detector = MTCNN()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break

        # Detectar rostros en la imagen
        caras = detector.detect_faces(frame)
        for cara in caras:
            x1, y1, ancho, alto = cara['box']
            x2, y2 = x1 + ancho, y1 + alto

            # Validar coordenadas para evitar errores
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            # Recortar y mostrar la región del rostro detectado
            rostro_recortado = frame[y1:y2, x1:x2]
            cv2.imshow('Rostro Detectado', cv2.resize(rostro_recortado, (150, 200)))

        cv2.imshow('Registro Facial', frame)
        if cv2.waitKey(1) == 27:  # Presionar Esc para capturar el rostro
            if caras:
                usuario_img = usuario.get()
                cv2.imwrite(f"{usuario_img}.jpg", rostro_recortado)
                print("Rostro registrado correctamente.")
                usuario_entrada.delete(0, END)
                Label(pantalla1, text="Registro Facial Exitoso", fg="#003366", font=("Segoe UI", 14, 'bold')).pack(pady=10)

                # Guardar el usuario en el archivo de registro
                with open("usuarios.txt", "a") as archivo:
                    archivo.write(f"{usuario_img}\n")
            else:
                print("No se detectó ningún rostro.")
            break

    cap.release()
    cv2.destroyAllWindows()

# Función para comparar dos imágenes de rostros
def orb_sim(img1, img2):
    orb = cv2.ORB_create()
    kpa, descr_a = orb.detectAndCompute(img1, None)
    kpb, descr_b = orb.detectAndCompute(img2, None)
    comp = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = comp.match(descr_a, descr_b)
    regiones_similares = [i for i in matches if i.distance < 70]
    return len(regiones_similares) / len(matches) if matches else 0

# Función para mostrar mensaje de bienvenida
def mostrar_bienvenida(usuario):
    Label(pantalla2, text=f"\u2714 Bienvenido, {usuario}!", fg="#003366", font=("Segoe UI", 16, 'bold')).pack(pady=20)

# Función para iniciar sesión facial
def login_facial():
    global pantalla2

    pantalla2 = Toplevel(pantalla)
    pantalla2.title("Login")
    pantalla2.geometry("400x350")

    cap = cv2.VideoCapture(0)
    detector = MTCNN()

    usuarios = cargar_usuarios()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break

        caras = detector.detect_faces(frame)

        for cara in caras:
            x1, y1, ancho, alto = cara['box']
            x2, y2 = x1 + ancho, y1 + alto
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

            rostro_detectado = frame[y1:y2, x1:x2]
            rostro_detectado = cv2.resize(rostro_detectado, (150, 200), interpolation=cv2.INTER_CUBIC)

            for usuario in usuarios:
                if os.path.exists(f"{usuario}.jpg"):
                    rostro_reg = cv2.imread(f"{usuario}.jpg", 0)
                    rostro_log = cv2.cvtColor(rostro_detectado, cv2.COLOR_BGR2GRAY)
                    similitud = orb_sim(rostro_reg, rostro_log)

                    if similitud >= 0.98:
                        registrar_inicio_sesion(usuario)
                        winsound.Beep(1000, 500)
                        mostrar_bienvenida(usuario)
                        pantalla2.update()
                        cap.release()
                        cv2.destroyAllWindows()
                        pantalla2.after(3000, pantalla2.destroy)
                        return

        if caras:
            winsound.Beep(500, 500)
            Label(pantalla2, text="Usuario no encontrado.", fg="#ad0707", font=("Segoe UI", 14, 'bold')).pack(pady=20)
            pantalla2.update()
            cap.release()
            cv2.destroyAllWindows()
            pantalla2.after(3000, pantalla2.destroy)
            return

        cv2.imshow('Login Facial', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Login facial cancelado.")
            break

    cap.release()
    cv2.destroyAllWindows()

# Función para cargar usuarios registrados
def cargar_usuarios():
    if os.path.exists("usuarios.txt"):
        with open("usuarios.txt", "r") as archivo:
            return [line.strip() for line in archivo]
    return []

# Función para registrar inicio de sesión
def registrar_inicio_sesion(usuario):
    hora_fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("inicios_sesion.txt", "a") as archivo:
        archivo.write(f"{usuario} inició sesión el {hora_fecha}\n")

# Pantalla de registro
def registro():
    global usuario, usuario_entrada, pantalla1
    pantalla1 = Toplevel(pantalla)
    pantalla1.title("Registro")
    pantalla1.geometry("400x350")
    usuario = StringVar()

    Label(pantalla1, text="Registro facial: debe asignar un usuario:", bg="#003366", fg="white", font=("Segoe UI", 12)).pack(pady=10)
    Label(pantalla1, text="Usuario *", font=("Segoe UI", 12), bg="#003366", fg="white").pack(pady=5)
    usuario_entrada = Entry(pantalla1, textvariable=usuario, font=("Segoe UI", 12))
    usuario_entrada.pack(pady=5, padx=20, fill=X)

    Button(pantalla1, text="Registro Facial", width=20, height=2, command=registro_facial, bg="#003366", fg="white", font=("Segoe UI", 12, 'bold')).pack(pady=10)

# Mostrar lista de usuarios registrados
def mostrar_lista_usuarios():
    usuarios = cargar_usuarios()

    pantalla_lista = Toplevel(pantalla)
    pantalla_lista.title("Lista de Usuarios")
    pantalla_lista.geometry("300x400")
    Label(pantalla_lista, text="Usuarios Registrados", font=("Segoe UI", 14), fg="#003366").pack(pady=10)

    for usuario in usuarios:
        Label(pantalla_lista, text=usuario, font=("Segoe UI", 12)).pack(anchor="w", padx=20)

# Mostrar lista de inicios de sesión
def mostrar_lista_inicios_sesion():
    if os.path.exists("inicios_sesion.txt"):
        with open("inicios_sesion.txt", "r") as archivo:
            inicios = archivo.readlines()
    else:
        inicios = []

    pantalla_lista_inicios = Toplevel(pantalla)
    pantalla_lista_inicios.title("Inicios de Sesión")
    pantalla_lista_inicios.geometry("400x400")
    Label(pantalla_lista_inicios, text="Inicios de Sesión", font=("Segoe UI", 14), fg="#003366").pack(pady=10)

    for inicio in inicios:
        Label(pantalla_lista_inicios, text=inicio.strip(), font=("Segoe UI", 12)).pack(anchor="w", padx=20)

# Pantalla principal
def pantalla_principal():
    global pantalla
    pantalla = Tk()
    pantalla.geometry("400x500")
    pantalla.title("Proyecto Final")

    Label(pantalla, text="Login Inteligente", bg="#003366", fg="white", width="300", height="2", font=("Segoe UI", 15, 'bold')).pack(pady=20)
    Button(pantalla, text="Iniciar Sesión", height="2", width="30", command=login_facial, bg="#003366", fg="white", font=("Segoe UI", 12, 'bold')).pack(pady=10)
    Button(pantalla, text="Registro", height="2", width="30", command=registro, bg="#003366", fg="white", font=("Segoe UI", 12, 'bold')).pack(pady=10)
    Button(pantalla, text="Usuarios Registrados", height="2", width="30", command=mostrar_lista_usuarios, bg="#003366", fg="white", font=("Segoe UI", 12, 'bold')).pack(pady=10)
    Button(pantalla, text="Historial de Sesión", height="2", width="30", command=mostrar_lista_inicios_sesion, bg="#003366", fg="white", font=("Segoe UI", 12, 'bold')).pack(pady=10)

    pantalla.mainloop()

pantalla_principal()