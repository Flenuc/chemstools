"""
Parallelized Lewis Structure Utilities
=======================================
Optimized version of structure generation utilities using parallel processing
and intelligent caching for improved performance.

Features:
- Parallel molecular structure generation
- Batch processing for multiple molecules
- Intelligent caching with adaptive TTL
- Performance monitoring and metrics
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, AllChem

from core.parallel_computing import (
    ParallelExecutor,
    ParallelConfig,
    ExecutorType,
    parallel_map,
    parallelize
)
from core.intelligent_cache import (
    IntelligentCache,
    CacheConfig,
    CacheStrategy,
    cached,
    get_intelligent_cache
)
from .utils import LewisStructureGenerator
from .simple_structures import get_simple_structure

logger = logging.getLogger(__name__)


class ParallelLewisGenerator:
    """
    Enhanced Lewis structure generator with parallel processing capabilities.
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        enable_cache: bool = True,
        cache_ttl: int = 7200  # 2 hours default
    ):
        """
        Initialize parallel Lewis generator.
        
        Args:
            max_workers: Maximum number of parallel workers
            enable_cache: Whether to enable caching
            cache_ttl: Cache time-to-live in seconds
        """
        # Initialize parallel executor
        self.parallel_config = ParallelConfig(
            max_workers=max_workers,
            executor_type=ExecutorType.THREAD,  # RDKit works well with threads
            timeout=60.0,
            chunk_size=5,
            enable_cache=enable_cache,
            cache_ttl=cache_ttl,
            fallback_to_sequential=True
        )
        self.executor = ParallelExecutor(self.parallel_config)
        
        # Initialize intelligent cache
        self.cache_config = CacheConfig(
            default_ttl=cache_ttl,
            strategy=CacheStrategy.ADAPTIVE,
            enable_compression=True,
            compression_threshold=512,  # Compress structures > 512 bytes
            enable_metrics=True
        )
        self.cache = IntelligentCache(self.cache_config)
        
        # Base generator for single structures
        self.base_generator = LewisStructureGenerator()
        
    def generate_single_structure(
        self,
        formula: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a single Lewis structure with caching.
        
        Args:
            formula: Molecular formula or SMILES
            force_refresh: Force regeneration even if cached
            
        Returns:
            Structure data dictionary
        """
        # Define compute function for cache
        def compute_structure():
            logger.debug(f"Computing structure for {formula}")
            
            # Check for hardcoded simple structure first
            simple_struct = get_simple_structure(formula)
            if simple_struct:
                mol_block = self.base_generator.generate_mol_block_from_lewis(simple_struct)
                return {
                    'mol_data': mol_block,
                    'lewis_data': simple_struct,
                    'success': True,
                    'source': 'hardcoded'
                }
            
            # Check if ionic compound
            if self.base_generator.is_ionic_compound(formula):
                return self.base_generator.generate_ionic_structure(formula)
            
            # Generate using RDKit
            return self.base_generator.generate_lewis_structure(formula)
        
        # Use intelligent cache
        result = self.cache.get(
            namespace='lewis_structures',
            identifier=formula.upper(),
            compute_func=compute_structure,
            force_refresh=force_refresh
        )
        
        return result
    
    def generate_batch_structures(
        self,
        formulas: List[str],
        return_partial: bool = True,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple Lewis structures in parallel.
        
        Args:
            formulas: List of molecular formulas
            return_partial: Return successful results even if some fail
            progress_callback: Function called with progress updates
            
        Returns:
            List of structure data dictionaries
        """
        if not formulas:
            return []
        
        logger.info(f"Generating {len(formulas)} structures in parallel")
        start_time = time.time()
        
        # Cache key function for parallel processing
        def cache_key_func(formula: str) -> str:
            return f"lewis_structures:{formula.upper()}"
        
        # Process in parallel with caching
        results = self.executor.map_parallel(
            func=self.generate_single_structure,
            items=formulas,
            operation_name="batch_lewis_generation",
            use_cache=True,
            cache_key_func=cache_key_func
        )
        
        # Filter results if needed
        if return_partial:
            valid_results = []
            for i, result in enumerate(results):
                if result and result.get('success'):
                    valid_results.append(result)
                else:
                    logger.warning(f"Failed to generate structure for {formulas[i]}")
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(i + 1, len(formulas))
            
            results = valid_results
        
        duration = time.time() - start_time
        logger.info(f"Generated {len(results)} structures in {duration:.2f}s")
        
        return results
    
    def optimize_coordinates_parallel(
        self,
        molecules: List[Chem.Mol]
    ) -> List[Chem.Mol]:
        """
        Optimize 2D coordinates for multiple molecules in parallel.
        
        Args:
            molecules: List of RDKit molecule objects
            
        Returns:
            List of molecules with optimized coordinates
        """
        def optimize_single(mol: Chem.Mol) -> Chem.Mol:
            """Optimize coordinates for a single molecule"""
            try:
                # Generate 2D coordinates
                AllChem.Compute2DCoords(mol)
                
                # Apply custom optimization for simple molecules
                if mol.GetNumAtoms() < 10:
                    mol = self.base_generator.optimize_simple_molecule_coords(mol)
                
                return mol
            except Exception as e:
                logger.error(f"Failed to optimize coordinates: {e}")
                return mol
        
        # Process in parallel
        return self.executor.map_parallel(
            func=optimize_single,
            items=molecules,
            operation_name="coordinate_optimization"
        )
    
    def calculate_properties_parallel(
        self,
        molecules: List[Chem.Mol]
    ) -> List[Dict[str, Any]]:
        """
        Calculate molecular properties for multiple molecules in parallel.
        
        Args:
            molecules: List of RDKit molecule objects
            
        Returns:
            List of property dictionaries
        """
        def calculate_single(mol: Chem.Mol) -> Dict[str, Any]:
            """Calculate properties for a single molecule"""
            try:
                # Calculate various molecular properties
                properties = {
                    'molecular_weight': rdMolDescriptors.CalcExactMolWt(mol),
                    'formula': rdMolDescriptors.CalcMolFormula(mol),
                    'num_atoms': mol.GetNumAtoms(),
                    'num_bonds': mol.GetNumBonds(),
                    'num_heavy_atoms': mol.GetNumHeavyAtoms(),
                    'num_rotatable_bonds': rdMolDescriptors.CalcNumRotatableBonds(mol),
                    'num_h_acceptors': rdMolDescriptors.CalcNumHBA(mol),
                    'num_h_donors': rdMolDescriptors.CalcNumHBD(mol),
                    'tpsa': rdMolDescriptors.CalcTPSA(mol),
                    'logp': rdMolDescriptors.CalcCrippenDescriptors(mol)[0]
                }
                
                # Calculate formal charges
                formal_charges = self.base_generator.calculate_formal_charges(mol)
                properties['formal_charges'] = formal_charges
                properties['total_charge'] = sum(formal_charges)
                
                # Calculate lone pairs
                lone_pairs = self.base_generator.get_lone_pairs(mol)
                properties['lone_pairs'] = lone_pairs
                properties['total_lone_pairs'] = sum(lone_pairs)
                
                return properties
                
            except Exception as e:
                logger.error(f"Failed to calculate properties: {e}")
                return {}
        
        # Process in parallel with caching
        return self.executor.map_parallel(
            func=calculate_single,
            items=molecules,
            operation_name="property_calculation",
            use_cache=True,
            cache_key_func=lambda mol: f"mol_properties:{Chem.MolToSmiles(mol)}"
        )
    
    def validate_structures_parallel(
        self,
        structures: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple Lewis structures in parallel.
        
        Args:
            structures: List of structure data dictionaries
            
        Returns:
            List of validation results
        """
        def validate_single(structure: Dict[str, Any]) -> Dict[str, Any]:
            """Validate a single structure"""
            try:
                validation = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                
                lewis_data = structure.get('lewis_data', {})
                
                # Check if structure exists
                if not lewis_data:
                    validation['valid'] = False
                    validation['errors'].append("No Lewis data found")
                    return validation
                
                # Validate electron count
                total_electrons = lewis_data.get('total_valence_electrons', 0)
                atoms = lewis_data.get('atoms', [])
                bonds = lewis_data.get('bonds', [])
                
                # Count electrons in bonds
                bond_electrons = sum(bond.get('order', 1) * 2 for bond in bonds)
                
                # Count lone pair electrons
                lone_pair_electrons = sum(
                    atom.get('lone_pairs', 0) * 2 for atom in atoms
                )
                
                # Check electron conservation
                used_electrons = bond_electrons + lone_pair_electrons
                if used_electrons != total_electrons:
                    validation['warnings'].append(
                        f"Electron count mismatch: {used_electrons} used vs {total_electrons} total"
                    )
                
                # Check formal charges
                total_charge = sum(atom.get('formal_charge', 0) for atom in atoms)
                if total_charge != 0:
                    validation['warnings'].append(
                        f"Non-zero total formal charge: {total_charge}"
                    )
                
                # Check connectivity
                if len(atoms) > 1 and len(bonds) == 0:
                    validation['errors'].append("Multi-atom structure with no bonds")
                    validation['valid'] = False
                
                return validation
                
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return {
                    'valid': False,
                    'errors': [str(e)],
                    'warnings': []
                }
        
        # Process in parallel
        return self.executor.map_parallel(
            func=validate_single,
            items=structures,
            operation_name="structure_validation"
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the parallel generator.
        
        Returns:
            Dictionary with performance metrics
        """
        metrics = {
            'cache_metrics': self.cache.get_metrics(),
            'parallel_metrics': {
                'max_workers': self.parallel_config.max_workers,
                'executor_type': self.parallel_config.executor_type.value,
                'cache_enabled': self.parallel_config.enable_cache,
                'cache_ttl': self.parallel_config.cache_ttl
            }
        }
        
        # Get system load information
        from core.intelligent_cache import SystemLoadMonitor
        load_monitor = SystemLoadMonitor()
        metrics['system_load'] = load_monitor.get_system_load()
        metrics['load_level'] = load_monitor.get_load_level()
        
        return metrics


# Convenience functions using default parallel generator
_default_generator = None


def get_default_parallel_generator() -> ParallelLewisGenerator:
    """Get or create default parallel generator instance"""
    global _default_generator
    if _default_generator is None:
        _default_generator = ParallelLewisGenerator()
    return _default_generator


@cached(namespace='lewis_structures', ttl=7200)
def generate_structure_cached(formula: str) -> Dict[str, Any]:
    """
    Generate a Lewis structure with caching.
    
    Args:
        formula: Molecular formula or SMILES
        
    Returns:
        Structure data dictionary
    """
    generator = get_default_parallel_generator()
    return generator.generate_single_structure(formula)


def generate_structures_batch(
    formulas: List[str],
    max_workers: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple Lewis structures in parallel.
    
    Args:
        formulas: List of molecular formulas
        max_workers: Maximum number of parallel workers
        
    Returns:
        List of structure data dictionaries
    """
    generator = ParallelLewisGenerator(max_workers=max_workers)
    return generator.generate_batch_structures(formulas)


# Parallel decorator for structure generation
@parallelize(
    operation_name="parallel_lewis_generation",
    use_cache=True,
    cache_ttl=7200
)
def generate_structures_parallel(formulas: List[str]) -> List[Dict[str, Any]]:
    """
    Decorator-based parallel structure generation.
    
    Args:
        formulas: List of molecular formulas
        
    Returns:
        List of structure data dictionaries
    """
    # This will be automatically parallelized by the decorator
    generator = LewisStructureGenerator()
    return [generator.generate_lewis_structure(f) for f in formulas]
