# src/translations.py

CURRENT_LANG = "es"

STRINGS = {
    "es": {
        "btn_next": "Siguiente",
        "btn_back": "Atrás",
        "btn_install": "Instalar",
        "btn_reboot": "Reiniciar",
        "btn_quit": "Salir",
        "step_welcome": "Bienvenido",
        "step_system": "Sistema",
        "step_user": "Usuario",
        "step_part": "Disco",
        "step_summary": "Resumen",
        "step_install": "Instalación",
        "step_done": "Listo",
        "wel_title": "Instalador Void Linux",
        "wel_desc": "Este asistente instalará el sistema actual.",
        
        # NEW
        "sys_title": "Configuración del sistema",
        "sys_desc": "Elija la configuración de idioma, zona horaria y teclado.",
        "sys_region": "Región e idioma",
        "sys_lang": "Idioma del sistema:",
        "sys_tz": "Zona horaria:",
        "sys_kbd_frame": "Teclado",
        "sys_layout": "Distribución:",
        
        "part_title": "Método de partición",
        "part_disk": "Disco de destino:",
        "part_erase": "Borrar disco",
        "part_erase_desc": "Elimina todos los datos.",
        "part_free": "Instalar junto a",
        "part_free_desc": "Usa espacio no particionado.",
        "part_fs": "Sistema de archivos:",
        "part_swap": "Swap (8 GB)",
        "part_home": "/home separada",
        "part_warn": "¡Se perderán datos!",
        "sum_title": "Resumen",
        "sum_dev": "Disco",
        "sum_mode": "Modo",
        "sum_fs": "Archivos",
        "sum_user": "Usuario",
        "sum_host": "Hostname",
        "inst_run": "Instalando...",
        "inst_part": "Particionando...",
        "inst_mount": "Montando...",
        "inst_copy": "Copiando...",
        "inst_conf": "Configurando...",
        "inst_fin": "Finalizando...",
        "inst_boot": "Cargador de arranque...",
        "inst_done": "¡Hecho!",
        "inst_fail": "¡Error!",
        "done_title": "¡Éxito!",
        "done_desc": "El sistema está listo.",
        "user_name": "Usuario",
        "user_pass": "Contraseña",
        "user_root": "Contraseña Root",
        "user_host": "Hostname",
        "modal_title": "¿Iniciar?",
        "modal_txt": "Se modificará el disco.",
        "err_title": "Error"
    }
}

def T(key):
    return STRINGS.get(CURRENT_LANG, STRINGS["es"]).get(key, STRINGS["es"].get(key, key))

def set_language(lang_code):
    global CURRENT_LANG
    if lang_code in STRINGS:
        CURRENT_LANG = lang_code
