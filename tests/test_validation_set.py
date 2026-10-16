

import json
from pathlib import Path
from src.mysql_utils import ejecutar, cargar_esquema

VAL_QUESTIONS = [
    
    # SISTEMA_ACADEMICO (20 preguntas: 8 fáciles, 7 medias, 5 difíciles)
    
    {
        "id": "val_01",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuáles son los nombres y carreras de todos los estudiantes con estado Activo?",
        "sql_referencia": "SELECT nombre, carrera FROM estudiantes WHERE estado = 'Activo'",
        "sql_ref": "SELECT nombre, carrera FROM estudiantes WHERE estado = 'Activo'",
        "columnas_esperadas": ["nombre", "carrera"],
        "requiere_orden": False
    },
    {
        "id": "val_02",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuál es el nombre y presupuesto anual de cada departamento?",
        "sql_referencia": "SELECT nombre, presupuesto_anual FROM departamentos",
        "sql_ref": "SELECT nombre, presupuesto_anual FROM departamentos",
        "columnas_esperadas": ["nombre", "presupuesto_anual"],
        "requiere_orden": False
    },
    {
        "id": "val_03",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Qué profesores tienen grado académico de Doctorado?",
        "sql_referencia": "SELECT nombre, email FROM profesores WHERE grado_academico = 'Doctorado'",
        "sql_ref": "SELECT nombre, email FROM profesores WHERE grado_academico = 'Doctorado'",
        "columnas_esperadas": ["nombre", "email"],
        "requiere_orden": False
    },
    {
        "id": "val_04",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuáles son los cursos que otorgan más de 3 créditos?",
        "sql_referencia": "SELECT codigo, nombre, creditos FROM cursos WHERE creditos > 3",
        "sql_ref": "SELECT codigo, nombre, creditos FROM cursos WHERE creditos > 3",
        "columnas_esperadas": ["codigo", "nombre", "creditos"],
        "requiere_orden": False
    },
    {
        "id": "val_05",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "Muestra el nombre y promedio acumulado de los 5 estudiantes con mejor promedio, ordenados descendentemente.",
        "sql_referencia": "SELECT nombre, promedio_acumulado FROM estudiantes ORDER BY promedio_acumulado DESC LIMIT 5",
        "sql_ref": "SELECT nombre, promedio_acumulado FROM estudiantes ORDER BY promedio_acumulado DESC LIMIT 5",
        "columnas_esperadas": ["nombre", "promedio_acumulado"],
        "requiere_orden": True
    },
    {
        "id": "val_06",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuántos estudiantes están registrados por cada estado académico?",
        "sql_referencia": "SELECT estado, COUNT(*) AS total FROM estudiantes GROUP BY estado",
        "sql_ref": "SELECT estado, COUNT(*) AS total FROM estudiantes GROUP BY estado",
        "columnas_esperadas": ["estado", "total"],
        "requiere_orden": False
    },
    {
        "id": "val_07",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Qué profesores fueron contratados después del 1 de enero de 2020?",
        "sql_referencia": "SELECT nombre, fecha_contratacion FROM profesores WHERE fecha_contratacion > '2020-01-01'",
        "sql_ref": "SELECT nombre, fecha_contratacion FROM profesores WHERE fecha_contratacion > '2020-01-01'",
        "columnas_esperadas": ["nombre", "fecha_contratacion"],
        "requiere_orden": False
    },
    {
        "id": "val_08",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuáles son los cursos del semestre 2024-1 con cupo máximo superior o igual a 25 estudiantes?",
        "sql_referencia": "SELECT codigo, nombre, cupo_maximo FROM cursos WHERE semestre = '2024-1' AND cupo_maximo >= 25",
        "sql_ref": "SELECT codigo, nombre, cupo_maximo FROM cursos WHERE semestre = '2024-1' AND cupo_maximo >= 25",
        "columnas_esperadas": ["codigo", "nombre", "cupo_maximo"],
        "requiere_orden": False
    },
    {
        "id": "val_09",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuál es el nombre de cada departamento y la cantidad de profesores adscritos?",
        "sql_referencia": "SELECT d.nombre, COUNT(p.id) AS total_profesores FROM departamentos d LEFT JOIN profesores p ON d.id = p.departamento_id GROUP BY d.id, d.nombre",
        "sql_ref": "SELECT d.nombre, COUNT(p.id) AS total_profesores FROM departamentos d LEFT JOIN profesores p ON d.id = p.departamento_id GROUP BY d.id, d.nombre",
        "columnas_esperadas": ["nombre", "total_profesores"],
        "requiere_orden": False
    },
    {
        "id": "val_10",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Qué cursos imparte cada profesor? Muestra el nombre del profesor y el nombre del curso.",
        "sql_referencia": "SELECT p.nombre AS profesor, c.nombre AS curso FROM profesores p JOIN cursos c ON p.id = c.profesor_id",
        "sql_ref": "SELECT p.nombre AS profesor, c.nombre AS curso FROM profesores p JOIN cursos c ON p.id = c.profesor_id",
        "columnas_esperadas": ["profesor", "curso"],
        "requiere_orden": False
    },
    {
        "id": "val_11",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuál es el promedio de calificaciones de los estudiantes en cada curso?",
        "sql_referencia": "SELECT c.nombre, ROUND(AVG(i.calificacion), 2) AS promedio_nota FROM cursos c JOIN inscripciones i ON c.id = i.curso_id WHERE i.calificacion IS NOT NULL GROUP BY c.id, c.nombre",
        "sql_ref": "SELECT c.nombre, ROUND(AVG(i.calificacion), 2) AS promedio_nota FROM cursos c JOIN inscripciones i ON c.id = i.curso_id WHERE i.calificacion IS NOT NULL GROUP BY c.id, c.nombre",
        "columnas_esperadas": ["nombre", "promedio_nota"],
        "requiere_orden": False
    },
    {
        "id": "val_12",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Qué departamentos tienen un salario promedio de profesores superior a 3000 USD?",
        "sql_referencia": "SELECT d.nombre, ROUND(AVG(p.salario), 2) AS salario_promedio FROM departamentos d JOIN profesores p ON d.id = p.departamento_id GROUP BY d.id, d.nombre HAVING AVG(p.salario) > 3000",
        "sql_ref": "SELECT d.nombre, ROUND(AVG(p.salario), 2) AS salario_promedio FROM departamentos d JOIN profesores p ON d.id = p.departamento_id GROUP BY d.id, d.nombre HAVING AVG(p.salario) > 3000",
        "columnas_esperadas": ["nombre", "salario_promedio"],
        "requiere_orden": False
    },
    {
        "id": "val_13",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuántos cursos tiene inscritos cada estudiante activo?",
        "sql_referencia": "SELECT e.nombre, COUNT(i.id) AS total_cursos FROM estudiantes e LEFT JOIN inscripciones i ON e.id = i.estudiante_id WHERE e.estado = 'Activo' GROUP BY e.id, e.nombre",
        "sql_ref": "SELECT e.nombre, COUNT(i.id) AS total_cursos FROM estudiantes e LEFT JOIN inscripciones i ON e.id = i.estudiante_id WHERE e.estado = 'Activo' GROUP BY e.id, e.nombre",
        "columnas_esperadas": ["nombre", "total_cursos"],
        "requiere_orden": False
    },
    {
        "id": "val_14",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "Muestra los estudiantes junto con el nombre del curso y calificación para todas las inscripciones con estado Aprobado.",
        "sql_referencia": "SELECT e.nombre AS estudiante, c.nombre AS curso, i.calificacion FROM estudiantes e JOIN inscripciones i ON e.id = i.estudiante_id JOIN cursos c ON i.curso_id = c.id WHERE i.estado = 'Aprobado'",
        "sql_ref": "SELECT e.nombre AS estudiante, c.nombre AS curso, i.calificacion FROM estudiantes e JOIN inscripciones i ON e.id = i.estudiante_id JOIN cursos c ON i.curso_id = c.id WHERE i.estado = 'Aprobado'",
        "columnas_esperadas": ["estudiante", "curso", "calificacion"],
        "requiere_orden": False
    },
    {
        "id": "val_15",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuál es el total de créditos inscritos por cada estudiante en el semestre 2024-1?",
        "sql_referencia": "SELECT e.nombre, SUM(c.creditos) AS total_creditos FROM estudiantes e JOIN inscripciones i ON e.id = i.estudiante_id JOIN cursos c ON i.curso_id = c.id WHERE c.semestre = '2024-1' GROUP BY e.id, e.nombre",
        "sql_ref": "SELECT e.nombre, SUM(c.creditos) AS total_creditos FROM estudiantes e JOIN inscripciones i ON e.id = i.estudiante_id JOIN cursos c ON i.curso_id = c.id WHERE c.semestre = '2024-1' GROUP BY e.id, e.nombre",
        "columnas_esperadas": ["nombre", "total_creditos"],
        "requiere_orden": False
    },
    {
        "id": "val_16",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "¿Qué estudiantes tienen un promedio acumulado estrictamente mayor al promedio de todos los estudiantes de su misma carrera?",
        "sql_referencia": "SELECT e1.nombre, e1.carrera, e1.promedio_acumulado FROM estudiantes e1 WHERE e1.promedio_acumulado > (SELECT AVG(e2.promedio_acumulado) FROM estudiantes e2 WHERE e2.carrera = e1.carrera)",
        "sql_ref": "SELECT e1.nombre, e1.carrera, e1.promedio_acumulado FROM estudiantes e1 WHERE e1.promedio_acumulado > (SELECT AVG(e2.promedio_acumulado) FROM estudiantes e2 WHERE e2.carrera = e1.carrera)",
        "columnas_esperadas": ["nombre", "carrera", "promedio_acumulado"],
        "requiere_orden": False
    },
    {
        "id": "val_17",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "Usando una cláusula WITH, calcula el presupuesto por profesor de cada departamento y filtra los que superan el promedio general.",
        "sql_referencia": "WITH stats AS (SELECT d.nombre, (d.presupuesto_anual / NULLIF(COUNT(p.id), 0)) AS pres_prof FROM departamentos d LEFT JOIN profesores p ON d.id = p.departamento_id GROUP BY d.id, d.nombre, d.presupuesto_anual) SELECT nombre, ROUND(pres_prof, 2) AS presupuesto_por_profesor FROM stats WHERE pres_prof > (SELECT AVG(pres_prof) FROM stats WHERE pres_prof IS NOT NULL)",
        "sql_ref": "WITH stats AS (SELECT d.nombre, (d.presupuesto_anual / NULLIF(COUNT(p.id), 0)) AS pres_prof FROM departamentos d LEFT JOIN profesores p ON d.id = p.departamento_id GROUP BY d.id, d.nombre, d.presupuesto_anual) SELECT nombre, ROUND(pres_prof, 2) AS presupuesto_por_profesor FROM stats WHERE pres_prof > (SELECT AVG(pres_prof) FROM stats WHERE pres_prof IS NOT NULL)",
        "columnas_esperadas": ["nombre", "presupuesto_por_profesor"],
        "requiere_orden": False
    },
    {
        "id": "val_18",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "Genera el ranking de estudiantes dentro de cada carrera según su promedio acumulado usando funciones de ventana, ordenados por carrera y posición.",
        "sql_referencia": "SELECT carrera, nombre, promedio_acumulado, DENSE_RANK() OVER (PARTITION BY carrera ORDER BY promedio_acumulado DESC) AS ranking_carrera FROM estudiantes ORDER BY carrera, ranking_carrera",
        "sql_ref": "SELECT carrera, nombre, promedio_acumulado, DENSE_RANK() OVER (PARTITION BY carrera ORDER BY promedio_acumulado DESC) AS ranking_carrera FROM estudiantes ORDER BY carrera, ranking_carrera",
        "columnas_esperadas": ["carrera", "nombre", "promedio_acumulado", "ranking_carrera"],
        "requiere_orden": True
    },
    {
        "id": "val_19",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "¿Qué profesores ganan un salario superior al promedio de salarios de su respectivo departamento?",
        "sql_referencia": "SELECT p.nombre, p.salario, p.departamento_id FROM profesores p WHERE p.salario > (SELECT AVG(p2.salario) FROM profesores p2 WHERE p2.departamento_id = p.departamento_id)",
        "sql_ref": "SELECT p.nombre, p.salario, p.departamento_id FROM profesores p WHERE p.salario > (SELECT AVG(p2.salario) FROM profesores p2 WHERE p2.departamento_id = p.departamento_id)",
        "columnas_esperadas": ["nombre", "salario", "departamento_id"],
        "requiere_orden": False
    },
    {
        "id": "val_20",
        "esquema_id": "sistema_academico",
        "db_id": "sistema_academico",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "¿Cuál es la antigüedad calculada en años para cada profesor respecto al 2026-10-23, ordenados de mayor a menor?",
        "sql_referencia": "SELECT nombre, TIMESTAMPDIFF(YEAR, fecha_contratacion, '2026-10-23') AS antiguedad_anios FROM profesores ORDER BY antiguedad_anios DESC",
        "sql_ref": "SELECT nombre, TIMESTAMPDIFF(YEAR, fecha_contratacion, '2026-10-23') AS antiguedad_anios FROM profesores ORDER BY antiguedad_anios DESC",
        "columnas_esperadas": ["nombre", "antiguedad_anios"],
        "requiere_orden": True
    },

    
    # CLINICA_SALUD (20 preguntas: 7 fáciles, 8 medias, 5 difíciles)
    
    {
        "id": "val_21",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuáles son los médicos activos junto con su especialidad?",
        "sql_referencia": "SELECT nombre, especialidad FROM medicos WHERE activo = TRUE",
        "sql_ref": "SELECT nombre, especialidad FROM medicos WHERE activo = TRUE",
        "columnas_esperadas": ["nombre", "especialidad"],
        "requiere_orden": False
    },
    {
        "id": "val_22",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Qué medicamentos tienen un precio menor a 50 quetzales?",
        "sql_referencia": "SELECT nombre, precio, presentacion FROM medicamentos WHERE precio < 50",
        "sql_ref": "SELECT nombre, precio, presentacion FROM medicamentos WHERE precio < 50",
        "columnas_esperadas": ["nombre", "precio", "presentacion"],
        "requiere_orden": False
    },
    {
        "id": "val_23",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuáles son los pacientes de género femenino registrados en la clínica?",
        "sql_referencia": "SELECT nombre, fecha_nac, telefono FROM pacientes WHERE genero = 'F'",
        "sql_ref": "SELECT nombre, fecha_nac, telefono FROM pacientes WHERE genero = 'F'",
        "columnas_esperadas": ["nombre", "fecha_nac", "telefono"],
        "requiere_orden": False
    },
    {
        "id": "val_24",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Cuántas citas médicas hay registradas para cada estado?",
        "sql_referencia": "SELECT estado, COUNT(*) AS total_citas FROM citas GROUP BY estado",
        "sql_ref": "SELECT estado, COUNT(*) AS total_citas FROM citas GROUP BY estado",
        "columnas_esperadas": ["estado", "total_citas"],
        "requiere_orden": False
    },
    {
        "id": "val_25",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "Muestra el nombre, principio activo y stock de los 5 medicamentos con mayor inventario disponible, de mayor a menor.",
        "sql_referencia": "SELECT nombre, principio_activo, stock FROM medicamentos ORDER BY stock DESC LIMIT 5",
        "sql_ref": "SELECT nombre, principio_activo, stock FROM medicamentos ORDER BY stock DESC LIMIT 5",
        "columnas_esperadas": ["nombre", "principio_activo", "stock"],
        "requiere_orden": True
    },
    {
        "id": "val_26",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿En qué piso y con qué extensión se encuentra cada departamento médico?",
        "sql_referencia": "SELECT nombre, piso, extension FROM departamentos_med",
        "sql_ref": "SELECT nombre, piso, extension FROM departamentos_med",
        "columnas_esperadas": ["nombre", "piso", "extension"],
        "requiere_orden": False
    },
    {
        "id": "val_27",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "facil",
        "peso": 1,
        "pregunta": "¿Qué pacientes tienen tipo de sangre 'O+'?",
        "sql_referencia": "SELECT nombre, tipo_sangre, telefono FROM pacientes WHERE tipo_sangre = 'O+'",
        "sql_ref": "SELECT nombre, tipo_sangre, telefono FROM pacientes WHERE tipo_sangre = 'O+'",
        "columnas_esperadas": ["nombre", "tipo_sangre", "telefono"],
        "requiere_orden": False
    },
    {
        "id": "val_28",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuántos médicos pertenecen a cada departamento médico?",
        "sql_referencia": "SELECT d.nombre, COUNT(m.id) AS total_medicos FROM departamentos_med d LEFT JOIN medicos m ON d.id = m.departamento_id GROUP BY d.id, d.nombre",
        "sql_ref": "SELECT d.nombre, COUNT(m.id) AS total_medicos FROM departamentos_med d LEFT JOIN medicos m ON d.id = m.departamento_id GROUP BY d.id, d.nombre",
        "columnas_esperadas": ["nombre", "total_medicos"],
        "requiere_orden": False
    },
    {
        "id": "val_29",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "Muestra el nombre del paciente, el médico que lo atendió y la fecha de cada cita con estado Completada.",
        "sql_referencia": "SELECT p.nombre AS paciente, m.nombre AS medico, c.fecha_hora FROM citas c JOIN pacientes p ON c.paciente_id = p.id JOIN medicos m ON c.medico_id = m.id WHERE c.estado = 'Completada'",
        "sql_ref": "SELECT p.nombre AS paciente, m.nombre AS medico, c.fecha_hora FROM citas c JOIN pacientes p ON c.paciente_id = p.id JOIN medicos m ON c.medico_id = m.id WHERE c.estado = 'Completada'",
        "columnas_esperadas": ["paciente", "medico", "fecha_hora"],
        "requiere_orden": False
    },
    {
        "id": "val_30",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuál es el costo promedio de las citas atendidas por cada especialidad médica?",
        "sql_referencia": "SELECT m.especialidad, ROUND(AVG(c.costo), 2) AS costo_promedio FROM medicos m JOIN citas c ON m.id = c.medico_id WHERE c.costo IS NOT NULL GROUP BY m.especialidad",
        "sql_ref": "SELECT m.especialidad, ROUND(AVG(c.costo), 2) AS costo_promedio FROM medicos m JOIN citas c ON m.id = c.medico_id WHERE c.costo IS NOT NULL GROUP BY m.especialidad",
        "columnas_esperadas": ["especialidad", "costo_promedio"],
        "requiere_orden": False
    },
    {
        "id": "val_31",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Qué médicos han atendido más de una cita completada?",
        "sql_referencia": "SELECT m.nombre, COUNT(c.id) AS total_atendidas FROM medicos m JOIN citas c ON m.id = c.medico_id WHERE c.estado = 'Completada' GROUP BY m.id, m.nombre HAVING COUNT(c.id) > 1",
        "sql_ref": "SELECT m.nombre, COUNT(c.id) AS total_atendidas FROM medicos m JOIN citas c ON m.id = c.medico_id WHERE c.estado = 'Completada' GROUP BY m.id, m.nombre HAVING COUNT(c.id) > 1",
        "columnas_esperadas": ["nombre", "total_atendidas"],
        "requiere_orden": False
    },
    {
        "id": "val_32",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Qué medicamentos y cuántas unidades totales han sido recetadas en las consultas?",
        "sql_referencia": "SELECT m.nombre, SUM(r.cantidad) AS total_unidades_recetadas FROM medicamentos m JOIN recetas r ON m.id = r.medicamento_id GROUP BY m.id, m.nombre",
        "sql_ref": "SELECT m.nombre, SUM(r.cantidad) AS total_unidades_recetadas FROM medicamentos m JOIN recetas r ON m.id = r.medicamento_id GROUP BY m.id, m.nombre",
        "columnas_esperadas": ["nombre", "total_unidades_recetadas"],
        "requiere_orden": False
    },
    {
        "id": "val_33",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Cuál es el monto total facturado en citas por cada médico en la clínica?",
        "sql_referencia": "SELECT m.nombre, COALESCE(SUM(c.costo), 0) AS total_facturado FROM medicos m LEFT JOIN citas c ON m.id = c.medico_id WHERE c.estado = 'Completada' GROUP BY m.id, m.nombre",
        "sql_ref": "SELECT m.nombre, COALESCE(SUM(c.costo), 0) AS total_facturado FROM medicos m LEFT JOIN citas c ON m.id = c.medico_id WHERE c.estado = 'Completada' GROUP BY m.id, m.nombre",
        "columnas_esperadas": ["nombre", "total_facturado"],
        "requiere_orden": False
    },
    {
        "id": "val_34",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Qué pacientes han tenido al menos una cita con costo superior a 250 quetzales?",
        "sql_referencia": "SELECT DISTINCT p.nombre, p.telefono FROM pacientes p JOIN citas c ON p.id = c.paciente_id WHERE c.costo > 250",
        "sql_ref": "SELECT DISTINCT p.nombre, p.telefono FROM pacientes p JOIN citas c ON p.id = c.paciente_id WHERE c.costo > 250",
        "columnas_esperadas": ["nombre", "telefono"],
        "requiere_orden": False
    },
    {
        "id": "val_35",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "media",
        "peso": 2,
        "pregunta": "¿Qué departamentos médicos tienen un salario promedio en su personal médico superior a 15000 quetzales?",
        "sql_referencia": "SELECT d.nombre, ROUND(AVG(m.salario), 2) AS salario_promedio FROM departamentos_med d JOIN medicos m ON d.id = m.departamento_id GROUP BY d.id, d.nombre HAVING AVG(m.salario) > 15000",
        "sql_ref": "SELECT d.nombre, ROUND(AVG(m.salario), 2) AS salario_promedio FROM departamentos_med d JOIN medicos m ON d.id = m.departamento_id GROUP BY d.id, d.nombre HAVING AVG(m.salario) > 15000",
        "columnas_esperadas": ["nombre", "salario_promedio"],
        "requiere_orden": False
    },
    {
        "id": "val_36",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "¿Qué pacientes han gastado en citas un total mayor al gasto promedio de todos los pacientes que han asistido a citas completadas?",
        "sql_referencia": "SELECT p.nombre, SUM(c.costo) AS gasto_total FROM pacientes p JOIN citas c ON p.id = c.paciente_id WHERE c.estado = 'Completada' GROUP BY p.id, p.nombre HAVING SUM(c.costo) > (SELECT AVG(sub.total_gasto) FROM (SELECT SUM(c2.costo) AS total_gasto FROM citas c2 WHERE c2.estado = 'Completada' GROUP BY c2.paciente_id) sub)",
        "sql_ref": "SELECT p.nombre, SUM(c.costo) AS gasto_total FROM pacientes p JOIN citas c ON p.id = c.paciente_id WHERE c.estado = 'Completada' GROUP BY p.id, p.nombre HAVING SUM(c.costo) > (SELECT AVG(sub.total_gasto) FROM (SELECT SUM(c2.costo) AS total_gasto FROM citas c2 WHERE c2.estado = 'Completada' GROUP BY c2.paciente_id) sub)",
        "columnas_esperadas": ["nombre", "gasto_total"],
        "requiere_orden": False
    },
    {
        "id": "val_37",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "Usando CTE con la cláusula WITH, calcula el valor total del inventario de medicamentos (precio * stock) por presentación y muestra las presentaciones que superan 2000 quetzales.",
        "sql_referencia": "WITH inventario_pres AS (SELECT presentacion, SUM(precio * stock) AS valor_total FROM medicamentos GROUP BY presentacion) SELECT presentacion, ROUND(valor_total, 2) AS valor_total FROM inventario_pres WHERE valor_total > 2000",
        "sql_ref": "WITH inventario_pres AS (SELECT presentacion, SUM(precio * stock) AS valor_total FROM medicamentos GROUP BY presentacion) SELECT presentacion, ROUND(valor_total, 2) AS valor_total FROM inventario_pres WHERE valor_total > 2000",
        "columnas_esperadas": ["presentacion", "valor_total"],
        "requiere_orden": False
    },
    {
        "id": "val_38",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "Clasifica el salario de los médicos dentro de cada departamento médico usando la función de ventana DENSE_RANK(), ordenando por departamento y puesto salarial.",
        "sql_referencia": "SELECT d.nombre AS departamento, m.nombre AS medico, m.salario, DENSE_RANK() OVER (PARTITION BY m.departamento_id ORDER BY m.salario DESC) AS rango_salario FROM medicos m JOIN departamentos_med d ON m.departamento_id = d.id ORDER BY departamento, rango_salario",
        "sql_ref": "SELECT d.nombre AS departamento, m.nombre AS medico, m.salario, DENSE_RANK() OVER (PARTITION BY m.departamento_id ORDER BY m.salario DESC) AS rango_salario FROM medicos m JOIN departamentos_med d ON m.departamento_id = d.id ORDER BY departamento, rango_salario",
        "columnas_esperadas": ["departamento", "medico", "salario", "rango_salario"],
        "requiere_orden": True
    },
    {
        "id": "val_39",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "¿Qué médicos tienen un salario superior al salario promedio de los médicos de su respectivo departamento médico?",
        "sql_referencia": "SELECT m1.nombre, m1.salario, m1.departamento_id FROM medicos m1 WHERE m1.salario > (SELECT AVG(m2.salario) FROM medicos m2 WHERE m2.departamento_id = m1.departamento_id)",
        "sql_ref": "SELECT m1.nombre, m1.salario, m1.departamento_id FROM medicos m1 WHERE m1.salario > (SELECT AVG(m2.salario) FROM medicos m2 WHERE m2.departamento_id = m1.departamento_id)",
        "columnas_esperadas": ["nombre", "salario", "departamento_id"],
        "requiere_orden": False
    },
    {
        "id": "val_40",
        "esquema_id": "clinica_salud",
        "db_id": "clinica_salud",
        "nivel": "dificil",
        "peso": 3,
        "pregunta": "¿Cuál es la edad en años de cada paciente calculada al 2026-10-23, ordenados de mayor a menor edad?",
        "sql_referencia": "SELECT nombre, TIMESTAMPDIFF(YEAR, fecha_nac, '2026-10-23') AS edad_anios FROM pacientes ORDER BY edad_anios DESC",
        "sql_ref": "SELECT nombre, TIMESTAMPDIFF(YEAR, fecha_nac, '2026-10-23') AS edad_anios FROM pacientes ORDER BY edad_anios DESC",
        "columnas_esperadas": ["nombre", "edad_anios"],
        "requiere_orden": True
    }
]


