
import csv
import json
import os
import sys
from collections import Counter
from decimal import Decimal
from typing import Optional

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.mysql_utils import ejecutar, cargar_esquema, obtener_esquema


# Normalización de resultados

def _normalizar_valor(valor):
    #Normaliza un valor para comparación: redondea números a 2 decimales,
    #convierte a string los demás tipos.
    if valor is None:
        return None
    if isinstance(valor, (int, float, Decimal)):
        return round(float(valor), 2)
    if isinstance(valor, bytes):
        return valor.decode("utf-8", errors="replace")
    return str(valor)


def _normalizar_fila(fila: list) -> tuple:
    #Normaliza todos los valores de una fila
    return tuple(_normalizar_valor(v) for v in fila)


def _extraer_columnas(resultado: dict, columnas_ref: list[str]) -> dict:
    #Extrae de 'resultado' solo las columnas que están en la referencia.
    #Permite columnas adicionales sin penalizar.
    if not resultado["ok"] or not resultado["columnas"]:
        return resultado

    # Mapear nombres de columna a índices (case-insensitive)
    col_idx = {}
    for i, col in enumerate(resultado["columnas"]):
        col_idx[col.lower()] = i

    # Buscar las columnas de referencia en las del resultado
    indices = []
    cols_encontradas = []
    for ref_col in columnas_ref:
        ref_lower = ref_col.lower()
        if ref_lower in col_idx:
            indices.append(col_idx[ref_lower])
            cols_encontradas.append(ref_col)

    # Si no encontramos todas las columnas de referencia, devolver como está
    if len(cols_encontradas) < len(columnas_ref):
        return resultado

    # Filtrar las filas a solo las columnas de referencia
    filas_filtradas = []
    for fila in resultado["filas"]:
        filas_filtradas.append([fila[i] for i in indices])

    return {
        "ok": True,
        "columnas": cols_encontradas,
        "filas": filas_filtradas,
        "error": None,
    }


# Comparación de resultados

def comparar_resultados(
    filas_pred: list[list],
    filas_ref: list[list],
    requiere_orden: bool = False,
) -> bool:
    
    pred_norm = [_normalizar_fila(f) for f in filas_pred]
    ref_norm = [_normalizar_fila(f) for f in filas_ref]

    if requiere_orden:
        return pred_norm == ref_norm
    else:
        return Counter(pred_norm) == Counter(ref_norm)


# Categorización de errores

def categorizar_error(resultado_pred: dict, resultado_ref: dict) -> str:
    """
    Categoriza el tipo de error de una predicción incorrecta.

    Categorías:
    - 'sintaxis': error de sintaxis SQL
    - 'tabla_inexistente': tabla no encontrada
    - 'columna_inexistente': columna no encontrada
    - 'join_incorrecto': problema con JOIN (más o menos filas de las esperadas)
    - 'agregacion': problema con GROUP BY, HAVING, funciones de agregación
    - 'filtro': WHERE/HAVING incorrecto (mismas columnas pero valores distintos)
    - 'resultado_distinto': la consulta ejecuta pero el resultado no coincide
    - 'timeout': tiempo excedido
    - 'otro': no clasificable
    """
    if not resultado_pred["ok"]:
        error = resultado_pred["error"].lower() if resultado_pred["error"] else ""

        if "syntax" in error or "parse" in error:
            return "sintaxis"
        if "table" in error and ("doesn't exist" in error or "not found" in error):
            return "tabla_inexistente"
        if "column" in error or "unknown column" in error or "field" in error:
            return "columna_inexistente"
        if "group" in error or "full_group_by" in error or "only_full_group_by" in error:
            return "agregacion"
        if "timeout" in error or "time" in error:
            return "timeout"
        return "sintaxis"  # Error de ejecución genérico

    # La consulta ejecutó, pero el resultado no coincide
    if not resultado_ref["ok"]:
        return "otro"

    pred_filas = resultado_pred["filas"] or []
    ref_filas = resultado_ref["filas"] or []

    # Verificar si es un problema de cantidad de filas (posible JOIN)
    if len(pred_filas) != len(ref_filas):
        if len(pred_filas) > len(ref_filas) * 2 or len(pred_filas) < len(ref_filas) // 2:
            return "join_incorrecto"

    # Verificar si las columnas son diferentes
    pred_cols = set(c.lower() for c in (resultado_pred["columnas"] or []))
    ref_cols = set(c.lower() for c in (resultado_ref["columnas"] or []))
    if pred_cols != ref_cols and not ref_cols.issubset(pred_cols):
        return "columna_inexistente"

    return "resultado_distinto"

