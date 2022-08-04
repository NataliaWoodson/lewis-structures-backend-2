from django.shortcuts import get_object_or_404
from lewis_structures_main.helper_functions import get_record_by_id
from lewis_structures_main.models import Molecule
from rest_framework import viewsets, permissions
from lewis_structures_main.serializers import MoleculeSerializer
from django.http import JsonResponse
import requests
import os
from random import randint
from rest_framework.decorators import authentication_classes

# def index(request):
#     return HttpResponse("Hello, world. You're at the polls index.")

# class MoleculeViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows molecules to be viewed or edited
#     """

#     queryset = Molecule.objects.all().order_by("molecule_id")
#     serializer_class = MoleculeSerializer
#     permission_classes = [permissions.IsAuthenticated]
@authentication_classes([])
def get_molecule_list(request):
    molecules = Molecule.objects.all()
    data = {"molecules": list(molecules.values("molecule_id", "molecular_formula"))}
    return JsonResponse(data)

def get_molecule_by_id(request, id):
    molecule = get_object_or_404(Molecule, pk=id)
    data = {
            "molecule_id": molecule.molecule_id,
            "molecular_formula": molecule.molecular_formula
        }

    return JsonResponse(data)


apiUrl = "https://api.rsc.org/compounds/v1/filter/element"
apiKey = os.environ.get("API_KEY")

def index(request):
    '''
    Given params, make GET request to API, returns query id
    '''
    params = {
        "includeElements":["H", "B", "C", "N", "O", "F", "Al", "Si", "P", "S", "Cl"],
        "excludeElements":["He", "Li", "Be", "Ne", "Na", "Mg", "Ar", "K", "Ca", "Sc", "Ti", "V"],
        "orderBy": "molecularWeight"
    }
    response = requests.post(apiUrl, headers = {'apikey': apiKey}, json = params) 
    elementRequest = response.json()
    elementRequestDisplay= get_query_status(elementRequest)
    for formula in elementRequestDisplay:
        if not Molecule.objects.filter(molecular_formula=formula).exists():
        # if formula not in Molecule.objects.all():
        # call to database to see if it exists
        # if it does, pass
        # else, add it
            formula_data = Molecule(
                molecular_formula = formula
            )
            formula_data.save()
            all_formulas = Molecule.objects.all().order_by('molecule_id')
    return JsonResponse(elementRequestDisplay, safe=False)


def get_query_status(query_id):
    '''
    Given query id, request query status, returns query status
    '''
    query_id = query_id["queryId"]
    response = requests.get(f'https://api.rsc.org/compounds/v1/filter/{query_id}/status', headers={'apikey': apiKey})
    queryResultDisplay = get_query_result(query_id)
    return queryResultDisplay

# put in for loop
def get_query_result(query_id):
    '''
    Given query id, request query results, returns dict with list of query results
    '''
    #randomize the molecules
    params={
        "start": randint(0,890),
        # "start": 300,
        # "start": 200,
        "count": 100
    }
    response = requests.get(f'https://api.rsc.org/compounds/v1/filter/{query_id}/results', params = params, headers={'apikey': apiKey})
    data = response.json()
    getMolecularDisplay = get_molecular_data(data["results"])
    return getMolecularDisplay

def get_molecular_data(data):
    '''
    Given dict containing list of query results, get molecular data
    Returns dicts with lists of dicts containing molecular data
    '''
    params={
        "recordIds":data,
        "fields": ["commonName", "stdinchiKey", "molecularWeight"]
    }

    response = requests.post(f'https://api.rsc.org/compounds/v1/records/batch', json = params, headers={'apikey': apiKey})
    data = response.json()
    filterMolecularData = filter_molecular_data(data)
    return filterMolecularData
    # filtered_charge = filtered_by_charge(data["records"])
    # return filtered_charge
    
# filter out common name constraint and return a list with valid molecules
def filter_molecular_data(data):
    filtered_molecules = []
    #as we go thru every molecule and we check every name and see if that is in our common names and if it is, skip it(molecule) and not add it to our list.
    #Given, do, return
    for molecule in data["records"]:        
        if isMoleculeInCommonName(molecule) == False:
            filtered_molecules.append(molecule)
    # return filtered_molecules
    filtered_charge = filtered_by_charge(filtered_molecules)
    return filtered_charge

#helper function
def isMoleculeInCommonName(molecule):
    if "commonName" not in molecule:
        return True
    common_names = ["ion", "ide", "ite", "ate", "ic", "ous", "ium", "hypo", "yl", "per", "(", ")", "I", "$"]
    for name in common_names:
        molecule_name = molecule["commonName"]
        molecule_name = molecule_name.replace(" ", "")

        if name in molecule_name:
            return True
    return False

def filtered_by_charge(filtered_data):
    filtered_molecules = []
    for molecule in filtered_data:
        stdinchi_key = molecule['stdinchiKey']
        response = requests.get(f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{stdinchi_key}/property/MolecularFormula,Charge,Complexity/JSON')
        data = response.json()
        if "Fault" in data:
            continue
        elif data["PropertyTable"]["Properties"][0]["Charge"] == 0:
            filtered_molecules.append(data["PropertyTable"]["Properties"][0]["MolecularFormula"])
    remove_singles = filter_for_single_elements(filtered_molecules)
    return remove_singles

def filter_for_single_elements(filtered_data):
    filtered_molecules = []
    for molecule in filtered_data:
        if len(molecule) > 1 or len(molecule) == 2 and not molecule[1].islower():
            filtered_molecules.append(molecule)
    filter_for_atoms = filter_atoms(filtered_molecules)
    return filter_for_atoms

final_list = []
def filter_atoms(filtered_data):
    for molecule in filtered_data:
        if not molecule.isalpha():
            filter_for_max_atoms(molecule)
        else: 
            count = len(molecule)
            if count <= 6:
                final_list.append(molecule)
    final_set = create_formula_set(final_list)
    return final_set
    
def create_formula_set(filtered_data):
    final_set = set(filtered_data)
    json_list = list(final_set)
    return json_list

    

# helper function to filter atoms
def filter_for_max_atoms(molecule):
    count  = 0
    for char in range(len(molecule) - 1):
        if (molecule[char + 1]).isdigit():
            count += int(molecule[char + 1])
        else:
            count += 1
    if count <= 6:
        final_list.append(molecule)
    return final_list