def build_chart_data(measurements: list):
    """
    creates the chart-data for the measurements-list
    :param measurements: all measurements that should be displayed in the chart
    :return: a new object from type LineChartDataSet containing the data_rows
    """
    data_rows = {}
    for measurement in measurements:
        if measurement.signal_id not in data_rows:
            data_rows[measurement.signal_id] = []

        data_rows[measurement.signal_id].append({'x': measurement.timestamp, 'y': measurement.measurement_value})
    return LineChartDataSet(data_rows)


class LineChartDataSet:
    """ wrapper for the chart-data """
    def __init__(self, data_rows: dict):
        """
        initializes a new object from type LineChartDataSet
        :param data_rows: the actual data-rows the chart shall show
        """
        self.data_rows = data_rows
