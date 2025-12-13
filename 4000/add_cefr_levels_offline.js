#!/usr/bin/env node
/**
 * Script OFFLINE para agregar niveles CEFR a las palabras en el archivo TSV de Anki
 * Versión que NO usa API externa, solo diccionarios locales
 */

const fs = require('fs').promises;

/**
 * Función para determinar nivel CEFR usando solo diccionarios locales
 * @param {string} text - La palabra o frase a evaluar
 * @returns {string} - El nivel CEFR estimado
 */
function getCEFRLevelOffline(text) {
    text = text.toLowerCase().trim();
    
    // Si es una frase (contiene espacios), analizamos cada palabra
    if (text.includes(' ')) {
        return analyzePhrase(text);
    }
    
    // Diccionarios de palabras basados en el script Python original
    // A1 - Palabras más básicas y fundamentales
    const a1Words = new Set([
        'agree', 'arrive', 'august', 'boat', 'breakfast', 'camera', 'catch', 'duck', 'enjoy', 
        'invite', 'love', 'month', 'travel', 'visit', 'weather', 'week', 'wine', 'kill', 
        'laugh', 'loud', 'noise', 'smell', 'cloud', 'animal', 'bus', 'cat', 'dog', 'door', 
        'friend', 'hear', 'help', 'horse', 'hospital', 'leg', 'open', 'pull', 'rabbit', 
        'school', 'see', 'chicken', 'eat', 'food', 'fruit', 'water', 'ask', 'banana', 
        'bread', 'cake', 'carrot', 'chocolate', 'always', 'seven', 'start', 'together', 
        'wear', 'year', 'home', 'family', 'from', 'green', 'red', 'book', 'clothes', 
        'dinner', 'end', 'january', 'december',
        // Palabras básicas adicionales
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
        'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when', 'what', 'who', 'how', 'why',
        'yes', 'no', 'not', 'good', 'bad', 'big', 'small', 'new', 'old', 'hot', 'cold', 'long', 'short',
        'like', 'want', 'need', 'have', 'get', 'go', 'come', 'look', 'drink', 'work', 'time', 'day'
    ]);
    
    // A2 - Palabras básicas pero un poco más complejas
    const a2Words = new Set([
        'capital', 'typical', 'adventure', 'approach', 'carefully', 'create', 'project', 
        'scare', 'secret', 'shout', 'terrible', 'worse', 'among', 'chart', 'describe', 
        'ever', 'fail', 'grade', 'instead', 'library', 'photograph', 'several', 'solve', 
        'suddenly', 'suppose', 'understand', 'view', 'appropriate', 'avoid', 'behave', 
        'calm', 'concern', 'content', 'expect', 'frequently', 'habit', 'instruct', 'issue', 
        'none', 'patient', 'positive', 'punish', 'represent', 'shake', 'spread', 'stroll', 
        'village', 'active', 'adult', 'age', 'balance', 'bike', 'choose', 'doctor', 
        'during', 'football', 'fun', 'game', 'heart', 'golf', 'increase', 'life', 'often', 
        'plenty', 'weight', 'apartment', 'article', 'artist', 'attitude', 'beauty', 'compare', 
        'judge', 'magazine', 'material', 'meal', 'method', 'neighbor', 'profit', 'quality', 
        'space', 'stair', 'symbol', 'thin', 'community', 'university', 'celebrate', 'decide', 
        'disappear', 'else', 'fair', 'flow', 'forward', 'hill', 'level', 'lone', 'puddle', 
        'response', 'season', 'solution', 'waste', 'whether', 'great', 'health', 'recipe', 
        'restaurant', 'special', 'alive', 'bone', 'bother', 'captain', 'conclusion', 'doubt', 
        'explore', 'glad', 'however', 'mention', 'social', 'speech', 'staff', 'toward', 
        'wood', 'achieve', 'advise', 'already', 'basic', 'bit', 'consider', 'destroy', 
        'entertain', 'extra', 'goal', 'lie', 'meat', 'opinion', 'real', 'reflect', 'regard', 
        'serve', 'vegetable', 'war', 'worth',
        // Palabras A2 adicionales
        'about', 'after', 'again', 'all', 'also', 'different', 'each', 'early', 'every', 
        'first', 'important', 'large', 'last', 'late', 'little', 'live', 'make', 'many', 'most',
        'much', 'never', 'next', 'only', 'other', 'own', 'place', 'right', 'same',
        'some', 'still', 'such', 'take', 'than', 'them', 'think', 'through', 'very',
        'way', 'well', 'while', 'world', 'write', 'young'
    ]);

    // B1 - Palabras de nivel intermedio
    const b1Words = new Set([
        'alcohol', 'chemical', 'evil', 'experiment', 'laboratory', 'nervous', 'alien', 
        'planet', 'report', 'shape', 'command', 'depend', 'medical', 'service', 'benefit', 
        'certain', 'chance', 'effect', 'essential', 'focus', 'function', 'grass', 
        'guard', 'image', 'immediate', 'primary', 'proud', 'remain', 'rest', 'separate', 
        'site', 'tail', 'trouble', 'advertise', 'aware', 'battery', 'black', 'city', 
        'clean', 'country', 'develop', 'electric', 'eventually', 'fact', 'glass', 'history', 
        'nature', 'people', 'plastic', 'problem', 'street', 'alone', 
        'professional', 'appeal', 'assume', 'borrow', 'client', 'downtown', 'dull', 'embarrass', 
        'fare', 'former', 'found', 'invest', 'loan', 'practical', 'quarter', 'salary', 
        'scholarship', 'temporary', 'treasure', 'urge', 'coach', 'control', 'description', 
        'direct', 'exam', 'example', 'limit', 'local', 'magical', 'mail', 'novel', 'outline', 
        'poet', 'print', 'scene', 'sheet', 'silly', 'store', 'suffer', 'technology', 'across', 
        'breathe', 'characteristic', 'consume', 'excite', 'extremely', 'fear', 'fortunate', 
        'happen', 'length', 'mistake', 'observe', 'opportunity', 'prize', 'race', 'realize', 
        'respond', 'risk', 'wonder', 'yet', 'art', 'contain', 'delicious', 'diet', 'accounting', 
        'injustice', 'international', 'lawyer', 'policy'
    ]);

    // B2 - Palabras de nivel intermedio-alto
    const b2Words = new Set([
        'apart', 'attribute', 'bilingual', 'completely', 'dash', 'disgust', 'fashionable', 
        'foreign', 'gulf', 'mirror', 'natural', 'nowadays', 'participant', 'ritual', 
        'spoken', 'sport', 'surprised', 'tense', 'totally', 'vague', 'allow', 'announce', 
        'beside', 'challenge', 'claim', 'condition', 'contribute', 'difference', 'divide', 
        'expert', 'famous', 'force', 'harm', 'lay', 'peace', 'prince', 'protect', 'sense', 
        'sudden', 'therefore', 'accept', 'arrange', 'attend', 'chase', 'contrast', 'encourage', 
        'familiar', 'grab', 'hang', 'huge', 'necessary', 'pattern', 'propose', 'purpose', 
        'release', 'require', 'satisfied', 'single', 'tear', 'theory', 'advance', 'athlete', 
        'average', 'behavior', 'behind', 'course', 'lower', 'match', 'member', 'mental', 
        'passenger', 'personality', 'poem', 'pole', 'remove', 'safety', 'shoot', 'sound', 
        'swim', 'web', 'block', 'bury', 'cheer', 'complex', 'critic', 'direction', 'event', 
        'exercise', 'friendship', 'guide', 'lack', 'perform', 'bright', 'actual', 'amaze', 
        'charge', 'comfort', 'contact', 'customer', 'deliver', 'earn', 'gate', 'include', 
        'manage', 'mystery', 'occur', 'opposite', 'plate', 'receive', 'reward', 'set', 
        'steal', 'thief'
    ]);

    // C1 - Palabras de nivel avanzado
    const c1Words = new Set([
        'exchange', 'appear', 'base', 'brain', 'career', 'clerk', 'effort', 'enter', 
        'excellent', 'hero', 'hurry', 'inform', 'later', 'leave', 'locate', 'nurse', 
        'operation', 'pain', 'refuse', 'though', 'various'
    ]);

    // C2 - Palabras de nivel muy avanzado
    const c2Words = new Set([
        'sophisticated', 'unprecedented', 'manifestation', 'contemporary', 'ambiguous'
    ]);

    // Verificar en orden de dificultad
    if (a1Words.has(text)) {
        return 'A1';
    } else if (a2Words.has(text)) {
        return 'A2';
    } else if (b1Words.has(text)) {
        return 'B1';
    } else if (b2Words.has(text)) {
        return 'B2';
    } else if (c1Words.has(text)) {
        return 'C1';
    } else if (c2Words.has(text)) {
        return 'C2';
    } else {
        // Para palabras no clasificadas, usar heurísticas básicas
        if (text.length <= 4 && /^[a-z]+$/.test(text)) {
            return 'A1';
        } else if (text.length <= 6) {
            return 'A2';
        } else if (text.length <= 8) {
            return 'B1';
        } else if (text.length <= 10) {
            return 'B2';
        } else {
            return 'C1';
        }
    }
}

