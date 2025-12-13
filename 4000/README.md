# 🎯 Clasificador CEFR Local

Sistema para clasificar palabras y frases en inglés según el Marco Común Europeo de Referencia (CEFR) usando análisis léxico y gramatical.

## ⚡ Comandos Rápidos

```bash
# Procesar tu archivo (archivo.txt o LR.txt)
python cerf_local.py --file "archivo.txt"

# Clasificar una palabra
python cerf_local.py --word "beautiful"

# Clasificar una frase
python cerf_local.py --text "This is a beautiful day"

# Modo interactivo
python cerf_local.py
```

**Resultado:** Se genera automáticamente `archivo_CEFR_local.txt` con los niveles CEFR agregados en la columna 15.

## 📋 Versiones Disponibles

### 1. **cerf_simple.py** (BÁSICO)
- ✅ Análisis heurístico simple
- 📄 Procesa archivos TSV
- 🚀 Fácil de usar

### 2. **cerf_local.py** (RECOMENDADO - AVANZADO)
- 🤖 Modelo neural `cefr_classifier_model_final`
- 📚 Análisis léxico (cefrpy) + Análisis gramatical (transformers)
- ⚖️ Lógica de "Ancla Dominante" para resultados más precisos
- 🔧 Requiere PyTorch, transformers, spaCy
- ✅ **OPCIÓN RECOMENDADA PARA MÁXIMA PRECISIÓN**

## 🚀 Inicio Rápido

### Instalación de Dependencias
```bash
# Dependencias básicas para cerf_local.py
pip install cefrpy spacy transformers torch

# Descargar modelo de spaCy
python -m spacy download en_core_web_sm
```

### Primer Uso
```bash
# Modo interactivo
python cerf_local.py

# O procesar un archivo directamente
python cerf_local.py --file "LR.txt"
```

## 💡 Uso

### 📝 Clasificar una palabra
```bash
python cerf_local.py --word "beautiful"
```

### 📖 Clasificar una frase
```bash
python cerf_local.py --text "This is a beautiful day"
```

### 📄 Procesar archivo TSV
```bash
# Procesar todo el archivo
python cerf_local.py --file "LR.txt"

# Procesar solo las primeras 10 líneas (para pruebas)
python cerf_local.py --file "LR.txt" --max-lines 10
```

### 💬 Modo interactivo
```bash
python cerf_local.py
# Luego escribe palabras o frases cuando te lo pida
# O escribe: file:LR.txt para procesar un archivo
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

## 📁 Formato de Archivos de Entrada

### Archivos TSV (Tabulación separada)
El clasificador procesa archivos `.txt` con formato TSV:

**Estructura esperada:**
```
Col 1      Col 2      Col 3      Col 4 (PALABRA)    ...    Col 15 (TAGS)
guid       notetype   deck       palabra           ...    tags_existentes
```

**Características:**
- Delimitador: TAB (`\t`)
- Primera línea: Líneas de comentario que comienzan con `#`
- Columna 4 (índice 3): Contiene la palabra o frase a clasificar
- Columna 15 (índice 14): Donde se agregan los tags CEFR

**Ejemplo de entrada:**
```
#separator:tab
#html:true
#guid column:1
#tags column:15
yTn}SjH`!h	JPCARDS	LR::00000-1000	be	...	LR::0-1000
jxP(Y*n%:x	JPCARDS	LR::00000-1000	the	...	LR::0-1000
```

**Ejemplo de salida (después del procesamiento):**
```
yTn}SjH`!h	JPCARDS	LR::00000-1000	be	...	LR::0-1000 A1
jxP(Y*n%:x	JPCARDS	LR::00000-1000	the	...	LR::0-1000 A1
```

### Archivos generados
Cuando procesas un archivo `archivo.txt`, se genera automáticamente:
```
archivo_CEFR_local.txt    (Con los niveles CEFR agregados)
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