# Evaluación completa

PESOS_NIVEL = {"facil": 1, "media": 2, "dificil": 3}


def evaluar_pregunta(
    sql_pred: str,
    sql_ref: str,
    database: str,
    columnas_esperadas: list[str] | None = None,
    requiere_orden: bool = False,
) -> dict:
    #Evalúa una sola pregunta comparando la ejecución del SQL predicho
    #contra el SQL de referencia.

    #Retorna un dict con:
    # - acierto (bool)
    # - categoria_error (str o None)
    # - resultado_pred (dict)
    # - resultado_ref (dict)
    # Resultado completo: con solo 10 filas, dos consultas sin ORDER BY pueden
    # devolver subconjuntos distintos del mismo resultado (9 de las 40 preguntas tienen > 10 filas)
    resultado_ref = ejecutar(sql_ref, database, max_filas=None)
    resultado_pred = ejecutar(sql_pred, database, max_filas=None)

    # Si la referencia falla, hay un error en el test, no en la predicción
    if not resultado_ref["ok"]:
        return {
            "acierto": False,
            "categoria_error": "error_en_referencia",
            "resultado_pred": resultado_pred,
            "resultado_ref": resultado_ref,
        }

    # Si la predicción falla, categorizar el error
    if not resultado_pred["ok"]:
        return {
            "acierto": False,
            "categoria_error": categorizar_error(resultado_pred, resultado_ref),
            "resultado_pred": resultado_pred,
            "resultado_ref": resultado_ref,
        }

    # Si hay columnas esperadas, filtrar las de la predicción
    if columnas_esperadas:
        resultado_pred = _extraer_columnas(resultado_pred, columnas_esperadas)
        resultado_ref = _extraer_columnas(resultado_ref, columnas_esperadas)

    # Comparar resultados
    acierto = comparar_resultados(
        resultado_pred["filas"],
        resultado_ref["filas"],
        requiere_orden=requiere_orden,
    )

    categoria = None if acierto else categorizar_error(resultado_pred, resultado_ref)

    return {
        "acierto": acierto,
        "categoria_error": categoria,
        "resultado_pred": resultado_pred,
        "resultado_ref": resultado_ref,
    }


