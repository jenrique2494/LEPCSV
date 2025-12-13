# 🎯 Clasificador CEFR Local

Sistema para clasificar palabras y frases en inglés según el Marco Común Europeo de Referencia (CEFR) usando análisis léxico y gramatical.

## 📋 Versiones Disponibles

### 1. **cerf_simple.py** (RECOMENDADO para empezar)
- ✅ **Funciona sin dependencias complejas**
- 📏 Usa análisis heurístico cuando no hay dependencias
- 🚀 Fácil de ejecutar
- 📄 Procesa archivos TSV

### 2. **cerf_local.py** (AVANZADO)
- 🤖 Requiere modelo neural `cefr_classifier_model_final`
- 📚 Combina análisis léxico (cefrpy) + gramatical (transformers)
- ⚖️ Usa lógica de "Ancla Dominante"
- 🔧 Requiere más dependencias

## 🚀 Inicio Rápido

### Opción 1: Ejecución Simple (Sin instalaciones)
```bash
python cerf_simple.py
```

### Opción 2: Con Dependencias Completas
```bash
# Instalar dependencias
pip install cefrpy spacy
python -m spacy download en_core_web_sm

# Ejecutar
python cerf_simple.py
```

## 💡 Uso

### 📝 Clasificar una palabra
```bash
python cerf_simple.py --word "beautiful"
```

### 📖 Clasificar una frase
```bash
python cerf_simple.py --text "This is a beautiful day"
```

### 📄 Procesar archivo TSV
```bash
# Procesar todo el archivo
python cerf_simple.py --file "tu_archivo.txt"

# Procesar solo las primeras 10 líneas (para pruebas)
python cerf_simple.py --file "tu_archivo.txt" --max-lines 10
```

### 💬 Modo interactivo
```bash
python cerf_simple.py
# Luego escribe palabras o frases cuando te lo pida
```

## 📊 Niveles CEFR

| Nivel | Descripción |
|-------|-------------|
| **A1** | Principiante |
| **A2** | Básico |
| **B1** | Intermedio |
| **B2** | Intermedio-Alto |
| **C1** | Avanzado |
| **C2** | Muy Avanzado |

## 🔧 Dependencias

### Básicas (para funcionamiento completo):
```bash
pip install cefrpy spacy
python -m spacy download en_core_web_sm
```

### Avanzadas (para modelo neural):
```bash
pip install torch transformers
```

## 📁 Estructura del Proyecto

```
4000/
├── cerf_simple.py              # ✅ Versión simplificada (USAR ESTA)
├── cerf_local.py               # 🤖 Versión completa con modelo
├── cefr_classifier_model_final/# 📦 Tu modelo entrenado (si lo tienes)
├── 4000EEnglish__1.Book copy.txt # 📄 Tu archivo a procesar
└── install_deps.bat            # 🛠️ Script de instalación
```

## 🎯 Ejemplos de Resultados

### Palabras:
- `"cat"` → **A1**
- `"beautiful"` → **B2**
- `"supremacy"` → **C1**

### Frases:
- `"I am happy"` → **A1**
- `"This is a beautiful day"` → **B2**
- `"The serendipitous discovery"` → **C1**

## 🧠 Cómo Funciona

### 1. **Análisis Heurístico** (siempre disponible)
- Usa diccionarios de palabras comunes
- Considera longitud de palabra
- Rápido y sin dependencias

### 2. **Análisis Léxico** (con cefrpy + spaCy)
- Base de datos profesional de palabras
- Análisis morfológico
- Más preciso

### 3. **Análisis Gramatical** (con modelo neural)
- Usa tu modelo entrenado
- Considera estructura de frases
- Máxima precisión

### 4. **Lógica de Ancla Dominante**
- Combina análisis léxico y gramatical
- La palabra más difícil domina el nivel final
- Ponderación inteligente

## 📝 Formato de Archivo TSV

El script espera archivos con formato:
```
columna1	columna2	columna3	palabra/frase	...	columna12(tags)
```

- **Columna 4**: Palabra o frase a analizar
- **Columna 12**: Donde se agrega el nivel CEFR

## 🔍 Solución de Problemas

### ❌ "No module named 'cefrpy'"
```bash
pip install cefrpy spacy
python -m spacy download en_core_web_sm
```

### ❌ "Modelo no encontrado"
- Asegúrate de que `cefr_classifier_model_final/` está en el directorio
- Usa `cerf_simple.py` que funciona sin modelo

### ⚠️ "Usando análisis heurístico"
- Normal si no tienes cefrpy instalado
- Resultados menos precisos pero funcionales

## 🎉 Estados del Sistema

Al ejecutar verás:
```
🎯 Clasificador CEFR Simplificado
========================================
📚 cefrpy/spaCy: ✅ (o ❌)
🤖 transformers: ✅ (o ❌)
========================================
```

- ✅ = Disponible y funcionando
- ❌ = No disponible, usando alternativas

## 🤝 Uso Recomendado

1. **Pruebas iniciales**: Usa `cerf_simple.py` sin instalaciones
2. **Análisis básico**: Instala cefrpy + spacy
3. **Análisis avanzado**: Agrega tu modelo neural
4. **Procesamiento masivo**: Usa `--max-lines` para pruebas

¡Disfruta clasificando vocabulario! 🎯
