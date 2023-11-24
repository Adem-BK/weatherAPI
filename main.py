import requests
from flask import Flask, render_template, request
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.template_folder = 'templates'

# Clé API pour OpenWeatherMap
API_KEY = '33dc56c5cc01694d953671ddfa8f8126'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&mode={mode}'

# Fonction pour obtenir les données météorologiques
def get_weather_data(city, mode):
    try:
        # Construire l'URL pour l'API météo en utilisant les paramètres fournis
        url = WEATHER_API_URL.format(city=city, API_KEY=API_KEY, mode=mode)
        response = requests.get(url)

        # Vérifier si la requête a réussi (code de statut 200)
        if response.status_code == 200:
            if mode == 'json':
                try:
                    json_data = response.json()
                except ValueError as e:
                    print(f"Error parsing JSON: {e}")
                    return {'data': f"Error parsing JSON: {e}", 'title': 'Weather Error'}

                # Extraire des éléments spécifiques de la réponse JSON
                city = json_data.get('name', 'N/A')
                temperature = json_data.get('main', {}).get('temp', 'N/A')
                humidity = json_data.get('main', {}).get('humidity', 'N/A')
                sunrise = 'N/A'  # Not available in the JSON response
                sunset = 'N/A'   # Not available in the JSON response

            elif mode == 'xml':
                try:
                    xml_data = ET.fromstring(response.text)
                except ET.ParseError as e:
                    print(f"Error parsing XML: {e}")
                    return {'data': f"Error parsing XML: {e}", 'title': 'Weather Error'}

                # Extraire des éléments spécifiques de la réponse XML avec des vérifications pour les éléments manquants
                city_id = 'N/A'
                city_name = 'N/A'

                for element in xml_data.iter('city'):
                    city_id = element.attrib.get('id', 'N/A')
                    city_name_element = element.find('name')
                    city_name = city_name_element.text if city_name_element is not None else 'N/A'
                    break
                    # Arrêter après avoir trouvé le premier élément 'city', en supposant qu'il y en ait qu'un

                temperature_element = xml_data.find('.//temperature')
                temperature = temperature_element.attrib.get('value', 'N/A') if temperature_element is not None else 'N/A'
                humidity_element = xml_data.find('.//humidity')
                humidity = humidity_element.attrib.get('value', 'N/A') if humidity_element is not None else 'N/A'
                sunrise_element = xml_data.find('.//sun')
                sunrise = sunrise_element.attrib.get('rise', 'N/A') if sunrise_element is not None else 'N/A'
                sunset_element = xml_data.find('.//sun')
                sunset = sunset_element.attrib.get('set', 'N/A') if sunset_element is not None else 'N/A'

            return {'data': {'city': city, 'temperature': temperature, 'humidity': humidity, 'sunrise': sunrise,
                             'sunset': sunset}, 'title': f'Weather for {city}'}
        else:
            return {'data': f"Error fetching weather data: {response.status_code}", 'title': 'Weather Error'}
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return {'data': f"Error fetching weather data: {e}", 'title': 'Weather Error'}

# Page d'accueil
@app.route('/')
def index_page():
    return render_template('index.html')

# Page XML
@app.route('/xml')
def xml_page():
    return render_template('xml_template.html', result={'title': 'Page XML - Weather', 'data': 'Please enter a city.'})

# Page JSON
@app.route('/json')
def json_page():
    return render_template('json_template.html', result={'title': 'Page JSON - Weather', 'data': 'Please enter a city.'})

# Page météo
@app.route('/weather', methods=['POST', 'GET'])
def weather_page():
    if request.method == 'POST':
        city = request.form['city']
        mode = request.form['mode']
        weather_dict = get_weather_data(city, mode)
        if mode == 'xml':
            return render_template('xml_template.html', result=weather_dict)
        elif mode == 'json':
            return render_template('json_template.html', result=weather_dict)
    else:
        return render_template('xml_template.html', result={'title': 'Page XML - Weather', 'data': 'Please enter a city.'})

# Exécute l'application Flask en mode débogage
if __name__ == '__main__':
    app.run(debug=True)
