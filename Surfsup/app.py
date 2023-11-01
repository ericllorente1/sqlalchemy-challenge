# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")



# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each tables

measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    year_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date>='2016-08-23', measurement.date<='2017-08-23')
    session.close()
    #create an empty list that will be appended with dictionaries and returned to user
    prcp_data = []
    #create a for loop to extract data from query 
    for date, prcp in year_data:
         #create an empty dictionary for each date/row/iteration
         prcp_dict = {}
         #append date 
         prcp_dict['Date'] = date
         #append precipitation
         prcp_dict['Precipitation'] = prcp
         #add dictionary to empty list 
         prcp_data.append(prcp_dict)
    #return a json response with list of query data
    return jsonify(prcp_data)
         
@app.route("/api/v1.0/stations")
def stations():
    #return a JSON list of stations from the dataset.
    stations = session.query(station.station)
    session.close()
    stations_list = [station for station in stations]
    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    #find most active station
    station_activity = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station = station_activity[0][0]
    most_active_station
    #using most active station id query dates and temperature for previous year of data.
    year_temperature = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == most_active_station).\
    filter(measurement.date>='2016-08-23', measurement.date<='2017-08-23').all()
    session.close()
    #create list that will be returned in json
    year_tobs = []
    #create a loop to create a dictionary for each date and temp
    for date, tobs in year_temperature:
        tobs_dict = {}
        tobs_dict['Date']= date
        tobs_dict['Temperature'] = tobs
        year_tobs.append(tobs_dict)
    
    return jsonify(year_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()    
    temp_aggs = []
    for tmin, tavg, tmax in query:
        tobs_dict = {}
        tobs_dict['tmin'] = tmin
        tobs_dict['tavg'] = tavg
        tobs_dict['tmax'] = tmax
        temp_aggs.append(tobs_dict)
    return jsonify(temp_aggs)

@app.route("/api/v1.0/<start>/<stop>")
def start_stop(start, stop):
    temp_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()    
        
    temps = []
    for tmin, tavg, tmax in temp_query:
        tobs_dict = {}
        tobs_dict['tmin'] = tmin
        tobs_dict['tavg'] = tavg
        tobs_dict['tmax'] = tmax
        temps.append(tobs_dict)
    return jsonify(temps)
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5002)