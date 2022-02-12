from application import db
from sqlalchemy.orm import relationship


class Signal(db.Model):
    signal_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    signal_gid = db.Column(db.String(50))
    signal_name = db.Column(db.String(200))
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.asset_id'))
    asset = relationship("Asset", back_populates="signals")
    unit = db.Column(db.String(20))
    measurements = relationship("Measurement", back_populates="signal")

    def __init__(self, signal_id=0, signal_gid=None, signal_name=None, asset_id=0, unit=None):
        self.signal_id = signal_id
        self.signal_gid = signal_gid
        self.signal_name = signal_name
        self.asset_id = asset_id
        self.unit = unit

    def __repr__(self):
        return '<Signal %i>' % self.signal_id


class Asset(db.Model):
    asset_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    latitude = db.Column(db.Float(32, 10))
    longitude = db.Column(db.Float(32, 10))
    description = db.Column(db.String(8000))
    signals = relationship("Signal", back_populates="asset")

    def __init__(self, asset_id=0, latitude=0, longitude=0, description=None):
        self.asset_id = asset_id
        self.latitude = latitude
        self.longitude = longitude
        self.description = description

    def __repr__(self):
        return '<Asset %i>' % self.asset_id


class Measurement(db.Model):
    measurement_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    signal_id = db.Column(db.Integer, db.ForeignKey('signal.signal_id'))
    signal = relationship("Signal", back_populates="measurements")
    measurement_value = db.Column(db.Float(8, 4))

    def __init__(self, timestamp=None, signal_id=0, measurement_value=0):
        self.timestamp = timestamp
        self.signal_id = signal_id
        self.measurement_value = measurement_value

    def __repr__(self):
        return '<Measurement %i>' % self.measurement_id
