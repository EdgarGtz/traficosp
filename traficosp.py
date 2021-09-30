# Importamos librerías

from urllib.request import urlopen
import json
import pandas as pd


# Guardamos el URL del archivo tipo json para trabajar con él como un diccionario

url = "https://www.waze.com/row-rtserver/broadcast/BroadcastRSS?format=JSON&buid=1397c15e3dfa4f4f7d815e17dd893f4d"
response = urlopen(url)
data = json.loads(response.read())


# Guardamos la llave 'routes' en un DataFrame

routes = pd.DataFrame.from_dict(data['routes'])

# Removemos las columnas que no nos interesan
routes = routes.drop(['toName', 'line', 'bbox', 'fromName',
                      'jamLevel', 'id', 'type', 'jams'],
                     axis = 1)


## Creamos un dummy DataFrame para crear nuestra base de datos

travel_time_ar = pd.DataFrame()

# Creamos una columna con los nombres de cada ruta
travel_time_ar['ruta'] = routes['name']

# Creamos una columna con la distancia de cada ruta (en metros)
travel_time_ar['distancia'] = routes['length']

# Creamos una columna con el tiempo de traslado (en segundos)
travel_time_ar['travel_time'] = routes['time']

# Creamos una columna con el tiempo histórico de traslado (en segundos)
travel_time_ar['historic_time'] = routes['historicTime']

## Trabajo con Fechas

# A nuestra base de datos le añadimos 
# una columna con el timestamp actual
travel_time_ar['fecha'] = pd.Timestamp.now()

# Creaamos una columna que redondea la hora
# del timestamp al minuto más cercano
travel_time_ar['hora'] = travel_time_ar['fecha'].dt.floor('T')

# A la columna 'hora' le dejamos 
# tan solo la hora del timestamp
travel_time_ar['hora'] = travel_time_ar['hora'].dt.time

# A la columna 'fecha' le dejamos
# tan solo la fecha actual
travel_time_ar['fecha'] = travel_time_ar['fecha'].dt.date


# Reordenamos las columnas de nuestro DataFrame
# para comenzar con la fecha y hora del reporte
reorder = ['fecha', 'hora', 'ruta',
           'distancia', 'travel_time', 'historic_time']

travel_time_ar = travel_time_ar.reindex(columns = reorder)

# Transformamos la distancia de las rutas a kilómetros
travel_time_ar['distancia'] = (travel_time_ar['distancia'] / 1000).round(decimals = 1)


# Agregamos los datos nuevos a la base de datos

# Cargamos el archivo de la base
base_completa = pd.read_excel(r"travel_time_ar.xlsx")

# Python lee la columna de fecha como timestamp
# La transformamos para que sea tan solo la fecha
base_completa['fecha'] = base_completa['fecha'].dt.date

# Concatenamos los datos nuevos a la base completa
base_completa = pd.concat([base_completa, travel_time_ar])

# Guardamos el archivo de excel actualizado de la base completa
writer_completa = pd.ExcelWriter(r"travel_time_ar.xlsx",
                                 engine = "xlsxwriter")

base_completa.to_excel(writer_completa, index = False)

writer_completa.save()








