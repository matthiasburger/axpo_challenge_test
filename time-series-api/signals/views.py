import json

from flask import Blueprint, jsonify, request, render_template, make_response

from signals.models import Asset, Measurement, Signal
from application import db
from core.demo_data import DemoDataFileReader
from signals.forms import MeasurementFilterForm, AssetForm

signal_app = Blueprint('signal_app', __name__)


@signal_app.route('/signal_list/<asset_ids>', methods=('GET', 'POST'))
def signal_list(asset_ids):
    if not asset_ids:
        return jsonify({'signals': []})

    all_asset_ids = [int(_id) for _id in str(asset_ids).split(',')]

    signals = Signal.query.filter(Signal.asset_id.in_(all_asset_ids)).all()
    signal_array = [
        {
            'id': signal.signal_id,
            'name': signal.signal_name
        } for signal in signals
    ]
    return jsonify({'signals': signal_array})

def _get_signals_by_asset_id(asset_ids):
    all_asset_ids = [int(_id) for _id in str(asset_ids).split(',')]

    return Signal.query.filter(Signal.asset_id.in_(all_asset_ids)).all()


class LineChartDataSet:
    def __init__(self, data_rows):
        self.data_rows = data_rows


class LineChartDataRow:
    def __init__(self, signal_id, measurements):
        self.signal_id = signal_id
        self.measurements = measurements

    def get_chart_data(self):
        return [{'x': measurement.timestamp, 'y':measurement.measurement_value} for measurement in self.measurements]


def build_chart_data(measurements):
    data_rows = {}
    for measurement in measurements:
        if measurement.signal_id not in data_rows:
            data_rows[measurement.signal_id] = []

        data_rows[measurement.signal_id].append({'x': measurement.timestamp, 'y':measurement.measurement_value})
    return LineChartDataSet(data_rows)

@signal_app.route('/measurement_visualization', methods=('GET', 'POST'))
def measurement_visualization():
    form = MeasurementFilterForm()

    if request.method == 'POST':
        date_from = form.from_date.data
        date_to = form.to_date.data
        asset_id = form.asset_ids.data
        signal_ids = form.signal_ids.data

        query_object = Measurement.query
        print(form.asset_ids.data)
        print(form.signal_ids.data)
        print(form.from_date.data)
        print(form.to_date.data)
        print (date_from)
        print (date_to)

        if signal_ids:
            query_object = query_object.filter(Measurement.signal_id.in_(signal_ids))
        if date_from:
            query_object = query_object.filter(Measurement.timestamp >= date_from)
        if date_to:
            query_object = query_object.filter(Measurement.timestamp <= date_to)

        chart_data = build_chart_data(query_object.all())

        form.last_filtered.data = 'bla'

        return render_template('signals/measurement_visualization.html', form=form, chart_data=chart_data)
    return render_template('signals/measurement_visualization.html', form=form,  chart_data=None)


@signal_app.route('/asset', methods=('GET', 'POST'))
def asset():
    form = AssetForm()

    if form.validate_on_submit():
        existing_asset = Asset.query.get(form.asset_id.data)
        if existing_asset is None:
            new_asset = Asset(asset_id=form.asset_id.data)
            existing_asset = new_asset
            db.session.add(existing_asset)
            db.session.flush()

        existing_asset.longitude = form.longitude.data
        existing_asset.latitude = form.latitude.data
        existing_asset.description = form.description.data
        db.session.commit()


    return render_template('signals/asset.html', form=form)



@signal_app.route('/import', methods=['POST'])
def import_data():
    """
        import data from /data-directory

        import assets via /data/assets.json
        import signals via /data/signals.json
        import measurements via /data/measurements.csv
    """
    amount = import_assets()
    amount += import_signals()
    amount += import_measurements()

    return jsonify({'imported': amount})


def import_assets():
    assets_key_replacement = {
        'asset_id': 'AssetID',
        'latitude': 'Latitude',
        'longitude': 'Longitude',
        'description': 'descri',
    }

    objects = DemoDataFileReader("data/assets.json", Asset).get_objects(assets_key_replacement)
    db.session.bulk_save_objects(objects)
    db.session.commit()
    return len(objects)


def import_signals():
    signals_key_replacement = {
        'signal_gid': 'SignalGId',
        'signal_id': 'SignalId',
        'signal_name': 'SignalName',
        'asset_id': 'AssetId',
        'unit': 'Unit'
    }

    objects = DemoDataFileReader("data/signal.json", Signal).get_objects(signals_key_replacement)
    db.session.bulk_save_objects(objects)
    db.session.commit()
    return len(objects)


def import_measurements():
    options = {
        'timestamp': lambda x: x[0],
        'signal_id': lambda x: x[1],
        'measurement_value': lambda x: float(x[2].replace(',', '.'))
    }
    objects = DemoDataFileReader("data/measurements.csv", Measurement).get_objects(options)
    db.session.bulk_save_objects(objects)
    db.session.commit()
    return len(objects)
