# -*- coding: utf-8 -*-
"""
Clasificador CEFR Local - Versión adaptada del script de Google Colab
Usa modelo local cefr_classifier_model_final y análisis combinado léxico + gramatical

Requiere:
- cefrpy, spacy, transformers, torch
- Modelo local: cefr_classifier_model_final/
- spaCy modelo: en_core_web_sm

Uso:
    python cerf_local.py
"""

import json
import torch
import os
import sys
import argparse
from pathlib import Path

# Verificar dependencias
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from cefrpy import CEFRAnalyzer, CEFRSpaCyAnalyzer
    import spacy
    HAS_DEPS = True
except ImportError as e:
    print(f"❌ Dependencias faltantes: {e}")
    print("📦 Instala con:")
    print("  pip install cefrpy spacy transformers torch")
    print("  python -m spacy download en_core_web_sm")
    HAS_DEPS = False
    sys.exit(1)

# Cargar modelo de spaCy
def load_spacy_model():
    """Carga el modelo de spaCy"""
    try:
        nlp = spacy.load("en_core_web_sm")
        print("✅ Modelo spaCy cargado correctamente")
        return nlp
    except OSError:
        print("❌ Modelo 'en_core_web_sm' no encontrado.")
        print("📦 Ejecuta: python -m spacy download en_core_web_sm")
        return None

# Cargar spaCy
nlp = load_spacy_model()
if nlp is None:
    print("⚠️  Continuando sin spaCy...")

