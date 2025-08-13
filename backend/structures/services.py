"""
Servicio para interactuar con la API de PubChem y gestionar el cache local de compuestos.
"""
import re
import time
import logging
import requests
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from django.core.cache import cache
from django.conf import settings
from .models import CompoundCache

logger = logging.getLogger(__name__)


class PubChemService:
    """
    Servicio para buscar información de compuestos químicos en PubChem.
    Implementa cache local en base de datos y cache temporal en memoria.
    """
    
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    TIMEOUT = 10  # segundos
    MAX_RETRIES = 3
    RATE_LIMIT_DELAY = 0.2  # 200ms entre requests (5 requests/segundo max)
    
    def __init__(self):
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChemsTools/1.0 (Educational Chemistry Tool)'
        })
    
    def _rate_limit(self):
        """Implementa rate limiting para respetar los límites de PubChem"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, retries: int = 0) -> Optional[Dict]:
        """
        Realiza una petición HTTP con reintentos y manejo de errores.
        """
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=self.TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.info(f"Compound not found: {url}")
                return None
            elif response.status_code == 503 and retries < self.MAX_RETRIES:
                # Servidor ocupado, reintentar
                time.sleep(2 ** retries)  # Backoff exponencial
                return self._make_request(url, retries + 1)
            else:
                logger.error(f"PubChem API error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al consultar PubChem: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al consultar PubChem: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error al parsear respuesta JSON: {e}")
            return None
    
    def detect_query_type(self, query: str) -> str:
        """
        Intenta detectar el tipo de query basándose en el formato.
        """
        query = query.strip()
        
        # Detectar SMILES (contiene caracteres especiales típicos)
        if any(char in query for char in ['@', '/', '\\', '[', ']', '(', ')']):
            return 'smiles'
        
        # Detectar InChI
        if query.startswith('InChI='):
            return 'inchi'
        
        # Detectar CAS number (formato: XXXX-XX-X)
        if re.match(r'^\d{2,7}-\d{2}-\d$', query):
            return 'cas'
        
        # Detectar fórmula molecular (empieza con elemento y tiene números)
        if re.match(r'^[A-Z][a-z]?\d*([A-Z][a-z]?\d*)*$', query):
            return 'formula'
        
        # Por defecto, asumir que es un nombre
        return 'name'
    
    def search_by_name(self, name: str) -> Optional[Dict]:
        """Busca un compuesto por nombre común o IUPAC"""
        encoded_name = quote(name)
        url = f"{self.BASE_URL}/compound/name/{encoded_name}/cids/JSON"
        return self._make_request(url)
    
    def search_by_smiles(self, smiles: str) -> Optional[Dict]:
        """Busca un compuesto por SMILES"""
        encoded_smiles = quote(smiles)
        url = f"{self.BASE_URL}/compound/smiles/{encoded_smiles}/cids/JSON"
        return self._make_request(url)
    
    def search_by_formula(self, formula: str) -> Optional[Dict]:
        """Busca compuestos por fórmula molecular"""
        encoded_formula = quote(formula)
        url = f"{self.BASE_URL}/compound/fastformula/{encoded_formula}/cids/JSON"
        return self._make_request(url)
    
    def search_by_inchi(self, inchi: str) -> Optional[Dict]:
        """Busca un compuesto por InChI"""
        encoded_inchi = quote(inchi)
        url = f"{self.BASE_URL}/compound/inchi/{encoded_inchi}/cids/JSON"
        return self._make_request(url)
    
    def get_compound_properties(self, cid: int) -> Optional[Dict]:
        """
        Obtiene las propiedades de un compuesto dado su CID.
        """
        # Lista de propiedades que queremos obtener
        properties = [
            'CanonicalSMILES',
            'IsomericSMILES',
            'IUPACName',
            'MolecularFormula',
            'MolecularWeight',
            'InChI',
            'InChIKey'
        ]
        
        props_string = ','.join(properties)
        url = f"{self.BASE_URL}/compound/cid/{cid}/property/{props_string}/JSON"
        
        result = self._make_request(url)
        if result and 'PropertyTable' in result:
            return result['PropertyTable']['Properties'][0]
        return None
    
    def get_compound_synonyms(self, cid: int, limit: int = 10) -> List[str]:
        """
        Obtiene sinónimos/nombres alternativos del compuesto.
        """
        url = f"{self.BASE_URL}/compound/cid/{cid}/synonyms/JSON"
        result = self._make_request(url)
        
        if result and 'InformationList' in result:
            synonyms = result['InformationList']['Information'][0].get('Synonym', [])
            return synonyms[:limit]
        return []
    
    def search_compound(self, query: str, query_type: Optional[str] = None) -> Optional[Dict]:
        """
        Busca un compuesto en PubChem y devuelve su información completa.
        Primero intenta buscar en el cache local.
        """
        query = query.strip()
        
        # Detectar tipo de query si no se especifica
        if not query_type:
            query_type = self.detect_query_type(query)
        
        # Buscar en cache de base de datos
        cache_key = f"pubchem_{query_type}_{query.lower()}"
        cached = CompoundCache.objects.filter(
            query=query.lower(),
            query_type=query_type
        ).first()
        
        if cached:
            logger.info(f"Compuesto encontrado en cache: {query}")
            cached.increment_access()
            return {
                'smiles': cached.smiles,
                'iupac_name': cached.iupac_name,
                'molecular_formula': cached.molecular_formula,
                'molecular_weight': cached.molecular_weight,
                'pubchem_cid': cached.pubchem_cid,
                'common_names': cached.common_names,
                'properties': cached.properties
            }
        
        # Buscar en PubChem
        logger.info(f"Buscando en PubChem: {query} (tipo: {query_type})")
        
        cid_result = None
        if query_type == 'name':
            cid_result = self.search_by_name(query)
        elif query_type == 'smiles':
            cid_result = self.search_by_smiles(query)
        elif query_type == 'formula':
            cid_result = self.search_by_formula(query)
        elif query_type == 'inchi':
            cid_result = self.search_by_inchi(query)
        
        if not cid_result or 'IdentifierList' not in cid_result:
            # Si no se encuentra por el tipo detectado, intentar como nombre
            if query_type != 'name':
                logger.info(f"No encontrado como {query_type}, intentando como nombre")
                cid_result = self.search_by_name(query)
        
        if cid_result and 'IdentifierList' in cid_result:
            cids = cid_result['IdentifierList'].get('CID', [])
            if cids:
                # Tomar el primer CID (más relevante)
                cid = cids[0]
                
                # Obtener propiedades del compuesto
                properties = self.get_compound_properties(cid)
                
                if properties:
                    # Obtener sinónimos
                    synonyms = self.get_compound_synonyms(cid)
                    
                    # Convertir molecular_weight a float si es posible
                    molecular_weight = properties.get('MolecularWeight')
                    if molecular_weight is not None:
                        try:
                            molecular_weight = float(molecular_weight)
                        except (ValueError, TypeError):
                            molecular_weight = None
                    
                    # Guardar en cache
                    try:
                        compound_cache = CompoundCache.objects.create(
                            query=query.lower(),
                            query_type=query_type,
                            smiles=properties.get('CanonicalSMILES', ''),
                            iupac_name=properties.get('IUPACName'),
                            molecular_formula=properties.get('MolecularFormula', ''),
                            molecular_weight=molecular_weight,
                            pubchem_cid=cid,
                            inchi=properties.get('InChI'),
                            inchi_key=properties.get('InChIKey'),
                            common_names=synonyms,
                            properties=properties
                        )
                        logger.info(f"Compuesto guardado en cache: {compound_cache}")
                    except Exception as e:
                        logger.error(f"Error guardando en cache: {e}")
                    
                    return {
                        'smiles': properties.get('CanonicalSMILES', ''),
                        'iupac_name': properties.get('IUPACName'),
                        'molecular_formula': properties.get('MolecularFormula', ''),
                        'molecular_weight': molecular_weight,
                        'pubchem_cid': cid,
                        'common_names': synonyms,
                        'properties': properties
                    }
        
        logger.warning(f"No se encontró el compuesto: {query}")
        return None
    
    def search_multi_language(self, query: str) -> Optional[Dict]:
        """
        Busca un compuesto probando diferentes idiomas y variaciones.
        Útil para nombres en español, inglés, etc.
        """
        # Diccionario de traducciones comunes español -> inglés
        translations = {
            'agua': 'water',
            'ácido sulfúrico': 'sulfuric acid',
            'acido sulfurico': 'sulfuric acid',
            'ácido clorhídrico': 'hydrochloric acid',
            'acido clorhidrico': 'hydrochloric acid',
            'sal': 'sodium chloride',
            'sal de mesa': 'sodium chloride',
            'azúcar': 'sucrose',
            'azucar': 'sucrose',
            'glucosa': 'glucose',
            'etanol': 'ethanol',
            'alcohol': 'ethanol',
            'metano': 'methane',
            'amoníaco': 'ammonia',
            'amoniaco': 'ammonia',
            'dióxido de carbono': 'carbon dioxide',
            'dioxido de carbono': 'carbon dioxide',
            'peróxido de hidrógeno': 'hydrogen peroxide',
            'peroxido de hidrogeno': 'hydrogen peroxide',
            'agua oxigenada': 'hydrogen peroxide',
            'acetona': 'acetone',
            'benceno': 'benzene',
            'ácido acético': 'acetic acid',
            'acido acetico': 'acetic acid',
            'vinagre': 'acetic acid',
        }
        
        # Intentar buscar directamente
        result = self.search_compound(query, 'name')
        if result:
            return result
        
        # Intentar con traducción si existe
        query_lower = query.lower()
        if query_lower in translations:
            result = self.search_compound(translations[query_lower], 'name')
            if result:
                return result
        
        # Intentar sin tildes/acentos
        import unicodedata
        normalized = unicodedata.normalize('NFKD', query)
        without_accents = ''.join([c for c in normalized if not unicodedata.combining(c)])
        if without_accents != query:
            result = self.search_compound(without_accents, 'name')
            if result:
                return result
        
        return None
