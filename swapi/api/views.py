import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Planet, People
from api.fixtures import SINGLE_PEOPLE_OBJECT, PEOPLE_OBJECTS
from api.serializers import serialize_people_as_json


def single_people(request):
    return JsonResponse(SINGLE_PEOPLE_OBJECT)


def list_people(request):
    return JsonResponse(PEOPLE_OBJECTS, safe=False)


@csrf_exempt
def people_list_view(request):
    """
    People `list` actions:

    Based on the request method, perform the following actions:

        * GET: Return the list of all `People` objects in the database.

        * POST: Create a new `People` object using the submitted JSON payload.

    Make sure you add at least these validations:

        * If the view receives another HTTP method out of the ones listed
          above, return a `400` response.

        * If submited payload is not JSON valid, return a `400` response.
    """
    if request.method == 'GET':
        try:
            people = [serialize_people_as_json(person) for person in People.objects.all()]
        except:
            return JsonResponse({
                'error': True, 
                'msg': 'Error. Please try again.'
            }, status = 400)
        data = people
        status = 200
    elif request.method == 'POST':
        try:
            payload = json.loads(request.body.decode())
            person = People.objects.create(
                name = payload['name'],
                homeworld = Planet.objects.get(id=payload['homeworld']),
                height = payload['height'],
                mass = payload['mass'],
                hair_color = payload['hair_color']
            )
        except:
            return JsonResponse({
                'error': True, 
                'msg': 'Error creating person. Please try again.'
            }, status = 400)            
        data = serialize_people_as_json(person)
        status = 201
    else:
        data = {'error': True, 'msg': 'HTTP method must be GET or POST.'}
        status = 400
    return JsonResponse(data, status=status, safe=False)

@csrf_exempt
def people_detail_view(request, people_id):
    """
    People `detail` actions:

    Based on the request method, perform the following actions:

        * GET: Returns the `People` object with given `people_id`.

        * PUT/PATCH: Updates the `People` object either partially (PATCH)
          or completely (PUT) using the submitted JSON payload.

        * DELETE: Deletes `People` object with given `people_id`.

    Make sure you add at least these validations:

        * If the view receives another HTTP method out of the ones listed
          above, return a `400` response.

        * If submited payload is not JSON valid, return a `400` response.
    """
    if request.body:
        try:
            payload = json.loads(request.body.decode())
        except:
            return JsonResponse({'error': True, 'msg': 'Invalid JSON payload'},
            status = 400)
    
    try:
        person = People.objects.get(id=people_id)
    except People.DoesNotExist:
        return JsonResponse({'error': True, 'msg': 'Person does not exist'},
        status = 400)    
    
    if request.method == 'GET':
        data = serialize_people_as_json(person)
        status = 200
    elif request.method in ['PUT', 'PATCH']:
        for field in payload:
                setattr(person, field, payload[field])
        data = serialize_people_as_json(person)
        status = 200
    elif request.method == 'DELETE':
        deleted = People.objects.get(id=people_id).delete()
        deleted.append({'error': False, 'msg': 'Successfully deleted.'})
        data = deleted
        status = 200
    else:
        data = {'error': True, 'message': 'HTTP method must be GET or POST.'}
        status = 400
        
    return JsonResponse(data=data, status=status, safe=False)