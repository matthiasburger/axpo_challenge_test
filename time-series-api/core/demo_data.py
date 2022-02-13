import json


class DemoDataFileReader:
    """
    This class reads a serialized list of data and converts them to a list of python-data-objects
    Works with json and works with (extremely) simple csv, pipe-separated
    """
    def __init__(self, file_path: str, target_class: type):
        """
        initializes a new instance of DemoDataFileReader
        :param file_path: the path where the file can be found
        :param target_class: the type the items can be deserialized
        """
        self.file_path = file_path
        self.target_class = target_class

    def _from_json(self, options: dict):
        """
        quick and dirty 'json-to-object'-deserializer
        :param options: (optional): {'new_property_name', 'old_property_name'}
        :return: a list of objects from specified type
        """
        with open(self.file_path, 'r') as file:
            data = file.read().replace('\n', '')

            j = json.loads(data)
            for obj in j:

                if options:
                    for new_key, old_key in options.items():
                        obj[new_key] = obj.pop(old_key)

                yield self.target_class(**obj)

    def _from_csv(self, options: dict):
        """
        quick and dirty 'csv-to-object'-deserializer
        :param options: (required): {'property_name', lambda[x]: x[0]}
        :return: a list of objects from specified type
        """
        if not options:
            raise Exception("please provide some options for {'property_name', lambda[x]: x[0]}")

        with open(self.file_path, 'r') as file:
            lines = file.readlines()

            for line in lines:
                if line[0].isalpha():
                    continue

                parts = line.split('|')
                target_object = self.target_class()

                for property_name, selector in options.items():
                    setattr(target_object, property_name, selector(parts))

                yield target_object

    def get_objects(self, options: dict):
        """
        deserializes the file and returns the result as a list of classes

        :param options: dependent on file-type the dictionary with options
            - for csv (required): {'property_name', lambda[x]: x[0]}
            - for json (optional): {'new_property_name', 'old_property_name'}
        :return: a list of objects from specified type
        """
        file_type = self.file_path.split('.')[-1]

        if file_type == 'json':
            return list(self._from_json(options))

        if file_type == 'csv':
            return list(self._from_csv(options))

        raise NotImplementedError('filetype .%s is not supported' % file_type)
