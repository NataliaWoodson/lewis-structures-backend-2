from lewis_structures_main.models import Molecule
from rest_framework import serializers

class MoleculeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Molecule
        fields = ["molecule_id", "molecular_formula"]
