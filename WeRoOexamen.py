#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================
  WeRoO limpiador de archivos
  Script para Termux (Android) - Python 3
  Autor: WeRoO
  Fecha: 2026
==============================================================
"""

import os
import sys
import time
import re

# ============================================================
# 1. CONFIGURACIÓN DE RUTAS
# ============================================================
RUTA_COMBOS = "/storage/emulated/0/Termux/combo"
CARPETA_SALIDA = "/storage/emulated/0/Termux/combo/combos limpios"
ARCHIVO_USERPASS = os.path.join(CARPETA_SALIDA, "UserPassword.txt")
ARCHIVO_SERVIDORES = os.path.join(CARPETA_SALIDA, "Servidores.txt")

# ============================================================
# 2. COLORES ANSI
# ============================================================
VIOLETA = "\033[95m"
CYAN = "\033[96m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
ROJO = "\033[91m"
GRIS = "\033[90m"
RESET = "\033[0m"
NEGRITA = "\033[1m"

# ============================================================
# 3. FUNCIONES DE INTERFAZ
# ============================================================
def limpiar_pantalla():
    """Limpia la pantalla de la terminal."""
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


def titulo():
    """Muestra el banner multicolor de WeRoO."""
    banner = f"""
{NEGRITA}{VIOLETA} ██╗    ██╗███████╗██████╗  ██████╗ ███████╗
{NEGRITA}{CYAN}   ██║  ██║██╔════╝██╔══██╗██╔═══██╗██╔════╝
{NEGRITA}{VERDE}   ██║  ██║█████╗  ██████╔╝██║   ██║█████╗
{NEGRITA}{AMARILLO}  ██║  ██║██╔══╝  ██╔══██╗██║   ██║██╔══╝
{NEGRITA}{ROJO}    ██║  ██║███████╗██║  ██║╚██████╔╝██║
{NEGRITA}{VIOLETA}   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝
{RESET}"""
    print(banner)
    print(f"{NEGRITA}{CYAN}       WeRoO limpiador de archivos{RESET}")
    print(f"{GRIS}       Ruta de búsqueda: {RUTA_COMBOS}{RESET}")
    linea()


def linea():
    """Dibuja una línea separadora."""
    print(f"{VIOLETA}{'=' * 60}{RESET}")


def progreso(actual, total, ancho=40):
    """Muestra una barra de progreso en la misma línea."""
    if total == 0:
        porcentaje = 100
    else:
        porcentaje = int((actual / total) * 100)
    llenado = int(ancho * actual / total) if total > 0 else ancho
    barra = f"{'█' * llenado}{'.' * (ancho - llenado)}"
    sys.stdout.write(
        f"\r{CYAN}Procesando {RESET}[{VERDE}{barra}{RESET}] {AMARILLO}{porcentaje}%{RESET}"
    )
    sys.stdout.flush()


# ============================================================
# 4. BÚSQUEDA Y SELECCIÓN DE ARCHIVOS
# ============================================================
def buscar_archivos():
    """Busca archivos .txt en la ruta de combos."""
    archivos = []
    try:
        if not os.path.isdir(RUTA_COMBOS):
            return None
        for nombre in os.listdir(RUTA_COMBOS):
            ruta_completa = os.path.join(RUTA_COMBOS, nombre)
            if os.path.isfile(ruta_completa) and nombre.lower().endswith(".txt"):
                archivos.append(nombre)
    except PermissionError:
        print(f"{ROJO}[!] Error: falta de permisos para leer la carpeta.{RESET}")
        return None
    except Exception as e:
        print(f"{ROJO}[!] Error al buscar archivos: {e}{RESET}")
        return None
    archivos.sort()
    return archivos


def mostrar_archivos(archivos):
    """Muestra los archivos encontrados numerados."""
    print(f"\n{NEGRITA}{VERDE}[+] Archivos .txt encontrados:{RESET}\n")
    for i, nombre in enumerate(archivos, start=1):
        print(f"  {CYAN}[{i}]{RESET} {AMARILLO}{nombre}{RESET}")
    print()


def seleccionar_archivo(archivos):
    """Permite al usuario seleccionar un archivo por número."""
    while True:
        try:
            entrada = input(f"{NEGRITA}{VIOLETA}Selecciona un archivo (número): {RESET}").strip()
            if entrada.lower() in ("q", "salir", "exit"):
                return None
            if not entrada:
                print(f"{ROJO}[!] Debes introducir un número.{RESET}")
                continue
            indice = int(entrada)
            if 1 <= indice <= len(archivos):
                return archivos[indice - 1]
            else:
                print(f"{ROJO}[!] Número fuera de rango. Intenta de nuevo.{RESET}")
        except ValueError:
            print(f"{ROJO}[!] Entrada inválida. Introduce un número.{RESET}")
        except (KeyboardInterrupt, EOFError):
            print()
            return None


# ============================================================
# 5. PROCESAMIENTO DE ARCHIVOS
# ============================================================
def contar_lineas(ruta_archivo):
    """Cuenta las líneas de un archivo de forma eficiente."""
    total = 0
    try:
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
            for _ in f:
                total += 1
    except Exception:
        total = 0
    return total


def procesar_archivo(ruta_archivo):
    """
    Procesa el archivo línea por línea detectando:
      - Usuario/Username/Usuário + Password/Contraseña/Senha
      - Servidor/Host
    Devuelve dos listas: userpass y servidores.
    """
    userpass = []
    servidores = []

    # Patrones de detección (insensibles a mayúsculas)
    patrones_usuario = re.compile(
        r"^\s*(?:usuario|username|usuário)\s*[:=]\s*(.+?)\s*$",
        re.IGNORECASE | re.UNICODE,
    )
    patrones_password = re.compile(
        r"^\s*(?:password|contraseña|senha)\s*[:=]\s*(.+?)\s*$",
        re.IGNORECASE | re.UNICODE,
    )
    patron_servidor = re.compile(
        r"^\s*(?:servidor|server)\s*[:=]\s*(.+?)\s*$",
        re.IGNORECASE | re.UNICODE,
    )
    patron_host = re.compile(
        r"^\s*host\s*[:=]\s*(.+?)\s*$",
        re.IGNORECASE | re.UNICODE,
    )

    # También soporta formato en una sola línea:
    # Username:USUARIO Password:CONTRASEÑA
    patron_linea_completa = re.compile(
        r"(?:usuario|username|usuário)\s*[:=]\s*([^\s]+)\s+"
        r"(?:password|contraseña|senha)\s*[:=]\s*(.+)",
        re.IGNORECASE | re.UNICODE,
    )

    usuario_actual = None
    total_lineas = contar_lineas(ruta_archivo)

    try:
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
            for numero_linea, linea in enumerate(f, start=1):
                progreso(numero_linea, total_lineas)
                linea_strip = linea.strip()
                if not linea_strip:
                    continue

                # 1) Formato en una sola línea (Usuario + Password)
                match_completo = patron_linea_completa.search(linea_strip)
                if match_completo:
                    user = match_completo.group(1).strip()
                    pwd = match_completo.group(2).strip()
                    if user and pwd:
                        userpass.append(f"Username:{user} Password:{pwd}")
                    continue

                # 2) Usuario
                match_user = patrones_usuario.match(linea_strip)
                if match_user:
                    usuario_actual = match_user.group(1).strip()
                    continue

                # 3) Password
                match_pass = patrones_password.match(linea_strip)
                if match_pass:
                    pwd = match_pass.group(1).strip()
                    if usuario_actual and pwd:
                        userpass.append(
                            f"Username:{usuario_actual} Password:{pwd}"
                        )
                    usuario_actual = None
                    continue

                # 4) Servidor
                match_srv = patron_servidor.match(linea_strip)
                if match_srv:
                    valor = match_srv.group(1).strip()
                    if valor:
                        servidores.append(f"Servidor:{valor}")
                    continue

                # 5) Host
                match_host = patron_host.match(linea_strip)
                if match_host:
                    valor = match_host.group(1).strip()
                    if valor:
                        servidores.append(f"Host:{valor}")
                    continue

                # Si hay una línea que no coincide con nada,
                # se descarta el usuario pendiente (no es password válido)
                usuario_actual = None

        progreso(total_lineas, total_lineas)
        print()
    except PermissionError:
        print(f"\n{ROJO}[!] Error: falta de permisos para leer el archivo.{RESET}")
        return None, None
    except Exception as e:
        print(f"\n{ROJO}[!] Error al leer el archivo: {e}{RESET}")
        return None, None

    return userpass, servidores


# ============================================================
# 6. ELIMINACIÓN DE DUPLICADOS
# ============================================================
def quitar_duplicados(lista):
    """Elimina duplicados conservando el orden de aparición."""
    if lista is None:
        return []
    vistos = set()
    resultado = []
    for elemento in lista:
        if elemento not in vistos:
            vistos.add(elemento)
            resultado.append(elemento)
    return resultado


# ============================================================
# 7. GUARDADO DE RESULTADOS
# ============================================================
def guardar_resultados(userpass, servidores):
    """Crea la carpeta de salida y guarda los archivos finales."""
    try:
        if not os.path.isdir(CARPETA_SALIDA):
            os.makedirs(CARPETA_SALIDA, exist_ok=True)
    except PermissionError:
        print(f"{ROJO}[!] Error: falta de permisos para crear la carpeta de salida.{RESET}")
        return False
    except Exception as e:
        print(f"{ROJO}[!] Error al crear la carpeta: {e}{RESET}")
        return False

    try:
        with open(ARCHIVO_USERPASS, "w", encoding="utf-8") as f:
            for linea in userpass:
                f.write(linea + "\n")
    except PermissionError:
        print(f"{ROJO}[!] Error: falta de permisos para guardar UserPassword.txt{RESET}")
        return False
    except Exception as e:
        print(f"{ROJO}[!] Error al guardar UserPassword.txt: {e}{RESET}")
        return False

    try:
        with open(ARCHIVO_SERVIDORES, "w", encoding="utf-8") as f:
            for linea in servidores:
                f.write(linea + "\n")
    except PermissionError:
        print(f"{ROJO}[!] Error: falta de permisos para guardar Servidores.txt{RESET}")
        return False
    except Exception as e:
        print(f"{ROJO}[!] Error al guardar Servidores.txt: {e}{RESET}")
        return False

    return True


# ============================================================
# 8. RESULTADO FINAL
# ============================================================
def mostrar_resultados(archivo_procesado, userpass, servidores):
    """Muestra el resumen final con vistas previas."""
    limpiar_pantalla()
    titulo()

    print(f"\n{NEGRITA}{VERDE}[+] Archivo procesado:{RESET} {AMARILLO}{archivo_procesado}{RESET}")
    print(f"{NEGRITA}{VERDE}[+] User/Password encontrados:{RESET} {CYAN}{len(userpass)}{RESET}")
    print(f"{NEGRITA}{VERDE}[+] Servidores/Hosts encontrados:{RESET} {CYAN}{len(servidores)}{RESET}")
    print(f"{NEGRITA}{VERDE}[+] Ruta UserPassword.txt:{RESET} {GRIS}{ARCHIVO_USERPASS}{RESET}")
    print(f"{NEGRITA}{VERDE}[+] Ruta Servidores.txt:{RESET} {GRIS}{ARCHIVO_SERVIDORES}{RESET}")
    linea()

    # Vista previa User/Password
    print(f"\n{NEGRITA}{VIOLETA}>> Vista previa User/Password (primeros 5):{RESET}")
    if userpass:
        for item in userpass[:5]:
            print(f"  {CYAN}•{RESET} {item}")
    else:
        print(f"  {ROJO}(No se encontraron User/Password){RESET}")

    linea()

    # Vista previa Servidores/Hosts
    print(f"\n{NEGRITA}{VIOLETA}>> Vista previa Servidores/Hosts (primeros 5):{RESET}")
    if servidores:
        for item in servidores[:5]:
            print(f"  {CYAN}•{RESET} {item}")
    else:
        print(f"  {ROJO}(No se encontraron Servidores/Hosts){RESET}")

    linea()


# ============================================================
# 9. FUNCIÓN PRINCIPAL
# ============================================================
def main():
    """Función principal del programa."""
    try:
        limpiar_pantalla()
        titulo()

        # Verificar que la carpeta de búsqueda exista
        if not os.path.isdir(RUTA_COMBOS):
            print(f"\n{ROJO}[!] Error: la carpeta {RUTA_COMBOS} no existe.{RESET}")
            print(f"{AMARILLO}Crea la carpeta e introduce archivos .txt para procesar.{RESET}")
            print(f"\n{NEGRITA}{AMARILLO}No pudiste Sacarme CHEVIC{RESET}")
            try:
                input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
            except (KeyboardInterrupt, EOFError):
                pass
            return

        # Buscar archivos
        print(f"\n{CYAN}Buscando archivos .txt en {RUTA_COMBOS}...{RESET}")
        time.sleep(0.5)
        archivos = buscar_archivos()

        if archivos is None:
            print(f"{ROJO}[!] No se pudo acceder a la carpeta.{RESET}")
            try:
                input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
            except (KeyboardInterrupt, EOFError):
                pass
            return

        if not archivos:
            print(f"{ROJO}[!] No se encontraron archivos .txt en la carpeta.{RESET}")
            print(f"{AMARILLO}Coloca archivos .txt en {RUTA_COMBOS} e intenta de nuevo.{RESET}")
            print(f"\n{NEGRITA}{AMARILLO}No pudiste Sacarme CHEVIC{RESET}")
            try:
                input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
            except (KeyboardInterrupt, EOFError):
                pass
            return

        # Mostrar y seleccionar archivo
        mostrar_archivos(archivos)
        archivo_seleccionado = seleccionar_archivo(archivos)

        if archivo_seleccionado is None:
            print(f"{AMARILLO}[i] Saliendo del programa...{RESET}")
            print(f"\n{NEGRITA}{AMARILLO}No pudiste Sacarme CHEVIC{RESET}")
            try:
                input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
            except (KeyboardInterrupt, EOFError):
                pass
            return

        ruta_completa = os.path.join(RUTA_COMBOS, archivo_seleccionado)

        # Procesar archivo
        print(f"\n{CYAN}Procesando archivo: {AMARILLO}{archivo_seleccionado}{RESET}")
        userpass, servidores = procesar_archivo(ruta_completa)

        if userpass is None or servidores is None:
            print(f"{ROJO}[!] Ocurrió un error durante el procesamiento.{RESET}")
            try:
                input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
            except (KeyboardInterrupt, EOFError):
                pass
            return

        # Quitar duplicados
        print(f"\n{CYAN}Eliminando duplicados...{RESET}")
        time.sleep(0.3)
        userpass = quitar_duplicados(userpass)
        servidores = quitar_duplicados(servidores)
        print(f"{VERDE}[+] Duplicados eliminados.{RESET}")

        # Guardar resultados
        print(f"{CYAN}Guardando resultados...{RESET}")
        time.sleep(0.3)
        if not guardar_resultados(userpass, servidores):
            print(f"{ROJO}[!] No se pudieron guardar los archivos.{RESET}")
            try:
                input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
            except (KeyboardInterrupt, EOFError):
                pass
            return

        print(f"{VERDE}[+] Archivos guardados correctamente.{RESET}")
        time.sleep(0.5)

        # Mostrar resultado final
        mostrar_resultados(archivo_seleccionado, userpass, servidores)

        # Mensaje final
        print(f"\n{NEGRITA}{AMARILLO}No pudiste Sacarme CHEVIC{RESET}")
        try:
            input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
        except (KeyboardInterrupt, EOFError):
            print()

    except KeyboardInterrupt:
        print(f"\n{ROJO}[!] Programa interrumpido por el usuario.{RESET}")
        print(f"{NEGRITA}{AMARILLO}No pudiste Sacarme CHEVIC{RESET}")
        try:
            input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
        except (KeyboardInterrupt, EOFError):
            pass
    except Exception as e:
        print(f"\n{ROJO}[!] Error inesperado: {e}{RESET}")
        try:
            input(f"{VERDE}Presiona Enter y ten un Lindo día.{RESET}")
        except (KeyboardInterrupt, EOFError):
            pass


if __name__ == "__main__":
    main()