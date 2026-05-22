# SATCS — Dashboard de Detección de Anomalías
## Sistema de Alerta Temprana en Contratación Pública · Sector Salud · Colombia

Prototipo MVP para walkthrough guiado con auditoras.

---

## 🚀 Instalación y ejecución (VS Code local)

### Requisitos
- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar el dashboard
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 🌐 Despliegue en Streamlit Cloud (opcional)

1. Sube esta carpeta a un repositorio GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo y selecciona `app.py` como archivo principal
4. Deploy — cualquier usuario accede por URL sin instalar nada

---

## 📁 Estructura del proyecto

```
satcs_dashboard/
├── app.py              ← Dashboard principal (todo autocontenido)
├── requirements.txt    ← Dependencias Python
└── README.md           ← Este archivo
```

> **Nota:** Los datos están embebidos directamente en `app.py` (Top-15 SECOP real + scores simulados).
> Para conectar a datos reales, reemplaza la función `cargar_datos()` con una lectura de CSV/BD.

---

## 🗂️ Funcionalidades del MVP

| Componente | Descripción |
|---|---|
| **Filtros sidebar** | Período, departamento, modalidad, nivel de riesgo, score mínimo |
| **KPIs** | Contratos analizados, alertas, riesgo alto, valor total, ahorro potencial |
| **Mapa territorial** | Burbujas por departamento coloreadas por score promedio |
| **Tabla interactiva** | Top-15 priorizados, clic para seleccionar |
| **Panel de explicación** | Ficha del contrato + factores de alerta + radar de scores |
| **Análisis comparativo** | Histograma, pie, barras por depto, scatter por modalidad |

---

## 📌 Guión de walkthrough sugerido (20 min)

1. **Intro (3 min):** Mostrar KPIs globales, explicar qué mide el score
2. **Mapa (3 min):** Identificar departamentos críticos (Boyacá, Casanare, Bogotá)
3. **Tabla (4 min):** Ordenar por score, señalar Caso #1 (score 0.952)
4. **Panel de explicación (5 min):** Clic en Caso #1, recorrer factores + radar
5. **Filtros (3 min):** Demostrar filtrado por departamento y modalidad
6. **Q&A + feedback (2 min)**

---

*SATCS v0.1 · Solo para uso interno · No para publicación*
