import django


def check_if_field_name_exists_on_cls(field_name, cls):
    """
    Check if a field is already present on a model in a `safe` manner that does
    not trigger or violate application loading.
    """
    if django.get_version() < "1.7":
        return field_name in [i.name for i, _ in cls._meta.get_fields_with_model()]
    else:
        exists = field_name in [f.name for f in cls._meta.local_fields]
        if exists:
            return exists
        elif cls._meta.parents:
            return any((
                check_if_field_name_exists_on_cls(field_name, parent) for parent in cls._meta.parents.keys()
            ))
        else:
            return False
