''''
import requests
import json
import os
import base64

applicationId=os.getenv('CLIENT_ID')
applicationSecret=os.getenv('CLIENT_SECRET')

url ='https://api.astronomyapi.com/api/v2/bodies/positions' 

# added login directly and it worked
# needs testing as environmental var
userpass = ""
authString = base64.b64encode(userpass.encode()).decode()
auth = "Basic " + authString
header = {'Authorization': auth}

#latitudeResponse=
#longitudeResponse=
#elevationResponse=
#fromDateResponse=
#toDateResponse=
#timeResponse=


response = requests.get(url,  
                        {'latitude':38.775867,
                        'longitude':-84.39733,
                        'elevation':1,
                        'from_date':"2020-12-20",
                        'to_date':"2020-12-23",
                        'time':"09:00:00"
                        },
                        headers = header,
                        )

print(response.json().keys())
''''