def evaluar_validacion(
    preguntas: list[dict],
    generar_sql_fn,
    database_map: dict[str, str],
) -> dict:
    """
    Evalúa un conjunto de preguntas de validación.

    Parámetros
    ----------
    preguntas : list[dict]
        Lista de preguntas con: id, esquema_id, pregunta, sql_referencia,
        columnas_esperadas, nivel, requiere_orden.
    generar_sql_fn : callable
        Función generar_sql(esquema, pregunta, ejecutar) -> str.
    database_map : dict
        Mapeo esquema_id -> nombre de la base de datos en MySQL.

    Retorna
    -------
    dict con:
    - resultados: lista de resultados por pregunta
    - ex_ponderado: EX ponderado global
    - ex_por_nivel: EX por nivel de dificultad
    - conteo_errores: conteo de errores por categoría
    - resumen: texto resumen
    """
    from src.mysql_utils import hacer_ejecutar

    resultados = []
    aciertos_ponderados = 0.0
    total_ponderado = 0.0
    aciertos_por_nivel = {"facil": 0, "media": 0, "dificil": 0}
    total_por_nivel = {"facil": 0, "media": 0, "dificil": 0}
    conteo_errores = {}

    for preg in preguntas:
        esquema_id = preg["esquema_id"]
        db_name = database_map[esquema_id]
        nivel = preg["nivel"]
        peso = PESOS_NIVEL.get(nivel, 1)

        # Obtener el esquema
        esquema = obtener_esquema(db_name)

        # Crear función ejecutar para esta base
        ej_fn = hacer_ejecutar(db_name)

        # Generar SQL
        try:
            sql_pred = generar_sql_fn(esquema, preg["pregunta"], ej_fn)
        except Exception as e:
            sql_pred = f"-- ERROR: {e}"

        # Evaluar
        eval_result = evaluar_pregunta(
            sql_pred=sql_pred,
            sql_ref=preg["sql_referencia"],
            database=db_name,
            columnas_esperadas=preg.get("columnas_esperadas"),
            requiere_orden=preg.get("requiere_orden", False),
        )

        total_ponderado += peso
        total_por_nivel[nivel] += peso

        if eval_result["acierto"]:
            aciertos_ponderados += peso
            aciertos_por_nivel[nivel] += peso

        if eval_result["categoria_error"]:
            cat = eval_result["categoria_error"]
            conteo_errores[cat] = conteo_errores.get(cat, 0) + 1

        resultados.append({
            "id": preg["id"],
            "nivel": nivel,
            "pregunta": preg["pregunta"],
            "sql_pred": sql_pred,
            "sql_ref": preg["sql_referencia"],
            "acierto": eval_result["acierto"],
            "categoria_error": eval_result["categoria_error"],
        })

    # Calcular métricas
    ex_ponderado = aciertos_ponderados / total_ponderado if total_ponderado > 0 else 0.0
    ex_por_nivel = {}
    for nivel in ["facil", "media", "dificil"]:
        if total_por_nivel[nivel] > 0:
            ex_por_nivel[nivel] = aciertos_por_nivel[nivel] / total_por_nivel[nivel]
        else:
            ex_por_nivel[nivel] = 0.0

    resumen = (
        f"EX ponderado: {ex_ponderado:.4f}\n"
        f"  Fácil:   {ex_por_nivel['facil']:.4f} "
        f"({aciertos_por_nivel['facil']}/{total_por_nivel['facil']})\n"
        f"  Media:   {ex_por_nivel['media']:.4f} "
        f"({aciertos_por_nivel['media']}/{total_por_nivel['media']})\n"
        f"  Difícil: {ex_por_nivel['dificil']:.4f} "
        f"({aciertos_por_nivel['dificil']}/{total_por_nivel['dificil']})\n"
        f"Errores: {conteo_errores}"
    )

    return {
        "resultados": resultados,
        "ex_ponderado": ex_ponderado,
        "ex_por_nivel": ex_por_nivel,
        "conteo_errores": conteo_errores,
        "resumen": resumen,
    }


def guardar_csv(resultados: list[dict], path: str, version: str = "baseline"):
    """Guarda los resultados de evaluación como CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "nivel", "pregunta", "sql_pred", "sql_ref",
            "acierto", "categoria_error", "version",
        ])
        writer.writeheader()
        for r in resultados:
            r_out = {**r, "version": version}
            writer.writerow(r_out)


if __name__ == "__main__":
    print("evaluador.py — Módulo de evaluación por ejecución")
    print("Importar y usar las funciones: evaluar_pregunta, evaluar_validacion")
    print()
    print("Ejemplo de uso:")
    print('  from src.evaluador import evaluar_pregunta')
    print('  result = evaluar_pregunta(sql_pred, sql_ref, "mi_base")')
    print('  print(result["acierto"], result["categoria_error"])')
