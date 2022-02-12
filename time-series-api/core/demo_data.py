import json


class DemoDataFileReader:
    """
        This class reads a serialized list of data and converts them to a list of python-data-objects
        Works with json and works with (extremely) simple csv, pipe-separated
    """
    def __init__(self, file_path, target_class):
        self.file_path = str(file_path)
        self.target_class = target_class

    def _from_json(self, options):
        """
            quick and dirty 'json-to-object'-deserializer
        """
        with open(self.file_path, 'r') as file:
            data = file.read().replace('\n', '')

            j = json.loads(data)
            for obj in j:

                if options:
                    for new_key, old_key in options.items():
                        obj[new_key] = obj.pop(old_key)

                yield self.target_class(**obj)

    def _from_csv(self, options):
        """
            quick and dirty 'csv-to-object'-deserializer
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

    def get_objects(self, options):
        """
            deserializes the file and returns the result as a list of classes
        """
        file_type = self.file_path.split('.')[-1]

        if file_type == 'json':
            return list(self._from_json(options))

        if file_type == 'csv':
            return list(self._from_csv(options))

        raise NotImplementedError('filetype .%s is not supported' % file_type)
