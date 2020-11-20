import http.client, urllib.parse, base64, json
import configparser
config = configparser.ConfigParser()
config.read('cfg.ini')

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key':'9b118dfdccee497aa3ffb617f5efdc42',
}
class my_dict(dict): 
  
    # __init__ function 
    def __init__(self): 
        self = dict() 
          
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value  
personGroupId = 'users'
def emotion_detect(image_url):
    emotion = my_dict() 
    params =urllib.parse.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes':'emotion'
        })

    body = '{"url":"%s"}'% image_url
    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        obj = json.loads(data)
        print ("FaceID: " + obj[0]['faceId'])
        anger=obj[0]['faceAttributes']['emotion']['anger']
        contempt=obj[0]['faceAttributes']['emotion']['contempt']
        disgust=obj[0]['faceAttributes']['emotion']['disgust']
        fear=obj[0]['faceAttributes']['emotion']['fear']
        happiness=obj[0]['faceAttributes']['emotion']['happiness']
        neutral=obj[0]['faceAttributes']['emotion']['neutral']
        sadness=obj[0]['faceAttributes']['emotion']['sadness']
        surprise=obj[0]['faceAttributes']['emotion']['surprise']     
        emotion.add('anger',float(anger))
        emotion.add('contempt',float(contempt))
        emotion.add('disgust',float(disgust))
        emotion.add('fear',float(fear))
        emotion.add('happiness',float(happiness))
        emotion.add('neutral',float(neutral))
        emotion.add('sadness',float(sadness))
        emotion.add('surprise',float(surprise))
        emval=max(emotion.values())
        em=''
        for key,val in emotion.items():
            if val==emval:
                em=key
        return em
    except Exception as e:
        print("Error: %s" % e)
        
def face_detect(image_url):
    params =urllib.parse.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false'
    })

    body = '{"url":"%s"}'% image_url
    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        obj = json.loads(data)
        print ("FaceID: " + obj[0]['faceId'])
        return obj[0]['faceId']
    except Exception as e:
        print("Error: %s" % e)



def create_person_group():
    params = urllib.parse.urlencode({
    'personGroupId' : 'group1' 
    })

    body = '{}'

    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("PUT", "/face/v1.0/persongroups/{personGroupId}?%s" % params,body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("Error: %s" % e)





def get_persons():

    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("GET", "/face/v1.0/persongroups/%s/persons?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        print(data)
        persons=[]
        for row in data:
            persons.append({'name':row['name'],'personId':row['personId']})
        conn.close()

        return persons
    except Exception as e:
        print (e)


def create_person(pname,udata):
    params = urllib.parse.urlencode({
        'personGroupId' : personGroupId
    })    
    body = '{"name":"%s","userData":"%s"}' % (pname,udata)
    
    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/persons?" % personGroupId, body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        conn.close()
        if not data['personId']:
            return ''
        else:    
            return data['personId']
    except Exception as e:
        print("Error: %s" % e)        



def add_person_face(personId,image_url):
    

    body = '{"url":"%s"}'% image_url
    
    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/persons/%s/persistedFaces?" %(personGroupId,personId), body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        print (data)
        conn.close()
    except Exception as e:
        print(e)    


def face_identify(faceId):
    

    #faceIds_str='['+" ".join('"'+str(x)+'",' for x in faceIds)+']'
    body = '{ "personGroupId":"%s","faceIds":["%s"]}' % (personGroupId, faceId)
    #print (body)
    try:
        print ("Face Identify in MSFace")
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify?" , body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        pid=data[0]['candidates'][0]['personId']
        print ("PID: " + pid)
        
        if not pid:
            return ''
        #print(pid)
        conn.close()
        return pid
    except Exception as e:
        print("Error: %s" % e)
        return '' 

def train():
    try:
        conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/train?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("Error: %s" % e)           



#if __name__ == '__main__':
    #add_person_face('3e6c7a54-9599-4ffb-bda2-9c47e2dde954','https://res.cloudinary.com/djdmnzbgx/image/upload/v1552826530/SmartMirror/tmp/42TrNuhVN0vcmJfVFS3j.jpg')
    #get_persons()
    #print(create_person('test',''))
    #fid=face_detect('https://res.cloudinary.com/djdmnzbgx/image/upload/v1552826530/SmartMirror/tmp/42TrNuhVN0vcmJfVFS3j.jpg')
    #fid =face_detect('https://res.cloudinary.com/djdmnzbgx/image/upload/v1550919838/SmartMirror/dataset/rkhe/fd.jpg')        
    #url='https://res.cloudinary.com/djdmnzbgx/image/upload/v1550919937/SmartMirror/dataset/radhika/fd.jpg'
    #pid='56e11b6c-9e2c-4459-8a46-cd08c72c9fbd'
    #add_person_face(pid,url)
    #face_identify(fid)
    #emotion_detect('https://res.cloudinary.com/djdmnzbgx/image/upload/v1552826530/SmartMirror/tmp/42TrNuhVN0vcmJfVFS3j.jpg')
