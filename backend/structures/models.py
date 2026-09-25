from django.db import models
from django.utils import timezone


class MolecularStructure(models.Model):
    """Model to store generated Lewis structures"""
    formula = models.CharField(max_length=100, db_index=True)
    mol_data = models.TextField(help_text="MOL format data")
    lewis_data = models.JSONField(help_text="Lewis structure JSON representation")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['formula']
    
    def __str__(self):
        return f"Lewis Structure: {self.formula}"


class CompoundCache(models.Model):
    """
    Cache local para almacenar información de compuestos obtenidos desde PubChem.
    Esto reduce la latencia y la dependencia de la API externa.
    """
    # Query original del usuario
    query = models.CharField(max_length=500, db_index=True, help_text="Query original (nombre, fórmula, etc)")
    query_type = models.CharField(
        max_length=50, 
        choices=[
            ('name', 'Nombre común'),
            ('iupac', 'Nombre IUPAC'),
            ('smiles', 'SMILES'),
            ('formula', 'Fórmula molecular'),
            ('inchi', 'InChI'),
            ('cas', 'CAS Number')
        ],
        help_text="Tipo de query utilizado"
    )
    
    # Datos del compuesto
    smiles = models.CharField(max_length=1000, help_text="SMILES canónico del compuesto")
    iupac_name = models.CharField(max_length=1000, null=True, blank=True, help_text="Nombre IUPAC oficial")
    common_names = models.JSONField(default=list, help_text="Lista de nombres comunes y sinónimos")
    molecular_formula = models.CharField(max_length=200, help_text="Fórmula molecular")
    molecular_weight = models.FloatField(null=True, blank=True, help_text="Peso molecular")
    
    # Identificadores externos
    pubchem_cid = models.IntegerField(null=True, blank=True, help_text="PubChem Compound ID")
    cas_number = models.CharField(max_length=50, null=True, blank=True, help_text="CAS Registry Number")
    inchi = models.TextField(null=True, blank=True, help_text="InChI string")
    inchi_key = models.CharField(max_length=100, null=True, blank=True, help_text="InChIKey")
    
    # Propiedades adicionales
    properties = models.JSONField(default=dict, help_text="Propiedades adicionales del compuesto")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(default=timezone.now)
    access_count = models.IntegerField(default=1, help_text="Número de veces que se ha accedido")
    
    class Meta:
        unique_together = ['query', 'query_type']
        indexes = [
            models.Index(fields=['smiles']),
            models.Index(fields=['molecular_formula']),
            models.Index(fields=['pubchem_cid']),
        ]
        ordering = ['-access_count', '-last_accessed']
    
    def __str__(self):
        return f"{self.query} ({self.query_type}) -> {self.molecular_formula}"
    
    def increment_access(self):
        """Incrementa el contador de acceso y actualiza la fecha"""
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['access_count', 'last_accessed'])
