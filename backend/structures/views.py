from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import LewisStructureGenerator
from .serializers import FormulaInputSerializer, LewisStructureSerializer
from .models import MolecularStructure, CompoundCache
from .services import PubChemService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def generate_lewis_structure(request):
    """
    Generar estructura de Lewis a partir de una consulta química.
    
    Este endpoint procesa una consulta química (nombre, fórmula, SMILES, etc.) y genera
    su estructura de Lewis correspondiente. Integra con PubChem para búsqueda de compuestos
    y utiliza RDKit para el cálculo estructural.
    
    **Método:** POST
    **URL:** /api/structures/lewis-generator/
    
    **Parámetros del body (JSON):**
    - query (str, requerido): Puede ser:
      - Fórmula molecular: "H2O", "CH4", "NH3"
      - Nombre común: "water", "agua", "methane"
      - Nombre IUPAC: "dihydrogen monoxide"
      - SMILES: "O", "C", "N"
      - InChI: "InChI=1S/H2O/h1H2"
    - query_type (str, opcional): Tipo de búsqueda ('name', 'formula', 'smiles', 'inchi')
    
    **Respuesta exitosa (201):**
    ```json
    {
        "id": 1,
        "formula": "H2O",
        "query": "agua",
        "iupac_name": "water",
        "mol_data": {
            "molecular_weight": 18.015,
            "num_atoms": 3,
            "num_bonds": 2
        },
        "lewis_data": {
            "atoms": [
                {"element": "O", "x": 0, "y": 0, "formal_charge": 0, "lone_pairs": 2},
                {"element": "H", "x": -1, "y": 0, "formal_charge": 0, "lone_pairs": 0},
                {"element": "H", "x": 1, "y": 0, "formal_charge": 0, "lone_pairs": 0}
            ],
            "bonds": [
                {"atom1": 0, "atom2": 1, "order": 1},
                {"atom1": 0, "atom2": 2, "order": 1}
            ],
            "total_electrons": 8,
            "valence_electrons": 8
        },
        "created_at": "2025-08-11T20:00:00Z",
        "pubchem_cid": 962,
        "common_names": ["water", "oxidane", "hydrogen oxide"]
    }
    ```
    
    **Respuesta con estructura cacheada (200):**
    Si la estructura ya fue generada previamente, se devuelve desde la base de datos.
    
    **Errores posibles:**
    - 400: Consulta inválida o no se puede generar la estructura
    - 404: Compuesto no encontrado en PubChem ni en cache local
    
    **Notas:**
    - Integra con PubChem API para búsqueda de compuestos
    - Las búsquedas se cachean localmente para reducir latencia
    - Soporta múltiples idiomas para nombres comunes
    - Los pares de electrones libres se calculan automáticamente
    """
    # Obtener el query del request
    query = request.data.get('query') or request.data.get('formula', '')
    query_type = request.data.get('query_type')
    
    if not query:
        return Response(
            {'error': 'Query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Importar utilidades necesarias
    from .utils import LewisStructureGenerator
    from .simple_structures import get_simple_structure
    
    # Inicializar servicio PubChem
    pubchem_service = PubChemService()
    
    # Primero buscar en cache de estructuras existentes por fórmula exacta
    try:
        existing = MolecularStructure.objects.get(formula=query.upper())
        logger.info(f"Structure found in cache for: {query}")
        
        # Intentar regenerar solo si es una estructura simple conocida
        simple_struct = get_simple_structure(query.upper())
        
        if simple_struct:
            # Si es una estructura simple, usar los datos hardcodeados
            mol_block = LewisStructureGenerator.generate_mol_block_from_lewis(simple_struct)
            existing.lewis_data = simple_struct
            existing.mol_data = mol_block
            existing.save()
            
            response_data = LewisStructureSerializer(existing).data
            response_data['source'] = 'local_cache_hardcoded'
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Para estructuras complejas, usar los datos existentes sin regenerar
            response_data = LewisStructureSerializer(existing).data
            response_data['source'] = 'local_cache'
            return Response(response_data, status=status.HTTP_200_OK)
    except MolecularStructure.DoesNotExist:
        pass
    
    # Buscar en PubChem o cache de compuestos
    logger.info(f"Searching compound: {query} (type: {query_type})")
    
    # Intentar búsqueda multi-idioma primero si parece ser un nombre
    compound_info = None
    if not query_type or query_type == 'name':
        compound_info = pubchem_service.search_multi_language(query)
    
    # Si no se encontró, intentar búsqueda normal
    if not compound_info:
        compound_info = pubchem_service.search_compound(query, query_type)
    
    # Si no se encuentra en PubChem, intentar generar directamente
    if not compound_info:
        logger.info(f"Compound not found in PubChem, trying direct generation for: {query}")
        result = LewisStructureGenerator.generate_lewis_structure(query)
        
        if not result['success']:
            return Response(
                {
                    'error': 'Compound not found',
                    'details': f'Could not find or generate structure for: {query}',
                    'suggestion': 'Try using a valid molecular formula, IUPAC name, or common name'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardar estructura generada directamente
        structure = MolecularStructure.objects.create(
            formula=query.upper(),
            mol_data=result['mol_data'],
            lewis_data=result['lewis_data']
        )
        
        response_data = LewisStructureSerializer(structure).data
        response_data['source'] = 'direct_generation'
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    # Usar SMILES de PubChem para generar estructura
    smiles = compound_info.get('smiles', '')
    formula = compound_info.get('molecular_formula', '')
    
    # Si no hay SMILES canónico, intentar con isomérico o de conectividad
    if not smiles or smiles.strip() == '':
        properties = compound_info.get('properties', {})
        smiles = properties.get('IsomericSMILES', '')
        if not smiles and 'ConnectivitySMILES' in properties:
            # Para compuestos iónicos, usar ConnectivitySMILES si está disponible
            smiles = properties.get('ConnectivitySMILES', '')
    
    # Primero verificar si hay una estructura hardcodeada para esta fórmula
    if formula:
        simple_struct = get_simple_structure(formula)
        if simple_struct:
            logger.info(f"Using hardcoded structure for {formula}")
            mol_block = LewisStructureGenerator.generate_mol_block_from_lewis(simple_struct)
            
            # Verificar si ya existe antes de crear
            try:
                structure = MolecularStructure.objects.get(formula=formula.upper())
                # Actualizar con los nuevos datos generados
                structure.mol_data = mol_block
                structure.lewis_data = simple_struct
                structure.save()
            except MolecularStructure.DoesNotExist:
                # Guardar estructura generada desde hardcode
                structure = MolecularStructure.objects.create(
                    formula=formula.upper(),
                    mol_data=mol_block,
                    lewis_data=simple_struct
                )
            
            response_data = LewisStructureSerializer(structure).data
            response_data.update({
                'query': query,
                'iupac_name': compound_info.get('iupac_name'),
                'pubchem_cid': compound_info.get('pubchem_cid'),
                'common_names': compound_info.get('common_names', [])[:5],
                'molecular_weight': compound_info.get('molecular_weight'),
                'source': 'pubchem_hardcoded'
            })
            return Response(response_data, status=status.HTTP_201_CREATED)
    
    if not smiles or smiles.strip() == '':
        # Si no hay SMILES y no hay estructura hardcodeada, intentar generar con la fórmula
        if formula:
            logger.info(f"No SMILES available for {query}, trying with formula: {formula}")
            result = LewisStructureGenerator.generate_lewis_structure(formula)
            
            if result['success']:
                # Verificar si ya existe antes de crear
                try:
                    structure = MolecularStructure.objects.get(formula=formula)
                    # Actualizar con los nuevos datos generados
                    structure.mol_data = result['mol_data']
                    structure.lewis_data = result['lewis_data']
                    structure.save()
                except MolecularStructure.DoesNotExist:
                    # Guardar estructura generada desde fórmula
                    structure = MolecularStructure.objects.create(
                        formula=formula,
                        mol_data=result['mol_data'],
                        lewis_data=result['lewis_data']
                    )
                
                response_data = LewisStructureSerializer(structure).data
                response_data.update({
                    'query': query,
                    'iupac_name': compound_info.get('iupac_name'),
                    'pubchem_cid': compound_info.get('pubchem_cid'),
                    'common_names': compound_info.get('common_names', [])[:5],
                    'molecular_weight': compound_info.get('molecular_weight'),
                    'source': 'pubchem_formula'
                })
                return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(
            {
                'error': 'No structural information available',
                'details': 'Compound found but no SMILES or valid formula available',
                'compound_info': compound_info
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generar estructura de Lewis desde SMILES
    result = LewisStructureGenerator.generate_lewis_structure(smiles)
    
    if not result['success']:
        return Response(
            {
                'error': 'Failed to generate Lewis structure',
                'details': result.get('error', 'Unknown error'),
                'compound_info': compound_info
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Guardar en base de datos con información adicional de PubChem
    formula = compound_info.get('molecular_formula', smiles)
    
    # Verificar si ya existe con esta fórmula
    try:
        existing = MolecularStructure.objects.get(formula=formula)
        response_data = LewisStructureSerializer(existing).data
        response_data.update({
            'query': query,
            'iupac_name': compound_info.get('iupac_name'),
            'pubchem_cid': compound_info.get('pubchem_cid'),
            'common_names': compound_info.get('common_names', [])[:5],
            'source': 'pubchem_cached'
        })
        return Response(response_data, status=status.HTTP_200_OK)
    except MolecularStructure.DoesNotExist:
        pass
    
    # Crear nueva estructura
    structure = MolecularStructure.objects.create(
        formula=formula,
        mol_data=result['mol_data'],
        lewis_data=result['lewis_data']
    )
    
    response_data = LewisStructureSerializer(structure).data
    response_data.update({
        'query': query,
        'iupac_name': compound_info.get('iupac_name'),
        'pubchem_cid': compound_info.get('pubchem_cid'),
        'common_names': compound_info.get('common_names', [])[:5],
        'molecular_weight': compound_info.get('molecular_weight'),
        'source': 'pubchem_new'
    })
    
    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_structures(request):
    """
    Listar estructuras de Lewis generadas recientemente.
    
    Devuelve las últimas 20 estructuras de Lewis generadas y almacenadas
    en la base de datos, ordenadas por fecha de creación descendente.
    
    **Método:** GET
    **URL:** /api/structures/
    
    **Respuesta exitosa (200):**
    ```json
    [
        {
            "id": 1,
            "formula": "H2O",
            "mol_data": {...},
            "lewis_data": {...},
            "created_at": "2025-08-11T20:00:00Z"
        },
        {
            "id": 2,
            "formula": "CH4",
            "mol_data": {...},
            "lewis_data": {...},
            "created_at": "2025-08-11T19:50:00Z"
        }
    ]
    ```
    
    **Notas:**
    - Máximo 20 estructuras por petición
    - No requiere autenticación
    """
    structures = MolecularStructure.objects.all()[:20]  # Limit to 20 most recent
    serializer = LewisStructureSerializer(structures, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_structure(request, structure_id):
    """
    Obtener una estructura de Lewis específica por ID.
    
    Devuelve los detalles completos de una estructura de Lewis almacenada,
    identificada por su ID único en la base de datos.
    
    **Método:** GET
    **URL:** /api/structures/{structure_id}/
    
    **Parámetros de ruta:**
    - structure_id (int): ID único de la estructura
    
    **Respuesta exitosa (200):**
    ```json
    {
        "id": 1,
        "formula": "H2O",
        "mol_data": {
            "molecular_weight": 18.015,
            "num_atoms": 3,
            "num_bonds": 2
        },
        "lewis_data": {
            "atoms": [...],
            "bonds": [...],
            "total_electrons": 8,
            "valence_electrons": 8
        },
        "created_at": "2025-08-11T20:00:00Z"
    }
    ```
    
    **Errores posibles:**
    - 404: Estructura no encontrada con el ID especificado
    """
    try:
        structure = MolecularStructure.objects.get(id=structure_id)
        serializer = LewisStructureSerializer(structure)
        return Response(serializer.data)
    except MolecularStructure.DoesNotExist:
        return Response(
            {'error': 'Structure not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def search_compound(request):
    """
    Buscar información de un compuesto químico.
    
    Busca información detallada de un compuesto en PubChem o cache local
    sin generar la estructura de Lewis. Útil para obtener metadatos.
    
    **Método:** GET
    **URL:** /api/structures/search/
    
    **Parámetros de query:**
    - q (str, requerido): Término de búsqueda (nombre, fórmula, SMILES, etc.)
    - type (str, opcional): Tipo de búsqueda ('name', 'formula', 'smiles', 'inchi')
    
    **Respuesta exitosa (200):**
    ```json
    {
        "smiles": "O",
        "iupac_name": "oxidane",
        "molecular_formula": "H2O",
        "molecular_weight": 18.015,
        "pubchem_cid": 962,
        "common_names": ["water", "oxidane", "hydrogen oxide"],
        "properties": {
            "CanonicalSMILES": "O",
            "IUPACName": "oxidane",
            "MolecularFormula": "H2O",
            "MolecularWeight": 18.015,
            "InChI": "InChI=1S/H2O/h1H2",
            "InChIKey": "XLYOFNOQVPJJNP-UHFFFAOYSA-N"
        }
    }
    ```
    
    **Errores posibles:**
    - 400: Parámetro de búsqueda faltante
    - 404: Compuesto no encontrado
    
    **Notas:**
    - No genera estructura de Lewis, solo obtiene información
    - Resultados se cachean automáticamente
    - Soporta búsqueda multi-idioma
    """
    query = request.GET.get('q', '').strip()
    query_type = request.GET.get('type')
    
    if not query:
        return Response(
            {'error': 'Search query parameter "q" is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Inicializar servicio PubChem
    pubchem_service = PubChemService()
    
    # Buscar compuesto
    logger.info(f"Searching for compound: {query} (type: {query_type})")
    
    # Intentar búsqueda multi-idioma si no se especifica tipo
    compound_info = None
    if not query_type or query_type == 'name':
        compound_info = pubchem_service.search_multi_language(query)
    
    # Si no se encontró, intentar búsqueda normal
    if not compound_info:
        compound_info = pubchem_service.search_compound(query, query_type)
    
    if compound_info:
        return Response(compound_info, status=status.HTTP_200_OK)
    else:
        return Response(
            {
                'error': 'Compound not found',
                'query': query,
                'suggestion': 'Try using a different search term or type'
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def list_cached_compounds(request):
    """
    Listar compuestos almacenados en cache.
    
    Devuelve los compuestos más utilizados desde el cache local,
    ordenados por frecuencia de acceso.
    
    **Método:** GET
    **URL:** /api/structures/cached-compounds/
    
    **Parámetros de query:**
    - limit (int, opcional): Número máximo de resultados (default: 20, max: 100)
    
    **Respuesta exitosa (200):**
    ```json
    [
        {
            "query": "water",
            "query_type": "name",
            "molecular_formula": "H2O",
            "iupac_name": "oxidane",
            "smiles": "O",
            "access_count": 150,
            "last_accessed": "2025-08-11T20:00:00Z"
        },
        {
            "query": "methane",
            "query_type": "name",
            "molecular_formula": "CH4",
            "iupac_name": "methane",
            "smiles": "C",
            "access_count": 75,
            "last_accessed": "2025-08-11T19:30:00Z"
        }
    ]
    ```
    
    **Notas:**
    - Útil para mostrar búsquedas populares
    - Ordenado por frecuencia de uso
    """
    limit = request.GET.get('limit', 20)
    try:
        limit = min(int(limit), 100)  # Máximo 100 resultados
    except (ValueError, TypeError):
        limit = 20
    
    compounds = CompoundCache.objects.all()[:limit]
    
    result = []
    for compound in compounds:
        result.append({
            'query': compound.query,
            'query_type': compound.query_type,
            'molecular_formula': compound.molecular_formula,
            'iupac_name': compound.iupac_name,
            'smiles': compound.smiles,
            'pubchem_cid': compound.pubchem_cid,
            'access_count': compound.access_count,
            'last_accessed': compound.last_accessed.isoformat(),
            'common_names': compound.common_names[:3] if compound.common_names else []
        })
    
    return Response(result, status=status.HTTP_200_OK)
