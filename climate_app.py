import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Assign the station  class to a variable called `Station`
Station = Base.classes.station
# Assign the measurement  class to a variable called `Measurement`
Measurement= Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes below:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[satrt_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[satrt_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
        f" Please put dates in 'YYYY-MM-DD' format <br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ the most recent date in the data set"""
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    #Using this date, retrieve the last 12 months of precipitation data by querying the 12 preceding months of data.
    begin_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    query_results = session.query(Measurement.prcp,Measurement.date ).\
    filter(Measurement.date >=begin_date).\
    filter(Measurement.date <=recent_date).all()
    print('xyx')
    print(begin_date)
    session.close()
    # Create a dictionary from the row data and append to a list of all precipitation 
    all_precipitation = []
    for row in query_results:
       precipitation_dict = {}
       precipitation_dict["Precipitation"] = row.prcp
       precipitation_dict["Date"] = row.date
       all_precipitation.append(precipitation_dict)
 
    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """ Return a JSON list of stations from the dataset.."""

    query_results_station = session.query(Station.station).\
        order_by (Station.station).all()
    
    return jsonify(query_results_station)

#query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    query_results = session.query(Measurement.tobs,Measurement.date ).\
    filter(Measurement.date >=last_year_date).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date <=recent_date).\
         order_by(Measurement.date).all()
    
    session.close()
    # Create a dictionary from the row data and append to a list of all precipitation 
    all_tobs = []
    for row in query_results:
       tobs_dict = {}
       tobs_dict["tobs"] = row.tobs
       tobs_dict["Date"] = row.date
       all_tobs.append(tobs_dict)
 
    return jsonify(all_tobs)
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
# for a given start or start-end range.
@app.route("/api/v1.0/<start_date>")
def temp_start_date(start_date):
    session = Session(engine)
    min_max_avg_temp=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
    func.avg(Measurement.tobs))\
    .filter(Measurement.date >= start_date).all()
    session.close()
    all_tobs_data_user = []
    for row in min_max_avg_temp:
       tobs_temp_dict = {}
       tobs_temp_dict["min_tobs"] = row[0]
       tobs_temp_dict["max_tobs"] = row[1]
       tobs_temp_dict["avg_tobs"] = row[2]
       all_tobs_data_user.append(tobs_temp_dict)

       
    return jsonify(all_tobs_data_user)

@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_start_end_date(start_date,end_date):
    session = Session(engine)
    min_max_avg_temp=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),\
    func.avg(Measurement.tobs))\
    .filter(Measurement.date >= start_date)\
    .filter(Measurement.date <= end_date).all()
    session.close()
    all_tobs_data_user_date_range = []
    for row in min_max_avg_temp:
       tobs_temp_date_range_dict = {}
       tobs_temp_date_range_dict["min_tobs"] = row[0]
       tobs_temp_date_range_dict["max_tobs"] = row[1]
       tobs_temp_date_range_dict["avg_tobs"] = row[2]
       all_tobs_data_user_date_range.append(tobs_temp_date_range_dict)

    return jsonify(all_tobs_data_user_date_range)

if __name__ == '__main__':
    app.run(debug=True)
