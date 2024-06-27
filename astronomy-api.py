import requests
import json
import os
import base64

applicationId=os.getenv('CLIENT_ID')
applicationSecret=('CLIENT_SECRET')

url ='https://api.astronomyapi.com/api/v2/bodies/positions' 

userpass = str(applicationId) + ":" + str(applicationSecret) 
#"applicationId:applicationSecret"
authString = base64.b64encode(userpass.encode()).decode()

#latitudeResponse=
#longitudeResponse=
#elevationResponse=
#fromDateResponse=
#toDateResponse=
#timeResponse=


response = requests.get(url, {
                        'latitude':38.775867,
                        'longitude':-84.39733,
                        'elevation':1,
                        'from_date':"2020-12-20T09:00:00.000-05:00",
                        'to_date':"2020-12-23T09:00:00.000-05:00",
                        'time':"2020-12-23T09:00:00.000-05:00",
                            })

print(response)
