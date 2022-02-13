import json

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, send_file
from signals.models import Asset, Measurement, Signal
from application import db
from sqlalchemy import func, delete
from core.demo_data import DemoDataFileReader
from signals.forms import MeasurementFilterForm, AssetForm, SignalForm, SignalGridForm
from signals.viewmodels import build_chart_data
import os
from io import BytesIO
import tempfile
from core.background_helper import background_job

signal_app = Blueprint('signal_app', __name__)


@signal_app.route('/signal_list/<asset_ids>', methods=('GET', 'POST'))
def signal_list(asset_ids: str):
    """
    returns all signals for all parametrized asset_ids is used for the multi-dropdown
    :param asset_ids: the asset-ids to be filtered for
    :return: an array of {id,name}-objects to be rendered for the dropdown-list
    """
    if not asset_ids:
        return jsonify({'signals': []})

    all_asset_ids = [int(_id) for _id in asset_ids.split(',')]

    signals = Signal.query.filter(Signal.asset_id.in_(all_asset_ids)).all()
    signal_array = [
        {
            'id': signal_.signal_id,
            'name': '%s (%s)' % (signal_.signal_name, signal_.signal_id)
        } for signal_ in signals
    ]
    return jsonify({'signals': signal_array})


@signal_app.route('/', methods=('GET', 'POST'))
def measurement_visualization():
    """
    the main functionality of this app, filtering and displaying some data
    the POST takes way too long with all this data
    :return: rendered signal/measurement_visualization.html with MeasurementFilterForm
    """
    form = MeasurementFilterForm()
    chart_data = None

    if request.method == 'POST':

        date_from = form.from_date.data
        date_to = form.to_date.data
        signal_ids = form.signal_ids.data

        query_object = Measurement.query

        if signal_ids:
            query_object = query_object.filter(Measurement.signal_id.in_(signal_ids))
        if date_from:
            query_object = query_object.filter(Measurement.timestamp >= date_from)
        if date_to:
            query_object = query_object.filter(Measurement.timestamp <= date_to)

        if request.form['action'] == 'Export':
            return export_data(query_object)

        chart_data = build_chart_data(query_object.all())

    return render_template('signals/measurement_visualization.html', form=form,  chart_data=chart_data)


def export_data(query):
    """
    export the data of a query and download it
    :param query: the query of data to export
    :return: the file containing the data
    """
    temp_dir = tempfile.TemporaryDirectory()
    file_path = os.path.join(temp_dir.name, "test.txt")
    with open(file_path, "w") as f:
        result = json.dumps([x for x in query.all()])
        f.write(result)

    return send_temp_file(file_path, temp_dir)


@signal_app.route('/asset', methods=('GET', 'POST'))
def asset():
    """
    create or update some assets
    :return: rendered signals/asset.html with AssetForm
    """
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


@signal_app.route('/signal-delete/<signal_id>', methods=['GET'])
def delete_signal(signal_id: int):
    """
    deletes a signal
    :param signal_id: the signal to be deleted
    :return: a redirect to the signal-grid
    """
    statement = delete(Signal).where(Signal.signal_id == signal_id)
    db.session.execute(statement)
    db.session.commit()
    return redirect(url_for('.signal_grid'))


def _create_or_update_signal(form: SignalForm):
    """
    creates or updates a signal
    :param form: the form of data to be created or updated
    :return: a redirect to the same form with same signal-id
    """
    existing_signal = Signal.query.get(form.signal_id.data)
    if existing_signal is None:
        if form.signal_id.data == 0:
            try:
                form.signal_id.data = db.session.query(func.max(Signal.signal_id)).first()[0] + 1
            except IndexError:
                form.signal_id.data = 1

        new_signal = Signal(signal_id=form.signal_id.data, asset_id=form.asset_id.data.asset_id)
        existing_signal = new_signal
        db.session.add(existing_signal)
        db.session.flush()

    existing_signal.signal_name = form.signal_name.data
    existing_signal.signal_gid = form.signal_gid.data
    existing_signal.asset_id = form.asset_id.data.asset_id
    existing_signal.unit = form.unit.data
    db.session.commit()

    return redirect(url_for('.signal', signal_id=existing_signal.signal_id))


@signal_app.route('/signal/<signal_id>', methods=('GET', 'POST'))
def signal(signal_id: int):
    """
    create or update a signal
    :param signal_id: the signal to be updated, or 0 to create a new one
    :return: rendered signals/signal.html with SignalForm
    """
    form = SignalForm()

    if request.method == 'POST':
        return _create_or_update_signal(form)

    existing_signal = Signal.query.get(signal_id)
    if not existing_signal:
        form.signal_id.data = signal_id
    else:
        form.signal_id.data = existing_signal.signal_id
        form.signal_gid.data = existing_signal.signal_gid
        form.signal_name.data = existing_signal.signal_name
        form.asset_id.data = existing_signal.asset
        form.unit.data = existing_signal.unit

    return render_template('signals/signal.html', form=form)


@signal_app.route('/signal-grid', methods=('GET', 'POST'))
def signal_grid():
    """
    show all signals in a grid
    :return: rendered signals/signal_grid.html with SignalGridForm
    """
    form = SignalGridForm()
    form.entries = Signal.query.all()

    return render_template('signals/signal_grid.html', form=form)


@signal_app.route('/import', methods=['GET'])
def import_data():
    """
    import data from /data-directory
    - import assets via /data/assets.json
    - import signals via /data/signals.json
    - import measurements via /data/measurements.csv
    :return: the sum of imported rows
    """
    amount = ImportFunctions.import_assets()
    amount += ImportFunctions.import_signals()
    amount += ImportFunctions.import_measurements()

    return redirect(url_for('.measurement_visualization'))


def send_temp_file(file_path: str, temp_dir: tempfile.TemporaryDirectory, remove_dir_after_send: bool = True):
    """
    send the response to download a file
    :param file_path: the filepath where the file exists
    :param temp_dir: the directory to be cleaned up
    :param remove_dir_after_send: specify whether the file shall be deleted after sending
    :return: the file-download-response
    """
    with open(file_path, "rb") as f:
        content = BytesIO(f.read())
    response = send_file(content, as_attachment=True, attachment_filename="export.json")
    if remove_dir_after_send:
        background_job(temp_dir.cleanup)
    return response


class ImportFunctions:
    """
    just a static wrapper-class for the different import-functions
    """

    @staticmethod
    def import_assets():
        """
        imports assets from data/assets.json
        :return: the number of imported objects
        """
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

    @staticmethod
    def import_signals():
        """
        imports signals from data/signals.json
        :return: the number of imported objects
        """
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

    @staticmethod
    def import_measurements():
        """
        imports measurements from data/measurements.csv
        :return: the number of imported objects
        """
        options = {
            'timestamp': lambda x: x[0],
            'signal_id': lambda x: x[1],
            'measurement_value': lambda x: float(x[2].replace(',', '.'))
        }
        objects = DemoDataFileReader("data/measurements.csv", Measurement).get_objects(options)
        db.session.bulk_save_objects(objects)
        db.session.commit()
        return len(objects)
