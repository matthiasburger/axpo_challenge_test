from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectMultipleField, DateTimeLocalField
from wtforms.validators import InputRequired, Optional
from wtforms_alchemy import QuerySelectMultipleField
from datetime import datetime

from signals.models import Asset


def assets():
    return Asset.query


class MeasurementFilterForm(FlaskForm):
    asset_ids = QuerySelectMultipleField('Assets', query_factory=assets, get_label="description",
                                         validators=[InputRequired()])
    signal_ids = SelectMultipleField('Signals', validators=[InputRequired()])
    from_date = DateTimeLocalField('From Date', format='%Y-%m-%dT%H:%M', validators=(Optional(),))
    to_date = DateTimeLocalField('To Date',default=datetime.today, format='%Y-%m-%dT%H:%M', validators=(Optional(),))
    last_filtered = StringField("filtered last")


class AssetForm(FlaskForm):
    description = StringField('Description', [InputRequired()])
    latitude = FloatField('Latitude', [InputRequired()])
    longitude = FloatField('Longitude', [InputRequired()])
    asset_id = IntegerField("Asset-Id", [InputRequired()])
