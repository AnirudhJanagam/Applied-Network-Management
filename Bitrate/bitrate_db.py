from influxdb import InfluxDBClient

db="aj_heartnett"

global influx

def influx(str,stream):
	s=stream.split('::')
	counter=8
	linenum=1
	client=InfluxDBClient('localhost',8086,'admin','admin',database=db)
	for line in iter(str.readline,''):
		line=line.rstrip()
		if(line == ''):
			pass
		elif(linenum > counter):		
			lines=line.split()
			t=lines[0]
			b=lines[1].split('.')
			json_body=[ 
        	      {
        	       "measurement": "bitrate",
        	       "tags": {                   
				"stream" : "{0}".format(s[1]),    
        	        },
        	       "fields": {
        	            "value": b[0],
			    "timestamp": t
        	        }
        	      }
		     ]
	
		        client.write_points(json_body)		
		linenum =linenum+1


