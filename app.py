# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, select


#Flask libraries
from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table

measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

climate_app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#this is the landing page
@climate_app.route("/")
def landing():
   """List all available api routes"""
   return (
    f"Welcome to the Climate API<br/>"
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end><br/>"
    f"dates will need to be input using the YYYY-MM-DD format"
    )

#page for precipitation
@climate_app.route("/api/v1.0/precipitation")
def prcp():
   #using the same syntax from the climate_starter file to gather prcp info
   last_year = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
   p_results = session.query(measurement.date, measurement.prcp).\
                filter(measurement.date >= last_year).all()
   #creating a dictionary to display in json format
   #we are using the dates as the keys and precip as values
   prcp_last_year = []
   for date, prcp in p_results:
      dict = {}
      dict[date] = prcp
      prcp_last_year.append(dict)
   return jsonify(prcp_last_year)

### page for stations ###
@climate_app.route("/api/v1.0/stations")
def stations():
   #querying all the info from the stations db
   s_results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
   #putting all that info into a dict and jsonifying it
   station_info = []
   for station, name, latitude, longitude, elevation in s_results:
      dict = {}
      dict["station"] = station
      dict["name"] = name
      dict["lat"] = latitude
      dict["lon"] = longitude
      dict["elevation"] = elevation
      station_info.append(dict)
   return jsonify(station_info)

### page for temperature (tobs) ###
@climate_app.route("/api/v1.0/tobs")
def temp():
   #getting data for only the last year
   last_year = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
   
   #station name taken from climate_starter
   t_results = session.query(measurement.date, measurement.tobs).\
   filter(measurement.station == 'USC00519281', measurement.date >= last_year).all()
   
   #jsonifying the results
   temps_last_year = []
   for date, tobs in t_results:
      dict = {}
      dict["date"] = date
      dict["temp"] = tobs
      temps_last_year.append(dict)
   return jsonify(temps_last_year)

### url for a specified start date ###
@climate_app.route("/api/v1.0/temp/<start_date>")
def start(start_date):
   #all date inputs will be converted to datetime format
   start_obj = dt.datetime.strptime(start_date, "%Y-%m-%d")
   
   #sel variable makes sure each part is queried individually
   sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

   #querying the min, max, and avg for dates after the one inputed
   temp_data = session.query(*sel).\
               filter(measurement.date >= start_obj).all()
   
   #storing it in a dictionary to display
   temps = {
      "min": temp_data[0][0],
      "max": temp_data[0][1],
      "average": temp_data[0][2]
}
   return jsonify(temps)

### url for a specified start and end date ###
@climate_app.route("/api/v1.0/temp/<start_date>/<end_date>")
def start_end(start_date, end_date):
   #same steps as the previous formula, but including an end date
   start_obj = dt.datetime.strptime(start_date, "%Y-%m-%d")
   end_obj =  dt.datetime.strptime(end_date, "%Y-%m-%d")
   sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
   
   #querying info from just the dates specified
   temp_data = session.query(*sel).\
               filter(measurement.date >= start_obj, measurement.date <= end_obj).all()
   temps = {
      "min": temp_data[0][0],
      "max": temp_data[0][1],
      "average": temp_data[0][2]
}
   return jsonify(temps)

if __name__ == "__main__":
    climate_app.run(debug=True)

session.close()