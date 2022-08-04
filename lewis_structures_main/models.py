
from django.db import models

class Molecule(models.Model):
    class Meta:
        db_table = "molecule"
    molecule_id = models.BigAutoField(primary_key=True)
    molecular_formula = models.CharField(max_length=50)
    

    def to_freq_map(self):
        # return formula_to_composition(self.molecular_formula)
        pass

    @classmethod
    def create(cls, req_body):
        molecule = cls(molecule_formula=req_body["molecular_formula"])
        return molecule