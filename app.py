from flask import Flask, render_template, request, Response
import pandas as pd
import requests
from io import StringIO
from geopy.geocoders import Nominatim
from geotext import GeoText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hola'
geolocator = Nominatim(user_agent="example app")

tweets = []
locations = []
csv_contents = []
applied = []
source_applied = []
count = 0
number_images= 100
confidence= 0.9
alert = ""
source_applied = {'ID': "", 'source': "", 'keywords': ""}

@app.route('/', methods=['GET','POST'])
def index():
    global count, applied, source_applied, number_images, tweets, csv_contents, confidence, alert, locations
    if request.method == "POST": 
        if 'source_button' in request.form:  
            if count == 0:
                option = request.form['source']
                keywords = request.form['keywords']
                number_images = request.form['number_pic']
                r = requests.post('http://131.175.120.2:7777/Crawler/API/CrawlCSV',
                                  json={'query': keywords,
                                        'count': number_images})   
                if len(r.text) != 1:                    
                    source_applied = {'ID': count, 'source': option, 'keywords': keywords}
                    print(source_applied)
                    f = {'ID': "", 'Filter': "", 'Attribute': "", 'Confidence': 0.9}
                    applied.append(f)
                    tmp= StringIO(r.text)
                    df= pd.read_csv(tmp)
                    df['user_country'] = ""
                    u = []
                    for x in range(len(df)):
                        user_loc = df['user_loc'].iloc[x]
                        if pd.isna(user_loc) == False:
                            geolocated_text = geolocator.geocode(user_loc, timeout= 10)
                            if geolocated_text == None:
                                full_location_list = GeoText(user_loc).cities + GeoText(user_loc).countries
                                full_location = ''.join(str(e) for e in full_location_list)
                                geolocated_full_location = geolocator.geocode(full_location, timeout= 10)
                                if geolocated_full_location == None:
                                    df['user_country'].iloc[x] = 'Not defined'
                                else:
                                    df['user_country'].iloc[x] = geolocated_full_location.address.split(', ')[-1]
                            else:
                                df['user_country'].iloc[x] = geolocated_text.address.split(', ')[-1]
                        else:
                            df['user_country'].iloc[x] = 'Not defined'
                            
                        p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                        u.append(p)
                    tweets.append(u)
                    df_sorted = df.sort_values(by=['user_country'], ascending = True)
                    locations.append(df_sorted['user_country'].astype(str).unique())
                    csv_string = df.to_csv(encoding= "utf-8")
                    csv_contents.append(csv_string)
                    count+=1
                    alert = ""
                else:
                    alert = "Your search query did not return any images. Please try to either shorten the query or make use of the OR keyword to make some of the terms optional"
                
            else:
                option = request.form['source']
                keywords = request.form['keywords']
                number_images = request.form['number_pic']                
                r = requests.post('http://131.175.120.2:7777/Crawler/API/CrawlCSV',
                                  json={'query': keywords,
                                        'count': number_images})
                if len(r.text) != 1:
                    source_applied = {'ID': 0, 'source': option, 'keywords': keywords}
                    print(source_applied)
                    tmp= StringIO(r.text)
                    df= pd.read_csv(tmp)
                    df['user_country'] = ""
                    u = []
                    for x in range(len(df)):
                        user_loc = df['user_loc'].iloc[x]
                        if pd.isna(user_loc) == False:
                            geolocated_text = geolocator.geocode(user_loc, timeout= 10)
                            if geolocated_text == None:
                                full_location_list = GeoText(user_loc).cities + GeoText(user_loc).countries
                                full_location = ''.join(str(e) for e in full_location_list)
                                geolocated_full_location = geolocator.geocode(full_location, timeout= 10)
                                if geolocated_full_location == None:
                                    df['user_country'].iloc[x] = 'Not defined'
                                else:
                                    df['user_country'].iloc[x] = geolocated_full_location.address.split(', ')[-1]
                            else:
                                df['user_country'].iloc[x] = geolocated_text.address.split(', ')[-1]
                        else:
                            df['user_country'].iloc[x] = 'Not defined'
                            
                        p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                        u.append(p)
                    tweets[0]= u  
                    df_sorted = df.sort_values(by=['user_country'], ascending = True)
                    locations[0] = df_sorted['user_country'].astype(str).unique()
                    csv_string = df.to_csv(encoding= "utf-8")
                    csv_contents[0]= csv_string
                    alert = ""
                else:
                    alert = "Your search query did not return any images. Please try to either shorten the query or make use of the OR keyword to make some of the terms optional"
                    
        elif 'apply_button' in request.form:
            if int(request.form['apply_button']) == count:
                if request.form['Filter_select'] != "User location":
                    Filter = request.form['Filter_select']
                    if request.form['Filter_select'] == "Remove memes":
                        attribute = "MemeDetector"
                    elif request.form['Filter_select'] == "Scene detector":
                        attribute = request.form['option1_select']
                    elif request.form['Filter_select'] == "Contains object":
                        attribute = request.form['option2_select']
                    confidence = request.form['confidence']
                    
                    params = {'filter_name_list': [attribute],
                              'confidence_threshold_list': [request.form['confidence']],
                              'column_name': 'media_url',
                              'csv_file': csv_contents[count-1]
                              }
                    r = requests.post(url='http://131.175.120.2:7777/Filter/API/FilterCSV', json=params)
                    
                    if len(r.text) > 160:
                        f = {'ID': count, 'Filter': Filter, 'Attribute': attribute, 'Confidence': confidence}
                        k = {'ID': "", 'Filter': "", 'Attribute': "", 'Confidence': 0.9}
                        applied[count-1] = f
                        applied.append(k)
                        print(applied)
                        csv_contents.append(r.text)
                        tmp= StringIO(r.text)
                        df= pd.read_csv(tmp)
                        df_sorted = df.sort_values(by=['user_country'], ascending = True)
                        locations.append(df_sorted['user_country'].astype(str).unique())
                        u = []
                        for x in range(len(df)):
                            p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                            u.append(p)
                        tweets.append(u)                    
                        count+=1
                        alert = ""
                    else:
                        alert = "After running the above filter, no images remain. Either increase the number of images or change the filter."
                        
                elif request.form['Filter_select'] == "User location":
                    Filter = "User location"
                    attribute = request.form['option3_select']
                    f = {'ID': count, 'Filter': Filter, 'Attribute': attribute, 'Confidence': confidence}
                    k = {'ID': "", 'Filter': "", 'Attribute': "", 'Confidence': 0.9}
                    applied[count-1] = f
                    applied.append(k)
                    print(applied)                    
                    tmp = StringIO(csv_contents[count-1])
                    df0 = pd.read_csv(tmp)
                    df = df0.loc[df0['user_country'] == attribute]
                    df_sorted = df.sort_values(by=['user_country'], ascending = True)
                    locations.append(df_sorted['user_country'].astype(str).unique())
                    u = []
                    for x in range(len(df)):
                        p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                        u.append(p)
                    tweets.append(u)                     
                    csv_string = df.to_csv(encoding= "utf-8")
                    csv_contents.append(csv_string)
                    count+=1
                    alert = ""
                
            else:
                sel_count = int(request.form['apply_button'])
                if request.form['Filter_select'] != "User location":
                    Filter = request.form['Filter_select']
                    if request.form['Filter_select'] == "Remove memes":
                        attribute = "MemeDetector"
                    elif request.form['Filter_select'] == "Scene detector":
                        attribute = request.form['option1_select']
                    elif request.form['Filter_select'] == "Contains object":
                        attribute = request.form['option2_select']

                    confidence = request.form['confidence']

                    params = {'filter_name_list': [attribute],
                              'confidence_threshold_list': [request.form['confidence']],
                              'column_name': 'media_url',
                              'csv_file': csv_contents[sel_count-1]
                              }                        
                    r = requests.post(url='http://131.175.120.2:7777/Filter/API/FilterCSV', json=params)
                    
                    if len(r.text) > 160:
                        f = {'ID': sel_count, 'Filter': Filter, 'Attribute': attribute, 'Confidence': confidence}
                        applied[sel_count-1] = f
                        print(applied)
                        csv_contents[sel_count] = r.text
                        tmp= StringIO(r.text)
                        df= pd.read_csv(tmp)
                        df_sorted = df.sort_values(by=['user_country'], ascending = True)
                        locations[sel_count]= df_sorted['user_country'].astype(str).unique()
                        u = []
                        for x in range(len(df)):
                            p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                            u.append(p)
                        tweets[sel_count]= u 
                        alert = ""
                    else:
                        alert = "After running the above filter, no images remain. Either increase the number of images or change the filter."
                
                elif request.form['Filter_select'] == "User location":
                    Filter = "User location"
                    attribute = request.form['option3_select']
                    f = {'ID': sel_count, 'Filter': Filter, 'Attribute': attribute, 'Confidence': confidence}
                    applied[sel_count-1] = f
                    print(applied)                    
                    tmp = StringIO(csv_contents[sel_count-1])
                    df0 = pd.read_csv(tmp)
                    df = df0.loc[df0['user_country'] == attribute]
                    df_sorted = df.sort_values(by=['user_country'], ascending = True)
                    locations[sel_count]= df_sorted['user_country'].astype(str).unique()
                    u = []
                    for x in range(len(df)):
                        p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                        u.append(p)
                    tweets[sel_count]= u                     
                    csv_string = df.to_csv(encoding= "utf-8")
                    csv_contents[sel_count]= csv_string
                    alert = ""

        elif 'reset_button' in request.form:
            count = 0
            source_applied = {'ID': "", 'source': "", 'keywords': ""}
            applied = []
            tweets = []
            csv_contents = []
            locations = []
            alert = ""
            
        elif 'up_button' in request.form:
            sel_count = int(request.form['up_button'])
            a = applied[sel_count-2]
            applied[sel_count-2] = applied[sel_count-1]
            applied[sel_count-1] = a
            
            for a in range(count-sel_count+1):
                if applied[sel_count-2+a]['Filter'] != "User location":
                    params = {'filter_name_list': [applied[sel_count-2+a]['Attribute']],
                              'confidence_threshold_list': [applied[sel_count-2+a]['Confidence']],
                              'column_name': 'media_url',
                              'csv_file': csv_contents[sel_count-2+a]
                              }
                    r = requests.post(url='http://131.175.120.2:7777/Filter/API/FilterCSV', json=params)
                    
                    if len(r.text) > 160:
                        print(applied)
                        csv_contents[sel_count-1+a] = r.text
                        tmp= StringIO(r.text)
                        df= pd.read_csv(tmp)
                        df_sorted = df.sort_values(by=['user_country'], ascending = True)
                        locations[sel_count-1+a]= df_sorted['user_country'].astype(str).unique()                        
                        u = []
                        for x in range(len(df)):
                            p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                            u.append(p)
                        tweets[sel_count-1+a]= u
                        alert = ""
                        
                    else:
                        alert = "After running the above filter, no images remain. Either increase the number of images or change the filter."
                        break
                else:
                    tmp = StringIO(csv_contents[sel_count-2+a])
                    df0 = pd.read_csv(tmp)
                    df = df0.loc[df0['user_country'] == applied[sel_count-2+a]['Attribute']]
                    csv_string = df.to_csv(encoding= "utf-8")
                    
                    if len(csv_string) > 160:
                        print(applied)
                        df_sorted = df.sort_values(by=['user_country'], ascending = True)
                        locations[sel_count-1+a]= df_sorted['user_country'].astype(str).unique()
                        u = []
                        for x in range(len(df)):
                            p = {"url": df['media_url'].iloc[x], "text": df['full_text'].iloc[x], "user_country": df['user_country'].iloc[x]}
                            u.append(p)
                        tweets[sel_count-1+a]= u                     
                        csv_contents[sel_count-1+a]= csv_string
                        alert = ""
                    else:
                        alert = "After running the above filter, no images remain. Either increase the number of images or change the filter."
                        break

    return render_template('index.html', count=count, source_applied=source_applied, tweets=tweets,
                           applied=applied, alert=alert, locations=locations,
                           number_images=number_images, confidence=confidence)

@app.route("/downloadCSV")
def downloadCSV():
    return Response(
        csv_contents[int(request.args.get('id'))],
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=download.csv"})

if __name__ == '__main__':
    app.run(debug=True)

