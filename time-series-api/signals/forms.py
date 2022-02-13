from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectMultipleField, DateTimeLocalField, FieldList, FormField
from wtforms.validators import InputRequired, Optional
from wtforms_alchemy import QuerySelectMultipleField, QuerySelectField
from datetime import datetime

from signals.models import Asset


def assets():
    """
    queries for all assets
    :return: a query-object providing the assets
    """
    return Asset.query


class MeasurementFilterForm(FlaskForm):
    """ form for filtering the measurements """
    asset_ids = QuerySelectMultipleField('Assets', query_factory=assets, get_label="description",
                                         validators=[InputRequired()])
    signal_ids = SelectMultipleField('Signals', validators=[InputRequired()])
    from_date = DateTimeLocalField('From Date', format='%Y-%m-%dT%H:%M', validators=(Optional(),))
    to_date = DateTimeLocalField('To Date', default=datetime.today, format='%Y-%m-%dT%H:%M', validators=(Optional(),))


class AssetForm(FlaskForm):
    """ form for creating/editing assets """

    description = StringField('Description', [InputRequired()])
    latitude = FloatField('Latitude', [InputRequired()])
    longitude = FloatField('Longitude', [InputRequired()])
    asset_id = IntegerField("Asset-ID", [InputRequired()])


class SignalForm(FlaskForm):
    """ form for creating/editing signals """

    signal_id = IntegerField('Signal-ID', [InputRequired()])
    signal_name = StringField('Name', [InputRequired()])
    signal_gid = StringField('GID', [InputRequired()])
    unit = StringField('Unit', [InputRequired()])
    asset_id = QuerySelectField("Asset",  query_factory=assets, get_label="description", validators=[InputRequired()])


class SignalGridForm(FlaskForm):
    """ form for displaying the grid of all signals """
    entries = FieldList(FormField(SignalForm))
