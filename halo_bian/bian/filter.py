from abc import abstractmethod

from halo_flask.classes import AbsBaseClass
from halo_flask.models import AbsDbMixin


class AbsBianFilter(AbsBaseClass):

    # Operators for scalar (e.g. non-array) columns
    _operators_scalar = {
        # operator => lambda column, value, original_value
        '$eq': lambda col, val, oval: col == val,
        '$ne': lambda col, val, oval: col.is_distinct_from(val),  # (see comment below)
        '$lt': lambda col, val, oval: col < val,
        '$lte': lambda col, val, oval: col <= val,
        '$gt': lambda col, val, oval: col > val,
        '$gte': lambda col, val, oval: col >= val,
        '$prefix': lambda col, val, oval: col.startswith(val),
        '$in': lambda col, val, oval: col.in_(val),  # field IN(values)
        '$nin': lambda col, val, oval: col.notin_(val),  # field NOT IN(values)
        '$exists': lambda col, val, oval: col != None if oval else col == None
    }

    # List of boolean operators, handled by a separate method
    _boolean_operators = frozenset(('$and', '$or', '$nor', '$not'))

    def __init__(self, force_filter=None, scalar_operators=None, array_operators=None, legacy_fields=None):
        pass



    @abstractmethod
    def save_servicing_session(self,servicing_session):
        pass

