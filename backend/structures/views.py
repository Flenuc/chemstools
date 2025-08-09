from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import LewisStructureGenerator
from .serializers import FormulaInputSerializer, LewisStructureSerializer
from .models import MolecularStructure


@api_view(['POST'])
def generate_lewis_structure(request):
    """
    Generate Lewis structure from molecular formula
    
    POST /backend/structures/lewis-generator/
    Body: {"formula": "H2O"}
    """
    serializer = FormulaInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    formula = serializer.validated_data['formula']
    
    # Check if structure already exists
    try:
        existing = MolecularStructure.objects.get(formula=formula)
        return Response(
            LewisStructureSerializer(existing).data,
            status=status.HTTP_200_OK
        )
    except MolecularStructure.DoesNotExist:
        pass
    
    # Generate new structure
    result = LewisStructureGenerator.generate_lewis_structure(formula)
    
    if not result['success']:
        return Response(
            {'error': 'Failed to generate Lewis structure', 'details': result['error']},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save to database
    structure = MolecularStructure.objects.create(
        formula=formula,
        mol_data=result['mol_data'],
        lewis_data=result['lewis_data']
    )
    
    return Response(
        LewisStructureSerializer(structure).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def list_structures(request):
    """List all generated structures"""
    structures = MolecularStructure.objects.all()[:20]  # Limit to 20 most recent
    serializer = LewisStructureSerializer(structures, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_structure(request, structure_id):
    """Get specific structure by ID"""
    try:
        structure = MolecularStructure.objects.get(id=structure_id)
        serializer = LewisStructureSerializer(structure)
        return Response(serializer.data)
    except MolecularStructure.DoesNotExist:
        return Response(
            {'error': 'Structure not found'},
            status=status.HTTP_404_NOT_FOUND
        )