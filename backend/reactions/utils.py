# backend/reactions/utils.py
import re
from sympy import symbols, Eq, solve
from collections import defaultdict
from typing import Dict, List, Tuple, Any

class ChemicalEquationBalancer:
    """
    Clase para balancear ecuaciones químicas usando SymPy
    """
    
    @staticmethod
    def parse_compound(compound: str) -> Dict[str, int]:
        """
        Parsea un compuesto químico y devuelve un diccionario con elementos y sus cantidades
        Ej: 'H2O' -> {'H': 2, 'O': 1}
        Ej: 'Ca(OH)2' -> {'Ca': 1, 'O': 2, 'H': 2}
        """
        elements = defaultdict(int)
        
        # Expandir paréntesis primero
        # Buscar patrones como (OH)2, (NO3)3, etc.
        def expand_parentheses(formula):
            import re
            while '(' in formula:
                # Encontrar el grupo entre paréntesis más interno
                match = re.search(r'\(([^()]+)\)(\d*)', formula)
                if not match:
                    break
                
                group_content = match.group(1)
                multiplier = int(match.group(2)) if match.group(2) else 1
                
                # Expandir el contenido del grupo
                expanded = ""
                group_elements = re.findall(r'([A-Z][a-z]?)(\d*)', group_content)
                for element, count in group_elements:
                    element_count = (int(count) if count else 1) * multiplier
                    expanded += f"{element}{element_count if element_count > 1 else ''}"
                
                # Reemplazar el grupo original con la versión expandida
                formula = formula[:match.start()] + expanded + formula[match.end():]
            
            return formula
        
        # Expandir paréntesis
        expanded_compound = expand_parentheses(compound)
        
        # Ahora parsear normalmente
        pattern = r'([A-Z][a-z]?)(\d*)'
        matches = re.findall(pattern, expanded_compound)
        
        for element, count in matches:
            count = int(count) if count else 1
            elements[element] += count
            
        return dict(elements)
    
    @staticmethod
    def parse_equation(equation: str) -> Tuple[List[str], List[str]]:
        """
        Parsea una ecuación química y separa reactivos y productos
        """
        # Limpiar espacios y dividir por ->
        equation = equation.replace(' ', '')
        reactants_str, products_str = equation.split('->')
        
        # Separar por +
        reactants = [r.strip() for r in reactants_str.split('+') if r.strip()]
        products = [p.strip() for p in products_str.split('+') if p.strip()]
        
        return reactants, products
    
    @classmethod
    def balance_equation(cls, equation: str) -> Dict[str, Any]:
        """
        Balancea una ecuación química y devuelve los resultados
        """
        try:
            # Parsear la ecuación
            reactants, products = cls.parse_equation(equation)
            all_compounds = reactants + products
            
            # Obtener todos los elementos únicos
            all_elements = set()
            compound_compositions = {}
            
            for compound in all_compounds:
                composition = cls.parse_compound(compound)
                compound_compositions[compound] = composition
                all_elements.update(composition.keys())
            
            all_elements = list(all_elements)
            
            # Crear variables simbólicas para cada compuesto
            variables = symbols([f'x{i}' for i in range(len(all_compounds))])
            
            # Crear ecuaciones para cada elemento
            equations = []
            for element in all_elements:
                reactant_sum = sum(
                    variables[i] * compound_compositions[reactants[i]].get(element, 0)
                    for i in range(len(reactants))
                )
                product_sum = sum(
                    variables[len(reactants) + i] * compound_compositions[products[i]].get(element, 0)
                    for i in range(len(products))
                )
                equations.append(Eq(reactant_sum, product_sum))
            
            # Agregar constraint: el primer coeficiente = 1 (para evitar solución trivial)
            equations.append(Eq(variables[0], 1))
            
            # Resolver el sistema de ecuaciones
            solution = solve(equations, variables)
            
            if not solution:
                return {
                    'success': False,
                    'error': 'No se pudo encontrar una solución para balancear la ecuación',
                    'original_equation': equation
                }
            
            # Convertir a enteros positivos
            coefficients = []
            for var in variables:
                coeff = float(solution[var]) if var in solution else 1.0
                coefficients.append(coeff)
            
            # Encontrar el denominador común para convertir a enteros
            from fractions import Fraction
            fractions = [Fraction(c).limit_denominator() for c in coefficients]
            lcm_denominator = 1
            for frac in fractions:
                lcm_denominator = lcm_denominator * frac.denominator // cls.gcd(lcm_denominator, frac.denominator)
            
            # Convertir a enteros
            int_coefficients = [int(frac * lcm_denominator) for frac in fractions]
            
            # Construir la ecuación balanceada
            balanced_reactants = []
            for i, reactant in enumerate(reactants):
                coeff = int_coefficients[i]
                if coeff == 1:
                    balanced_reactants.append(reactant)
                else:
                    balanced_reactants.append(f"{coeff}{reactant}")
            
            balanced_products = []
            for i, product in enumerate(products):
                coeff = int_coefficients[len(reactants) + i]
                if coeff == 1:
                    balanced_products.append(product)
                else:
                    balanced_products.append(f"{coeff}{product}")
            
            balanced_equation = f"{' + '.join(balanced_reactants)} -> {' + '.join(balanced_products)}"
            
            # Determinar tipo de reacción
            reaction_type = cls.determine_reaction_type(reactants, products)
            
            return {
                'success': True,
                'original_equation': equation,
                'balanced_equation': balanced_equation,
                'coefficients': {
                    'reactants': int_coefficients[:len(reactants)],
                    'products': int_coefficients[len(reactants):],
                    'compounds': dict(zip(all_compounds, int_coefficients))
                },
                'reaction_type': reaction_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al balancear la ecuación: {str(e)}',
                'original_equation': equation
            }
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Calcula el máximo común divisor"""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def determine_reaction_type(reactants: List[str], products: List[str]) -> str:
        """
        Determina el tipo de reacción química básico
        """
        if len(reactants) == 2 and len(products) == 1:
            return "síntesis"
        elif len(reactants) == 1 and len(products) >= 2:
            return "descomposición"
        elif any('O2' in reactant for reactant in reactants) and \
             any('CO2' in product or 'H2O' in product for product in products):
            return "combustión"
        elif len(reactants) == 2 and len(products) == 2:
            return "sustitución simple"
        else:
            return "otros"