/**
 * Analiza frases dividiendo en palabras y determinando el nivel más alto
 * @param {string} phrase - La frase a analizar
 * @returns {string} - El nivel CEFR de la frase
 */
function analyzePhrase(phrase) {
    // Limpiar la frase y dividir en palabras
    const words = phrase
        .toLowerCase()
        .replace(/[^\w\s]/g, '') // Remover puntuación
        .split(/\s+/)
        .filter(word => word.length > 0);
    
    if (words.length === 0) {
        return 'A1';
    }
    
    // Obtener nivel de cada palabra
    const levels = words.map(word => getCEFRLevelOffline(word));
    
    // Convertir niveles a números para comparar
    const levelValues = {
        'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6
    };
    
    // Encontrar el nivel más alto (el más difícil determina el nivel de la frase)
    const maxLevel = Math.max(...levels.map(level => levelValues[level] || 1));
    
    // Convertir de vuelta a string
    const levelNames = ['', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
    return levelNames[maxLevel];
}

/**
 * Función para procesar el archivo TSV y agregar niveles CEFR sin usar API
 * @param {string} inputFile - Ruta del archivo de entrada
 * @param {string} outputFile - Ruta del archivo de salida
 */
async function processTSVFileOffline(inputFile, outputFile) {
    try {
        console.log('Leyendo archivo TSV...');
        const data = await fs.readFile(inputFile, 'utf-8');
        const lines = data.split('\n');
        
        const processedLines = [];
        let processedCount = 0;
        const totalLines = lines.filter(line => !line.startsWith('#') && line.trim()).length;
        
        console.log(`Procesando ${totalLines} líneas...`);
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].replace(/\r?\n$/, '');
            
            // Procesar solo líneas que no sean comentarios
            if (line.startsWith('#') || !line.trim()) {
                processedLines.push(line);
                continue;
            }
            
            // Separar por tabulaciones
            const columns = line.split('\t');
            
            if (columns.length >= 12) {
                // Extraer la palabra de la columna 4 (índice 3)
                const text = columns[3].trim();
                
                if (text) {
                    console.log(`Procesando ${++processedCount}/${totalLines}: "${text}"`);
                    
                    // Obtener el nivel CEFR usando diccionarios locales
                    const cefrLevel = getCEFRLevelOffline(text);
                    
                    // Agregar el nivel a la columna 12 (índice 11)
                    if (columns[11].trim()) {
                        columns[11] = columns[11] + ' ' + cefrLevel;
                    } else {
                        columns[11] = cefrLevel;
                    }
                    
                    console.log(`  → Nivel CEFR asignado: ${cefrLevel}`);
                }
                
                // Reconstruir la línea
                const processedLine = columns.join('\t');
                processedLines.push(processedLine);
            } else {
                processedLines.push(line);
            }
        }
        
        // Escribir el archivo procesado
        console.log('Escribiendo archivo de salida...');
        await fs.writeFile(outputFile, processedLines.join('\n'), 'utf-8');
        
        console.log(`✅ Archivo procesado exitosamente!`);
        console.log(`📁 Archivo de salida: ${outputFile}`);
        console.log(`📊 Líneas procesadas: ${processedCount}`);
        
    } catch (error) {
        console.error('❌ Error procesando el archivo:', error.message);
        process.exit(1);
    }
}

// Configuración de archivos
const inputFile = 'c:\\Users\\jesus\\OneDrive\\Documentos\\LEPCSV\\4000\\4000EEnglish__1.Book copy.txt';
const outputFile = 'c:\\Users\\jesus\\OneDrive\\Documentos\\LEPCSV\\4000\\4000EEnglish__1.Book_with_CEFR_OFFLINE.txt';

// Ejecutar el procesamiento
if (require.main === module) {
    console.log('🚀 Iniciando procesamiento OFFLINE de archivo TSV con niveles CEFR...');
    console.log('📡 Esta versión NO usa API externa, solo diccionarios locales');
    console.log(`📖 Archivo de entrada: ${inputFile}`);
    console.log(`💾 Archivo de salida: ${outputFile}`);
    console.log('');
    
    processTSVFileOffline(inputFile, outputFile)
        .then(() => {
            console.log('🎉 Procesamiento completado exitosamente!');
        })
        .catch((error) => {
            console.error('💥 Error durante el procesamiento:', error);
            process.exit(1);
        });
}

module.exports = {
    processTSVFileOffline,
    getCEFRLevelOffline,
    analyzePhrase
};
