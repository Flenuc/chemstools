from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rdkit import Chem
from rdkit.Chem import Descriptors

class HealthCheckView(APIView):
    """
    Endpoint simple para verificar que el servidor está funcionando.
    """
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

class MolecularWeightCalculatorView(APIView):
    """
    Endpoint para calcular el peso molecular de una fórmula química.
    """
    def post(self, request, *args, **kwargs):
        formula = request.data.get('formula', '')
        if not formula:
            return Response(
                {"error": "Se requiere una fórmula."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Crear un objeto molécula a partir de la fórmula
            mol = Chem.MolFromSmiles(formula) # Para fórmulas simples, SMILES funciona
            if mol is None:
                # Intento alternativo para fórmulas como 'H2O'
                # Esto es una simplificación, RDKit prefiere formatos como SMILES.
                # Para un prototipo, manejaremos casos comunes.
                # Una implementación más robusta necesitaría un parser de fórmulas.
                # Por ahora, vamos a simularlo para 'H2O' y 'C6H12O6'
                if formula.upper() == 'H2O':
                    mol = Chem.MolFromSmiles('O')
                elif formula.upper() == 'C6H12O6':
                     mol = Chem.MolFromSmiles('C(C(C(C(C(C=O)O)O)O)O)O')
                else:
                    raise ValueError("Fórmula inválida o no soportada")

            # Calcular el peso molecular
            molecular_weight = Descriptors.MolWt(mol)

            return Response(
                {"formula": formula, "molecular_weight": molecular_weight},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"No se pudo procesar la fórmula: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )