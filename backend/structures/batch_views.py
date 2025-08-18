"""
Batch Processing API Views
===========================
API endpoints for batch processing of molecular structures
with parallel computation and real-time progress tracking.
"""

import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from django.core.cache import cache
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from core.parallel_computing import get_default_executor
from core.intelligent_cache import get_intelligent_cache
from .parallel_utils import ParallelLewisGenerator, get_default_parallel_generator
from .serializers import LewisStructureSerializer

logger = logging.getLogger(__name__)


class BatchProcessingThrottle(UserRateThrottle):
    """Custom throttle for batch processing endpoints"""
    rate = '100/hour'  # 100 batch requests per hour for authenticated users


class AnonymousBatchThrottle(AnonRateThrottle):
    """Custom throttle for anonymous batch processing"""
    rate = '10/hour'  # 10 batch requests per hour for anonymous users


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([BatchProcessingThrottle, AnonymousBatchThrottle])
def batch_generate_structures(request):
    """
    Generate multiple Lewis structures in parallel.
    
    **Method:** POST
    **URL:** /api/structures/batch/generate/
    
    **Request Body:**
    ```json
    {
        "formulas": ["H2O", "NH3", "CH4", "CO2"],
        "options": {
            "validate": true,
            "calculate_properties": true,
            "optimize_coordinates": true,
            "max_workers": 4,
            "cache_ttl": 7200
        }
    }
    ```
    
    **Response (200):**
    ```json
    {
        "job_id": "uuid-string",
        "status": "completed",
        "total": 4,
        "successful": 4,
        "failed": 0,
        "processing_time": 1.23,
        "results": [
            {
                "formula": "H2O",
                "success": true,
                "structure": {...},
                "properties": {...},
                "validation": {...}
            },
            ...
        ],
        "errors": [],
        "metrics": {
            "cache_hits": 2,
            "cache_misses": 2,
            "avg_time_per_structure": 0.31
        }
    }
    ```
    """
    try:
        data = request.data
        formulas = data.get('formulas', [])
        options = data.get('options', {})
        
        if not formulas:
            return Response(
                {'error': 'No formulas provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(formulas) > 100:
            return Response(
                {'error': 'Maximum 100 formulas per batch request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize parallel generator with options
        generator = ParallelLewisGenerator(
            max_workers=options.get('max_workers'),
            cache_ttl=options.get('cache_ttl', 7200)
        )
        
        # Track processing time
        start_time = timezone.now()
        
        # Generate structures in parallel
        logger.info(f"Starting batch generation for job {job_id}: {len(formulas)} formulas")
        
        results = []
        errors = []
        
        # Generate structures
        structures = generator.generate_batch_structures(formulas)
        
        # Process each structure
        for i, formula in enumerate(formulas):
            result = {
                'formula': formula,
                'success': False,
                'structure': None,
                'properties': None,
                'validation': None
            }
            
            # Find corresponding structure
            structure = None
            for struct in structures:
                if struct and struct.get('lewis_data', {}).get('formula', '').upper() == formula.upper():
                    structure = struct
                    break
            
            if structure and structure.get('success'):
                result['success'] = True
                result['structure'] = structure
                
                # Calculate properties if requested
                if options.get('calculate_properties'):
                    try:
                        # Convert to RDKit mol for property calculation
                        from rdkit import Chem
                        mol_block = structure.get('mol_data')
                        if mol_block:
                            mol = Chem.MolFromMolBlock(mol_block)
                            if mol:
                                properties = generator.calculate_properties_parallel([mol])[0]
                                result['properties'] = properties
                    except Exception as e:
                        logger.error(f"Failed to calculate properties for {formula}: {e}")
                
                # Validate if requested
                if options.get('validate'):
                    validations = generator.validate_structures_parallel([structure])
                    if validations:
                        result['validation'] = validations[0]
            else:
                errors.append({
                    'formula': formula,
                    'error': 'Failed to generate structure'
                })
            
            results.append(result)
        
        # Calculate metrics
        end_time = timezone.now()
        processing_time = (end_time - start_time).total_seconds()
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        # Get performance metrics
        perf_metrics = generator.get_performance_metrics()
        cache_metrics = perf_metrics.get('cache_metrics', {})
        
        response_data = {
            'job_id': job_id,
            'status': 'completed',
            'total': len(formulas),
            'successful': successful,
            'failed': failed,
            'processing_time': processing_time,
            'results': results,
            'errors': errors,
            'metrics': {
                'cache_hits': cache_metrics.get('hits', 0),
                'cache_misses': cache_metrics.get('misses', 0),
                'cache_hit_rate': cache_metrics.get('hit_rate', 0),
                'avg_time_per_structure': processing_time / len(formulas) if formulas else 0,
                'system_load': perf_metrics.get('load_level', 'unknown')
            }
        }
        
        # Cache the results for later retrieval
        cache.set(f'batch_job:{job_id}', response_data, timeout=3600)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([BatchProcessingThrottle])
def batch_validate_structures(request):
    """
    Validate multiple molecular structures in parallel.
    
    **Method:** POST
    **URL:** /api/structures/batch/validate/
    
    **Request Body:**
    ```json
    {
        "structures": [
            {"formula": "H2O", "lewis_data": {...}},
            {"formula": "NH3", "lewis_data": {...}}
        ],
        "options": {
            "strict": false,
            "check_3d": false
        }
    }
    ```
    
    **Response (200):**
    ```json
    {
        "job_id": "uuid-string",
        "total": 2,
        "valid": 2,
        "invalid": 0,
        "validations": [
            {
                "formula": "H2O",
                "valid": true,
                "errors": [],
                "warnings": []
            },
            ...
        ]
    }
    ```
    """
    try:
        data = request.data
        structures = data.get('structures', [])
        options = data.get('options', {})
        
        if not structures:
            return Response(
                {'error': 'No structures provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize parallel generator
        generator = get_default_parallel_generator()
        
        # Validate structures in parallel
        logger.info(f"Starting batch validation for job {job_id}: {len(structures)} structures")
        
        validations = generator.validate_structures_parallel(structures)
        
        # Count valid/invalid
        valid_count = sum(1 for v in validations if v.get('valid'))
        invalid_count = len(validations) - valid_count
        
        # Combine with input data
        results = []
        for i, validation in enumerate(validations):
            if i < len(structures):
                result = {
                    'formula': structures[i].get('formula', f'Structure_{i}'),
                    **validation
                }
                results.append(result)
        
        response_data = {
            'job_id': job_id,
            'total': len(structures),
            'valid': valid_count,
            'invalid': invalid_count,
            'validations': results
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Batch validation error: {e}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def stream_batch_generation(request):
    """
    Stream batch generation results as they complete.
    
    **Method:** POST
    **URL:** /api/structures/batch/stream/
    
    **Request Body:**
    ```json
    {
        "formulas": ["H2O", "NH3", "CH4", ...],
        "options": {
            "chunk_size": 5
        }
    }
    ```
    
    **Response:** Server-Sent Events stream
    ```
    data: {"event": "progress", "completed": 1, "total": 10, "formula": "H2O", "success": true}
    data: {"event": "progress", "completed": 2, "total": 10, "formula": "NH3", "success": true}
    ...
    data: {"event": "complete", "total": 10, "successful": 9, "failed": 1}
    ```
    """
    def event_stream():
        """Generate server-sent events"""
        try:
            data = json.loads(request.body)
            formulas = data.get('formulas', [])
            options = data.get('options', {})
            
            if not formulas:
                yield f'data: {json.dumps({"event": "error", "message": "No formulas provided"})}\n\n'
                return
            
            # Initialize generator
            generator = ParallelLewisGenerator(
                max_workers=options.get('max_workers'),
                cache_ttl=options.get('cache_ttl', 7200)
            )
            
            completed = 0
            successful = 0
            failed = 0
            
            # Process in chunks
            chunk_size = options.get('chunk_size', 5)
            
            for i in range(0, len(formulas), chunk_size):
                chunk = formulas[i:i + chunk_size]
                
                # Generate structures for this chunk
                chunk_results = generator.generate_batch_structures(chunk)
                
                # Send progress for each structure
                for j, formula in enumerate(chunk):
                    completed += 1
                    success = False
                    
                    # Check if generation was successful
                    if j < len(chunk_results) and chunk_results[j].get('success'):
                        success = True
                        successful += 1
                    else:
                        failed += 1
                    
                    # Send progress event
                    event = {
                        "event": "progress",
                        "completed": completed,
                        "total": len(formulas),
                        "formula": formula,
                        "success": success
                    }
                    
                    if success and j < len(chunk_results):
                        event["structure"] = chunk_results[j]
                    
                    yield f'data: {json.dumps(event)}\n\n'
            
            # Send completion event
            completion_event = {
                "event": "complete",
                "total": len(formulas),
                "successful": successful,
                "failed": failed
            }
            yield f'data: {json.dumps(completion_event)}\n\n'
            
        except Exception as e:
            logger.error(f"Stream generation error: {e}")
            yield f'data: {json.dumps({"event": "error", "message": str(e)})}\n\n'
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def get_batch_job_status(request, job_id):
    """
    Get the status of a batch processing job.
    
    **Method:** GET
    **URL:** /api/structures/batch/status/{job_id}/
    
    **Response (200):**
    ```json
    {
        "job_id": "uuid-string",
        "status": "completed",
        "total": 10,
        "successful": 9,
        "failed": 1,
        "processing_time": 2.34,
        "results": [...]
    }
    ```
    """
    try:
        # Try to get job from cache
        job_data = cache.get(f'batch_job:{job_id}')
        
        if not job_data:
            return Response(
                {'error': 'Job not found or expired'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(job_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving job status: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_performance_metrics(request):
    """
    Get current performance metrics for the batch processing system.
    
    **Method:** GET
    **URL:** /api/structures/batch/metrics/
    
    **Response (200):**
    ```json
    {
        "cache": {
            "hits": 1234,
            "misses": 567,
            "hit_rate": 68.5,
            "total_size_mb": 45.2
        },
        "parallel": {
            "max_workers": 8,
            "executor_type": "thread"
        },
        "system": {
            "cpu_percent": 45.2,
            "memory_percent": 62.1,
            "load_level": "medium"
        }
    }
    ```
    """
    try:
        generator = get_default_parallel_generator()
        metrics = generator.get_performance_metrics()
        
        return Response(metrics, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        return Response(
            {'error': 'Failed to retrieve metrics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
