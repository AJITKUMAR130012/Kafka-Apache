import random
import pandas as pd
from bokeh.driving import count
from bokeh.models import ColumnDataSource
from kafka import KafkaConsumer
from bokeh.plotting import curdoc, figure
from bokeh.models import DatetimeTickFormatter
from bokeh.models.widgets import Div
from bokeh.layouts import column,row
import ast
import time
import pytz
from datetime import datetime
from dateutil.parser import isoparse

tz = pytz.timezone('Asia/Calcutta')


UPDATE_INTERVAL = 1000
ROLLOVER = 10 # Number of displayed data points


source = ColumnDataSource({"x": [], "y": []})
consumer = KafkaConsumer('CleanSensorData', auto_offset_reset='earliest',bootstrap_servers=['localhost:9092'], consumer_timeout_ms=1000)
div = Div(
    text='',
    width=120,
    height=35
)



@count()
def update(x):
    for msg in consumer:
        msg_value=msg
        break
    values=ast.literal_eval(msg_value.value.decode("utf-8"))
    # x=((values["TimeStamp"]["$date"])/1000.0)
    print(values)

    x_str = values["TimeStamp"]["$date"]
    try:
        # Parse ISO 8601 string to datetime and convert to desired timezone
        x = isoparse(x_str).astimezone(tz)  # Already a datetime object
    except ValueError:
        print(f"Invalid timestamp format: {x_str}")
        return  # Skip this update if the timestamp is invalid


    
    print(50*"$")
   
    print(x)
    print(50*"$")


    div.text = "TimeStamp: "+str(x)


    y = values['WaterTemperature']
    print(y)
    
    source.stream({"x": [x], "y": [y]},ROLLOVER)

p = figure(title="Water Temperature Sensor Data",x_axis_type = "datetime",plot_width=1000)
p.line("x", "y", source=source)

p.xaxis.formatter=DatetimeTickFormatter(hourmin = ['%H:%M'])
p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Value'
p.title.align = "right"
p.title.text_color = "orange"
p.title.text_font_size = "25px"

doc = curdoc()
#doc.add_root(p)

doc.add_root(
    row(children=[div,p])
)
doc.add_periodic_callback(update, UPDATE_INTERVAL)
