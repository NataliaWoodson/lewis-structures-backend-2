from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest


def error_message(message, status_code):
    HttpResponseBadRequest(
        HttpResponse(JsonResponse(dict(details=message)), status_code)
    )


def success_message_info_as_list(message, status_code=200):
    """
    JsonResponse(<data in form of dict instance>)
    HttpResponse()
    """
    return HttpResponse(JsonResponse(message), status_code)


def return_database_info_dict(key, return_value):
    return_dict = {}
    return_dict[key] = return_value
    return HttpResponse(JsonResponse(return_dict))


def get_record_by_id(cls, id):
    try:
        id = int(id)
    except ValueError:
        error_message(f"Invalid id: {id}", 400)
    record = cls.query.get(id)
    if record:
        return record
    else:
        error_message(f"{cls.return_class_name()} id: {id} not found", 404)


def create_record_safely(cls, data_dict):
    try:
        return cls.create_from_dict(data_dict)
    except ValueError as err:
        error_message(f"Invalid data", 400)
    except KeyError as err:
        error_message(
            f"Invalid key(s): {err}.  {cls.return_class_name()} not added to {cls.return_class_name()} List.",
            400,
        )


def update_record_safely(cls, record, data_dict):
    try:
        record.update_self(data_dict)
    except ValueError as err:
        error_message(
            f"Invalid key(s): {err}. {cls.return_class_name()} not updated.", 400
        )
    except KeyError as err:
        error_message(
            f"Missing key(s): {err}. {cls.return_class_name()} not updated.", 400
        )