# Buscar modelo local
def find_model_path():
    """Busca el modelo en rutas posibles"""
    possible_paths = [
        "./cefr_classifier_model_final",
        "../cefr_classifier_model_final", 
        "./4000/cefr_classifier_model_final",
        "cefr_classifier_model_final",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Modelo encontrado en: {path}")
            return path
    
    print("❌ Modelo no encontrado en las rutas esperadas")
    print("💡 Asegúrate de que 'cefr_classifier_model_final' esté en el directorio actual")
    return None

def clasificar_palabra(palabra: str):
    """
    Clasifica una palabra individual en su nivel CEFR.
    """
    print(f"🔍 Análisis de la palabra: '{palabra}'")
    
    if not HAS_DEPS:
        return get_heuristic_level(palabra)
    
    try:
        analyzer = CEFRAnalyzer()
        nivel_promedio = analyzer.get_average_word_level_CEFR(palabra)

        if nivel_promedio:
            # El resultado es un enum CEFRLevel, acceder al nombre directamente
            nivel_cefr = nivel_promedio.name
            nivel_numerico = nivel_promedio.value
            
            print(f"✅ Nivel CEFR: {nivel_cefr} (puntuación: {nivel_numerico})")
            print("-" * 40)
            return nivel_cefr
        else:
            print("⚠️  Palabra no encontrada en la base de datos cefrpy")
            heuristic_level = get_heuristic_level(palabra)
            print(f"📏 Nivel heurístico: {heuristic_level}")
            print("-" * 40)
            return heuristic_level
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return get_heuristic_level(palabra)

def get_heuristic_level(word):
    """Nivel CEFR heurístico basado en longitud y frecuencia"""
    word = word.lower().strip()
    
    # Palabras muy básicas A1
    a1_words = {
        'the', 'a', 'an', 'and', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'good', 'bad', 'big', 'small', 'new', 'old', 'hot', 'cold', 'go', 'come',
        'eat', 'drink', 'see', 'look', 'like', 'want', 'need', 'home', 'time', 'day'
    }
    
    # Palabras básicas A2
    a2_words = {
        'about', 'after', 'again', 'because', 'different', 'important', 'often',
        'through', 'young', 'large', 'write', 'world', 'work', 'family', 'friend'
    }
    
    if word in a1_words:
        return 'A1'
    elif word in a2_words:
        return 'A2'
    else:
        # Usar longitud como heurística
        length = len(word)
        if length <= 4:
            return 'A1'
        elif length <= 6:
            return 'A2'
        elif length <= 8:
            return 'B1'
        elif length <= 10:
            return 'B2'
        else:
            return 'C1'


def clasificar_frase_con_anclaje_dominante(frase: str, classifier):
    """
    Clasifica una frase utilizando la lógica de "Ancla Dominante".
    La dominancia (léxica o gramatical) se determina por el nivel más alto.
    """
    print(f"🔍 Análisis con Anclaje Dominante: '{frase}'")

    LEVEL_TO_NUM = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
    NUM_TO_LEVEL = {num: level for level, num in LEVEL_TO_NUM.items()}

    # --- 1. Análisis Léxico para encontrar la palabra de MÁS alto nivel ---
    lexical_anchor_num = 0
    palabras_analizadas = []
    
    if HAS_DEPS and nlp:
        try:
            cefr_word_analyzer = CEFRAnalyzer()
            analyzer = CEFRSpaCyAnalyzer(cefr_word_analyzer)
            doc = nlp(frase)
            resultado_analisis = analyzer.analize_doc(doc)

            print("\n📚 Análisis léxico por palabra:")
            for token, token_info in zip(doc, resultado_analisis):
                if token.is_punct or token.is_space:
                    continue
                    
                palabra = token_info[0]
                nivel_numerico = token_info[3]  # Esto es un float
                
                if nivel_numerico is not None and nivel_numerico > 0:
                    if nivel_numerico > lexical_anchor_num:
                        lexical_anchor_num = nivel_numerico
                    nivel_cefr = NUM_TO_LEVEL.get(round(nivel_numerico), f"N{nivel_numerico}")
                    palabras_analizadas.append((palabra, nivel_cefr))
                    print(f"  {palabra:<15} → {nivel_cefr}")
                else:
                    print(f"  {palabra:<15} → No encontrada")
        except Exception as e:
            print(f"⚠️  Error en análisis léxico: {e}")
    
    if lexical_anchor_num == 0:
        print("⚠️  No se encontraron palabras con nivel CEFR, usando heurística")
        # Usar análisis heurístico para toda la frase
        words = [w for w in frase.split() if w.isalpha()]
        if words:
            heuristic_levels = [LEVEL_TO_NUM.get(get_heuristic_level(word), 1) for word in words]
            lexical_anchor_num = max(heuristic_levels) if heuristic_levels else 1
        else:
            lexical_anchor_num = 1
        lexical_anchor_tag = NUM_TO_LEVEL.get(round(lexical_anchor_num), "A1")
    else:
        # lexical_anchor_num ya es un número directo
        lexical_anchor_tag = NUM_TO_LEVEL.get(round(lexical_anchor_num), "A1")

    print(f"\n📈 Ancla Léxica Dominante: {lexical_anchor_tag} ({lexical_anchor_num:.2f})")

    # --- 2. Obtener la "Pista Gramatical" usando el clasificador ---
    grammatical_hint_num = 1
    top_grammatical_level_tag = "A1"
    
    if classifier:
        try:
            grammatical_scores = json.loads(classifier.predict(frase))
            top_grammatical_level_tag = max(grammatical_scores, key=grammatical_scores.get)
            grammatical_hint_num = LEVEL_TO_NUM.get(top_grammatical_level_tag, 1)
            confidence = grammatical_scores[top_grammatical_level_tag]
            print(f"🤖 Análisis Gramatical: {top_grammatical_level_tag} (confianza: {confidence:.3f})")
        except Exception as e:
            print(f"⚠️  Error en análisis gramatical: {e}")
            print(f"🤖 Análisis Gramatical: {top_grammatical_level_tag} (fallback)")
    else:
        print(f"🤖 Análisis Gramatical: {top_grammatical_level_tag} (clasificador no disponible)")

    # --- 3. Combinar con Ponderación Condicional ---
    if lexical_anchor_num >= grammatical_hint_num:
        lexical_weight = 0.85
        grammatical_weight = 0.15
        dominance = "📚 Léxico"
    else:
        lexical_weight = 0.25
        grammatical_weight = 0.75
        dominance = "🤖 Gramática"

    final_score = (lexical_anchor_num * lexical_weight) + (grammatical_hint_num * grammatical_weight)
    closest_level = min(LEVEL_TO_NUM, key=lambda level: abs(LEVEL_TO_NUM[level] - final_score))
    final_level_tag = closest_level

    print(f"\n🎯 Dominancia: {dominance}")
    print(f"⚖️  Pesos → Léxico: {lexical_weight:.0%}, Gramática: {grammatical_weight:.0%}")
    print("-" * 50)
    print(f"✅ NIVEL FINAL: {final_level_tag}")
    print(f"📊 Puntaje final: {final_score:.2f}")
    print("-" * 50)

    return final_level_tag


# ==============================================================================
# CLASE PARA INFERENCIA Y PREDICCIÓN
# ==============================================================================
print("🔧 Configurando clasificador CEFR...")

class CEFRClassifier:
    def __init__(self, model_path):
        """
        Inicializa el clasificador cargando el modelo y el tokenizador desde una ruta local.
        """
        if not HAS_DEPS:
            raise ImportError("Dependencias de transformers no disponibles")
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            print(f"📂 Cargando modelo desde: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Clasificador cargado en: {self.device}")
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            raise

    def predict(self, sentence: str) -> str:
        """
        Predice las probabilidades del nivel CEFR para una oración y devuelve un JSON.
        """
        # Tokenizar la oración de entrada
        inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Realizar la inferencia sin calcular gradientes para mayor eficiencia
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Los 'logits' son las puntuaciones brutas del modelo para cada clase
        logits = outputs.logits

        # Aplicar la función softmax para convertir los logits en una distribución de probabilidad
        probabilities = torch.nn.functional.softmax(logits, dim=-1).squeeze()

        # Crear el diccionario de salida con las probabilidades para cada nivel
        prob_dict = {
            self.model.config.id2label[i]: prob.item()
            for i, prob in enumerate(probabilities)
        }

        # Devolver el resultado como una cadena JSON formateada
        return json.dumps(prob_dict, indent=4)

# Inicializar el clasificador
classifier = None
model_path = find_model_path()

if model_path and HAS_DEPS:
    try:
        classifier = CEFRClassifier(model_path)
        print("🎉 Clasificador inicializado correctamente")
    except Exception as e:
        print(f"⚠️  Error inicializando clasificador: {e}")
        print("📚 Continuando solo con análisis léxico...")
        classifier = None
else:
    print("⚠️  Modelo no encontrado o dependencias faltantes")
    print("📚 Continuando solo con análisis léxico...")

# ==============================================================================
# FUNCIONES PRINCIPALES
# ==============================================================================
def obtener_nivel_mcerr(texto):
    """
    Clasifica una frase utilizando la lógica de "Ancla Dominante".
    """
    if classifier is None:
        print("⚠️  Clasificador neural no disponible, usando solo análisis léxico")
        # Fallback a análisis léxico simple
        if HAS_DEPS and nlp:
            return clasificar_frase_con_anclaje_dominante(texto, None)
        else:
            # Análisis heurístico para frases
            words = [w for w in texto.split() if w.isalpha()]
            if words:
                levels = [get_heuristic_level(word) for word in words]
                LEVEL_TO_NUM = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
                level_nums = [LEVEL_TO_NUM.get(level, 1) for level in levels]
                max_level = max(level_nums)
                NUM_TO_LEVEL = {v: k for k, v in LEVEL_TO_NUM.items()}
                return NUM_TO_LEVEL.get(max_level, 'A1')
            return 'A1'
    
    return clasificar_frase_con_anclaje_dominante(texto, classifier)

def clasificar_texto_auto(texto):
    """
    Clasifica el texto como palabra o frase y llama a la función apropiada.
    """
    texto = texto.strip()
    
    if " " in texto:
        print("📖 Detectado como frase")
        return obtener_nivel_mcerr(texto)
    else:
        print("📝 Detectado como palabra")
        return clasificar_palabra(texto)

def procesar_archivo_tsv(archivo_path, max_lines=None):
    """
    Procesa un archivo TSV y agrega niveles CEFR a la columna 15 (tags)
    """
    print(f"📁 Procesando archivo: {archivo_path}")
    
    if not os.path.exists(archivo_path):
        print(f"❌ Archivo no encontrado: {archivo_path}")
        return
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        lineas_procesadas = []
        procesadas = 0
        
        for i, linea in enumerate(lineas):
            if max_lines and procesadas >= max_lines:
                lineas_procesadas.extend(lineas[i:])  # Agregar líneas restantes sin procesar
                break
                
            linea = linea.rstrip('\n\r')
            
            # Procesar solo líneas que no sean comentarios
            if linea.startswith('#') or not linea.strip():
                lineas_procesadas.append(linea)
                continue
            
            columnas = linea.split('\t')
            
            # Verificar que tiene al menos 15 columnas (para columna de tags)
            if len(columnas) >= 15:
                palabra_frase = columnas[3].strip()  # Columna 4 (índice 3) contiene la palabra
                
                if palabra_frase:
                    print(f"\n{'='*60}")
                    print(f"📊 Procesando {procesadas + 1}: {palabra_frase}")
                    print(f"{'='*60}")
                    
                    nivel_cefr = clasificar_texto_auto(palabra_frase)
                    
                    # Agregar a columna 15 (índice 14) - columna de tags
                    tags_existentes = columnas[14].strip()
                    if tags_existentes:
                        columnas[14] = tags_existentes + ' ' + nivel_cefr
                    else:
                        columnas[14] = nivel_cefr
                    
                    procesadas += 1
                    print(f"✅ → {nivel_cefr}")
                
                lineas_procesadas.append('\t'.join(columnas))
            else:
                # Si no tiene suficientes columnas, agregar columnas vacías hasta llegar a 15
                while len(columnas) < 15:
                    columnas.append('')
                
                palabra_frase = columnas[3].strip()
                if palabra_frase:
                    print(f"\n{'='*60}")
                    print(f"📊 Procesando {procesadas + 1}: {palabra_frase}")
                    print(f"{'='*60}")
                    
                    nivel_cefr = clasificar_texto_auto(palabra_frase)
                    columnas[14] = nivel_cefr
                    
                    procesadas += 1
                    print(f"✅ → {nivel_cefr}")
                
                lineas_procesadas.append('\t'.join(columnas))
        
        # Guardar archivo procesado
        base_name = os.path.splitext(archivo_path)[0]
        archivo_salida = f"{base_name}_CEFR_local.txt"
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            for linea in lineas_procesadas:
                f.write(linea + '\n')
        
        print(f"\n🎉 ¡Procesamiento completado!")
        print(f"📊 Entradas procesadas: {procesadas}")
        print(f"💾 Archivo guardado como: {archivo_salida}")
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")

def main():
    """Función principal con interfaz de línea de comandos"""
    parser = argparse.ArgumentParser(description='Clasificador CEFR Local')
    parser.add_argument('--word', '-w', help='Palabra a clasificar')
    parser.add_argument('--text', '-t', help='Frase a clasificar')
    parser.add_argument('--file', '-f', help='Archivo TSV a procesar')
    parser.add_argument('--max-lines', '-m', type=int, help='Máximo de líneas a procesar (para pruebas)')
    
    args = parser.parse_args()
    
    # Mostrar estado del sistema
    print("🎯 Clasificador CEFR Local")
    print("="*50)
    print(f"📚 cefrpy/spaCy: {'✅' if HAS_DEPS and nlp else '❌'}")
    print(f"🤖 Modelo neural: {'✅' if classifier else '❌'}")
    print("="*50)
    
    if args.word:
        resultado = clasificar_texto_auto(args.word)
        print(f"\n🎯 Resultado final: {args.word} → {resultado}")
        
    elif args.text:
        resultado = clasificar_texto_auto(args.text)
        print(f"\n🎯 Resultado final: {args.text} → {resultado}")
        
    elif args.file:
        procesar_archivo_tsv(args.file, args.max_lines)
        
    else:
        # Modo interactivo
        print("\n💬 Modo interactivo activado")
        print("💡 Escribe palabras o frases para analizar")
        print("💡 Escribe 'exit' para salir")
        print("💡 Escribe 'file:ruta' para procesar un archivo")
        
        while True:
            try:
                entrada = input("\n🎯 Texto: ").strip()
                
                if entrada.lower() == 'exit':
                    print("👋 ¡Hasta luego!")
                    break
                
                if entrada.startswith('file:'):
                    archivo = entrada[5:].strip()
                    procesar_archivo_tsv(archivo, 5)  # Máximo 5 para pruebas interactivas
                    continue
                
                if not entrada:
                    continue
                
                resultado = clasificar_texto_auto(entrada)
                print(f"🎯 → {resultado}")
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

# ==============================================================================
# EJEMPLOS DE PRUEBA (para ejecutar directamente)
# ==============================================================================
def ejecutar_ejemplos():
    """Ejecuta ejemplos de prueba"""
    print("\n" + "="*60)
    print("🧪 EJECUTANDO EJEMPLOS DE PRUEBA")
    print("="*60)
    
    # Ejemplo de palabra
    print("\n📝 Probando palabra:")
    nivel_palabra = clasificar_texto_auto("beautiful")
    print(f"🎯 'beautiful' → {nivel_palabra}")
    
    # Ejemplo de frase
    print("\n📖 Probando frase:")
    nivel_frase = clasificar_texto_auto("This is a very beautiful sentence with complex vocabulary.")
    print(f"🎯 Frase → {nivel_frase}")

# Ejecutar ejemplos si se llama directamente
if __name__ == "__main__" and len(sys.argv) == 1:
    ejecutar_ejemplos()