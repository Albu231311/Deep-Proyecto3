"""
solucion.py — Archivo de entrega oficial del Proyecto 3 (Text-to-SQL con LoRA).

Al importarse carga el modelo indicado en config.json (con o sin adapter LoRA)
y expone:

    generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str

- ejecutar=None : una sola pasada de generación.
- ejecutar(sql) : autocorrección; si MySQL devuelve error, se le muestra el error
                  al modelo y se pide otra consulta (máximo 3 llamadas a ejecutar).
"""
import json
import os
import random
import sys
import time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RAIZ = os.path.dirname(os.path.abspath(__file__))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from src.prompt import construir_mensajes, construir_mensajes_correccion
from src.filtro import es_solo_lectura, limpiar_salida, SQL_RESPALDO


MAX_NUEVOS_TOKENS = 256
MAX_LLAMADAS_EJECUTAR = 3
# Margen de seguridad: no se inicia otra corrección si ya pasaron estos segundos
LIMITE_SEGUNDOS = 20.0

_modelo = None
_tokenizer = None
_device = None


# Carga del modelo

def _fijar_semilla(semilla: int) -> None:
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)
    torch.cuda.manual_seed_all(semilla)


def cargar_modelo(usar_adapter=None, adapter=None, config_path=None) -> None:
    """
    Carga modelo base + (opcionalmente) adapter LoRA según config.json.
    Los argumentos permiten sobreescribir la configuración desde los notebooks
    (p. ej. evaluar baseline, r=8 y r=32 sin editar config.json).
    """
    global _modelo, _tokenizer, _device

    with open(config_path or os.path.join(RAIZ, "config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
    if usar_adapter is None:
        usar_adapter = config.get("usar_adapter", True)
    adapter = adapter or config.get("adapter", "adapter/")
    if not os.path.isabs(adapter):
        adapter = os.path.join(RAIZ, adapter)

    _fijar_semilla(config.get("semilla", 2026))

    # Liberar el modelo anterior si se recarga desde un notebook
    _modelo = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    # float16 en GPU (T4); en CPU float16 es muy lento, se usa float32 solo para pruebas locales
    dtype = torch.float16 if _device == "cuda" else torch.float32

    _tokenizer = AutoTokenizer.from_pretrained(config["modelo_base"])
    modelo = AutoModelForCausalLM.from_pretrained(config["modelo_base"], torch_dtype=dtype)

    if usar_adapter:
        from peft import PeftModel
        from src.compat import parchear_torchao
        parchear_torchao()
        modelo = PeftModel.from_pretrained(modelo, adapter)
        # Fusionar los pesos LoRA: misma salida, inferencia más rápida
        modelo = modelo.merge_and_unload()

    _modelo = modelo.to(_device).eval()
    print(f"[solucion] Modelo: {config['modelo_base']} | adapter: "
          f"{adapter if usar_adapter else 'NO'} | device: {_device}")


# Generación

@torch.inference_mode()
def _generar(mensajes: list[dict]) -> str:
    """Generación determinista (greedy) a partir de mensajes de chat."""
    texto = _tokenizer.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True)
    entradas = _tokenizer(texto, return_tensors="pt").to(_device)
    salida = _modelo.generate(
        **entradas,
        max_new_tokens=MAX_NUEVOS_TOKENS,
        do_sample=False,
        temperature=None,
        top_p=None,
        top_k=None,
        repetition_penalty=1.0,
        pad_token_id=_tokenizer.eos_token_id,
    )
    nuevos = salida[0, entradas["input_ids"].shape[1]:]
    return limpiar_salida(_tokenizer.decode(nuevos, skip_special_tokens=True))


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    """
    Genera UNA consulta SELECT / WITH ... SELECT para la pregunta.
    Nunca devuelve una consulta que modifique la base.
    """
    inicio = time.time()
    sql = _generar(construir_mensajes(esquema, pregunta))

    if ejecutar is not None:
        llamadas = 0
        for _ in range(MAX_LLAMADAS_EJECUTAR):
            if es_solo_lectura(sql):
                try:
                    res = ejecutar(sql)
                except Exception as e:
                    res = {"ok": False, "error": str(e)}
                llamadas += 1
                if res.get("ok"):
                    return sql
                error = res.get("error") or "Error desconocido"
            else:
                error = "La respuesta debe ser una única consulta SELECT o WITH ... SELECT."

            if llamadas >= MAX_LLAMADAS_EJECUTAR or time.time() - inicio > LIMITE_SEGUNDOS:
                break
            sql = _generar(construir_mensajes_correccion(esquema, pregunta, sql, error))

    return sql if es_solo_lectura(sql) else SQL_RESPALDO


# El modelo se carga al importar (límite de 5 min), no en la primera pregunta (límite de 30 s)
cargar_modelo()


if __name__ == "__main__":
    esquema_demo = (
        "CREATE TABLE `clientes` (\n"
        "  `id` int NOT NULL,\n"
        "  `nombre` varchar(100) NOT NULL COMMENT 'Nombre completo',\n"
        "  `ciudad` varchar(50) DEFAULT NULL COMMENT 'Ciudad de residencia',\n"
        "  PRIMARY KEY (`id`)\n"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Clientes de la tienda'"
    )
    t = time.time()
    print(generar_sql(esquema_demo, "¿Cuántos clientes hay en cada ciudad?"))
    print(f"Tiempo: {time.time() - t:.1f} s")