def test_and_save():
    print(f"Total de preguntas en el conjunto de validación: {len(VAL_QUESTIONS)}")
    niveles = {"facil": 0, "media": 0, "dificil": 0}
    esquemas = {"sistema_academico": 0, "clinica_salud": 0}
    
    for q in VAL_QUESTIONS:
        niveles[q["nivel"]] += 1
        esquemas[q["esquema_id"]] += 1

    print("Distribución por nivel:", niveles)
    print("Distribución por esquema:", esquemas)
    assert len(VAL_QUESTIONS) == 40, "Deben ser exactamente 40 preguntas"
    assert niveles["facil"] == 15, "Deben ser 15 fáciles"
    assert niveles["media"] == 15, "Deben ser 15 medias"
    assert niveles["dificil"] == 10, "Deben ser 10 difíciles"

    # Validar ejecución de cada consulta en MySQL
    fallos = 0
    for q in VAL_QUESTIONS:
        res = ejecutar(q["sql_referencia"], q["esquema_id"])
        if not res["ok"]:
            print(f"   FALLÓ {q['id']} ({q['esquema_id']}): {res['error']}")
            fallos += 1
        else:
            num_filas = len(res["filas"])
            print(f" {q['id']} ({q['esquema_id']} - {q['nivel']}): {num_filas} filas")

    if fallos > 0:
        raise RuntimeError(f"{fallos} consultas fallaron en MySQL")

    print("\n¡Todas las 40 consultas ejecutaron con éxito en MySQL 8.4.10! 🎉")

    # Guardar en datos/validacion/val.jsonl
    val_path = Path("datos/validacion/val.jsonl")
    with open(val_path, "w", encoding="utf-8") as f:
        for q in VAL_QUESTIONS:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"Guardado exitoso en {val_path}")


if __name__ == "__main__":
    test_and_save()
