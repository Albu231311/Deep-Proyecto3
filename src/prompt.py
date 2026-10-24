"""
Construcción del prompt estandarizado.

El MISMO prompt se usa en:
  - el entrenamiento LoRA (notebooks/02_entrenamiento.ipynb),
  - la inferencia con adapter y sin adapter (solucion.py).
Así la comparación baseline vs. fine-tuning es justa.
"""
import re


SYSTEM_PROMPT = (
    "Eres un experto en MySQL 8.4. Devuelve solo una consulta SELECT o WITH...SELECT, "
    "sin explicaciones ni markdown. Respeta ONLY_FULL_GROUP_BY. "
    "Usa solo tablas y columnas del esquema."
)


# Limpieza del esquema

# Opciones de tabla que no aportan nada al modelo y solo gastan tokens
_OPCIONES_TABLA = re.compile(
    r"\s*(ENGINE|AUTO_INCREMENT|DEFAULT CHARSET|CHARSET|COLLATE|ROW_FORMAT)=\S+",
    re.IGNORECASE,
)
# Charset / collation a nivel de columna
_OPCIONES_COLUMNA = re.compile(
    r"\s+(CHARACTER SET \w+|COLLATE \w+)", re.IGNORECASE
)


def limpiar_esquema(esquema: str) -> str:
    """
    Compacta la salida de SHOW CREATE TABLE sin perder información útil:
    quita ENGINE, CHARSET, COLLATE y AUTO_INCREMENT, pero conserva columnas,
    tipos, llaves, FOREIGN KEY y todos los COMMENT.
    """
    lineas = []
    for linea in esquema.strip().splitlines():
        if linea.startswith(")"):
            linea = _OPCIONES_TABLA.sub("", linea)
        else:
            linea = _OPCIONES_COLUMNA.sub("", linea)
        lineas.append(linea.rstrip())
    return "\n".join(lineas)


# Mensajes de chat

def construir_mensajes(esquema: str, pregunta: str) -> list[dict]:
    """Mensajes system + user para una pregunta (sin la respuesta)."""
    user = (
        "### Esquema\n"
        f"{limpiar_esquema(esquema)}\n\n"
        "### Pregunta\n"
        f"{pregunta.strip()}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def construir_mensajes_correccion(
    esquema: str, pregunta: str, sql_previo: str, error: str
) -> list[dict]:
    """
    Mensajes para el experimento de autocorrección: se agrega la consulta
    que falló y el error devuelto por MySQL, y se pide una versión corregida.
    """
    mensajes = construir_mensajes(esquema, pregunta)
    mensajes.append({"role": "assistant", "content": sql_previo})
    mensajes.append({
        "role": "user",
        "content": (
            f"La consulta falló en MySQL 8.4 con este error:\n{error}\n"
            "Corrígela. Devuelve solo la consulta SQL corregida."
        ),
    })
    return mensajes


def construir_prompt(tokenizer, esquema: str, pregunta: str) -> str:
    """Texto del prompt listo para generar (termina en el turno del asistente)."""
    return tokenizer.apply_chat_template(
        construir_mensajes(esquema, pregunta),
        tokenize=False,
        add_generation_prompt=True,
    )
