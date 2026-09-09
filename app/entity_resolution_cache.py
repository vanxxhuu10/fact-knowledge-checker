from entity_resolver import resolve_entities


cache = {}


def get_entity_resolution(subject1, evidence1, subject2, evidence2):

    key = tuple(sorted([subject1, subject2]))

    if key in cache:
        return cache[key]

    result = resolve_entities(
        subject1,
        evidence1,
        subject2,
        evidence2
    )

    cache[key] = result

    return result