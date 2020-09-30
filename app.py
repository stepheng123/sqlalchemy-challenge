import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app
app = Flask(__name__)

# 3. Define static routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
	
	#create session link
	session = Session(engine)

	prcp_query = session.query(Measurement.date, Measurement.prcp).all()
	session.close()

# Create a dictionary from the data and append to a list
prcp_data = []
for date, prcp in prcp_query:
	prcp_dict = {}
	prcp_dict["date"] = date
	prcp_dict["prcp"] = prcp
	prcp_data.append(prcp_dict)
return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
	session = Session(engine)
	stations_query = session.query(Station.name,).all()
	session.close()
	names = list(np.ravel(stations_query))
	return jsonify(names)
    
@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
	max_date = session.query(func.max(Measurement.date)).first()
	max_date = [r for r in max_date]
	last_date = dt.datetime.strptime(max_date[0], '%Y-%m-%d')
	prev_year = last_date - dt.timedelta(days=365)
	tobs_q = session.query(Measurement.tobs).filter(Measurement.date >= prev_year).all()
	session.close()
	tobs = list(np.ravel(tobs_q))
	return jsonify(tobs)                 

@app.route("/api/v1.0/<start>")
def start_temp(start):
	session = Session(engine)
	temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
	temp_data=list(np.ravel(temp_data))
	session.close()
return jsonify(temp_data)

    

@app.route("/api/v1.0/<start>/<end>")
def range_temp(start, end):
	session = Session(engine)
	temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(and_(Measurement.date >= start, Measurement.date <= end)).all()
	temp_data = list(np.ravel(temp_data))
	session.close()
return jsonify(temp_data)



# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)