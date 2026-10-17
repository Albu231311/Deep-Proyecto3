
import json
import os
import re
import sys
from pathlib import Path


def extraer_tablas_y_columnas(schema_sql: str) -> dict[str, set[str]]:
    
    #Extrae nombres de tablas y sus columnas de sentencias CREATE TABLE.

    #Retorna un dict: {nombre_tabla: {col1, col2, ...}}
    
    tablas = {}

    # Buscar cada CREATE TABLE
    pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?(\w+)[`"]?\s*\((.*?)\)\s*(?:ENGINE|COMMENT|DEFAULT|;|\Z)'
    matches = re.findall(pattern, schema_sql, re.IGNORECASE | re.DOTALL)

    for tabla_nombre, cuerpo in matches:
        columnas = set()
        # Buscar definiciones de columnas (empiezan con nombre, no con KEY, INDEX, etc.)
        lineas = cuerpo.split('\n')
        for linea in lineas:
            linea = linea.strip().rstrip(',')
            if not linea:
                continue
            # Saltar constraints
            skip_words = ['PRIMARY', 'KEY', 'INDEX', 'UNIQUE', 'FOREIGN', 'CONSTRAINT', 'CHECK']
            if any(linea.upper().startswith(w) for w in skip_words):
                continue
            # Extraer nombre de columna
            col_match = re.match(r'[`"]?(\w+)[`"]?\s+', linea)
            if col_match:
                columnas.add(col_match.group(1).lower())

        tablas[tabla_nombre.lower()] = columnas

    return tablas


def extraer_info_de_train(train_path: str) -> dict[str, set[str]]:
    
    #Extrae tablas y columnas de todas las entradas del archivo de
    #entrenamiento (train.jsonl).

    #Cada línea del JSONL tiene un campo 'esquema' con los CREATE TABLE.
    
    todas_tablas = {}

    with open(train_path, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                entry = json.loads(linea)
            except json.JSONDecodeError:
                continue

            esquema = entry.get('esquema', '')
            tablas = extraer_tablas_y_columnas(esquema)

            for tabla, cols in tablas.items():
                if tabla not in todas_tablas:
                    todas_tablas[tabla] = set()
                todas_tablas[tabla].update(cols)

    return todas_tablas


def verificar_fuga(
    esquemas_val: dict[str, dict[str, set[str]]],
    tablas_train: dict[str, set[str]],
    umbral_columnas: float = 0.6,
) -> tuple[bool, str]:

    fugas = []

    for esquema_id, tablas_val in esquemas_val.items():
        for tabla_val, cols_val in tablas_val.items():
            if tabla_val in tablas_train:
                cols_train = tablas_train[tabla_val]
                coincidencias = cols_val & cols_train
                if len(cols_val) > 0:
                    ratio = len(coincidencias) / len(cols_val)
                else:
                    ratio = 0.0

                if ratio >= umbral_columnas:
                    fugas.append({
                        "esquema": esquema_id,
                        "tabla": tabla_val,
                        "cols_val": sorted(cols_val),
                        "cols_coincidentes": sorted(coincidencias),
                        "ratio": ratio,
                    })

    hay_fuga = len(fugas) > 0

    if hay_fuga:
        lineas = [" FUGA DETECTADA — Los siguientes esquemas de validación coinciden con el entrenamiento:\n"]
        for f in fugas:
            lineas.append(
                f"  Esquema: {f['esquema']}, Tabla: {f['tabla']}\n"
                f"    Columnas de validación: {f['cols_val']}\n"
                f"    Columnas coincidentes:  {f['cols_coincidentes']}\n"
                f"    Proporción:            {f['ratio']:.0%}\n"
            )
        reporte = "\n".join(lineas)
    else:
        reporte = " Sin fuga: ningún esquema de validación coincide con el entrenamiento."

    return hay_fuga, reporte



# CLI

def main():
    #Ejecuta el chequeo de fuga desde la línea de comandos."""
    proyecto_root = Path(__file__).parent.parent

    train_path = proyecto_root / "datos" / "entrenamiento" / "train.jsonl"
    val_dir = proyecto_root / "datos" / "validacion" / "esquemas_val"

    # Verificar archivos
    if not train_path.exists():
        print(f" No se encontró {train_path}")
        print("   Primero genera el archivo de entrenamiento.")
        sys.exit(1)

    if not val_dir.exists():
        print(f" No se encontró {val_dir}")
        sys.exit(1)

    # Leer esquemas de validación
    print("Leyendo esquemas de validación...")
    esquemas_val = {}
    for sql_file in sorted(val_dir.glob("*.sql")):
        esquema_id = sql_file.stem
        with open(sql_file, 'r', encoding='utf-8') as f:
            contenido = f.read()
        esquemas_val[esquema_id] = extraer_tablas_y_columnas(contenido)
        print(f"  {esquema_id}: {len(esquemas_val[esquema_id])} tablas")

    # Leer datos de entrenamiento
    print("Leyendo datos de entrenamiento...")
    tablas_train = extraer_info_de_train(str(train_path))
    print(f"  {len(tablas_train)} tablas únicas en el entrenamiento")

    # Verificar fuga
    print("\nVerificando fuga...")
    hay_fuga, reporte = verificar_fuga(esquemas_val, tablas_train)
    print(reporte)

    if hay_fuga:
        print("\n HAY FUGA. Revisa los esquemas de validación y elimina coincidencias.")
        sys.exit(1)
    else:
        print("\n Todo limpio. Los esquemas de validación son independientes del entrenamiento.")
        sys.exit(0)


if __name__ == "__main__":
    main()
