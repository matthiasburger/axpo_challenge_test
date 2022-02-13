from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import InstanceState


class Entity:
    """ base class for all entities, providing some general functions """

    def __json__(self):
        """
        does the json-serializing-things
        :return: the dictionary with all serializable values
        """
        result = dict()
        for k, v in self.__dict__.items():
            if isinstance(v, InstanceState):
                # not serializable, not needed in serializing
                continue

            if isinstance(v, datetime):
                v = v.isoformat()

            if isinstance(v, Decimal):
                v = float(v)

            result[k] = v

        return result

    def get_id(self):
        """
        abstract method for returning the id used for __repr__
        :return: an id of a object
        """
        raise NotImplementedError('get_id has to be implemented')

    def __repr__(self):
        return '<%s %i>' % (self.__class__, self.get_id())
