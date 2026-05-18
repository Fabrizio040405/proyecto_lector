import json
import os
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
from tabulate import tabulate

class Lector(object):
    """
    Docstring of Lector:
    -------------------------
    Clase Lector para leer archivos JSON y Database. Esta clase
    Tiene dos funciones con las cuales se puede instanciar un objeto "Lector".

    1. from_json: Lee un archivo JSON desde una ruta especificada.

    2. from_db: Lee una tabla desde una base de datos especificada por las credenciales de conexión.

    Además, la función "conectar_db" es un método estático que se encarga 
    de establecer la conexión con la base de datos utilizando las credenciales proporcionadas.

    """
    def __init__(self, ruta : str | psycopg2.extensions.connection = None, **kwargs):
        """
        Docstring of Constructor:
        -------------------------
        Inicializa un objeto de la clase Lector.
        Parámetros:
        - ruta: Puede ser una cadena de texto que representa la ruta de un archivo JSON o una conexión a una base de datos.

        - kwargs: Un diccionario de argumentos adicionales que pueden incluir: 

            - forma: Especifica la forma de lectura, ya sea '.json' o 'db'.

            - table: Especifica el nombre de la tabla a leer en caso de ser una conexión a una base de datos.
        """
        self.ruta = ruta
        self.forma = kwargs['forma'] 
        self.table = kwargs['table'] 

    @staticmethod
    def conectar_db(**kwargs):
        """
        Docstring of conectar_db:
        -------------------------
        Conecta a la base de datos con las credenciales especificadas.
        Retorna una conexión a la base de datos.
        """
        try: 

            connection = psycopg2.connect(
                host = kwargs["host"],
                database = kwargs["database"],
                user = kwargs["user"],
                password = kwargs["password"],
                port = kwargs["port"],
                sslmode = 'require', # Obligatorio para Neon
            )

            return connection
        
        except Exception as e:

            raise Exception(f'Error al conectar a la base de datos: {e}')
        
    @staticmethod
    def crear_tabla(df : pd.DataFrame, formato : str = 'tabule', showindex : bool = True) -> str:
        """
        Docstring of crear_tabla:
        -------------------------
        Crea una tabla en la base de datos a partir de un DataFrame de Pandas.
        
        Opciones de uso:

        - formatos:

            > flet: Crea una tabla utilizando la biblioteca Flet.
            > tabule: Crea una tabla utilizando la biblioteca tabule.    
        """
        if formato == 'flet':
            pass
        elif formato == 'tabule':
            tabla = tabulate(df, headers='keys', tablefmt='rounded_outline', showindex=showindex)
            return tabla
        else:
            raise Exception('No se ha especificado un formato de tabla válido')
    
    @classmethod
    def from_db(cls, **kwargs):
        """
        DocString of from_db:
        -------------------------
        Valida la existencia del archivo desde una Database.
        Forma correcta de llamar a la función:

        Lector.from_db(host='host', database='database', user='user', password='password', port='port', table='table')

        retorna una conexión a la base de datos.
        """
        
        try: 

            connection = cls.conectar_db(**kwargs)

            config = {
                'forma' : 'db',
                'table' : kwargs["table"]
            }

            return cls(connection, **config)
        
        except Exception as e:

            raise Exception(f'Error al conectar a la base de datos: {e}')

    @classmethod
    def from_json(cls, ruta : str = None):
        """
        DocString of from_json:
        -------------------------
        Valida la existencia del 
        archivo en la ruta especificada.
        """
        if not ruta:
            raise Exception('Debe Poner una ruta')
        elif not os.path.exists(ruta):
            raise Exception('Ruta no existe')
        elif not os.path.isfile(ruta):
            raise Exception('Debe ser un archivo no un directorio')
        elif not ruta.endswith('.json'):
            raise TypeError('Debe ser un archivo .json')

        return cls(ruta, forma = '.json', table = None)

    def get_data(self):
        """
        DocString of get_data:
        -------------------------
        Obtiene los datos del objeto Lector.
        además, dependiendo de la forma de lectura especificada, ya sea '.json' o 'db', se realiza la lectura 
        correspondiente y se retorna los datos obtenidos.

        Este método retorna los datos obtenidos en formato string.
        """
        if self.forma == '.json':
            with open(self.ruta,'r') as f:
                data = json.load(f)
            return data
        
        elif self.forma == 'db':
            cursor = self.ruta.cursor()
            cursor.execute(f"SELECT * FROM {self.table}")  # Reemplaza 'tu_tabla' con el nombre de tu tabla
            data = cursor.fetchall()
            columnas = [i[0] for i in cursor.description]  # Obtener los nombres de las columnas
            cursor.close()
            return columnas, data
        
        else:
            raise Exception('No se ha especificado una forma de lectura')
        
    def to_Dataframe(self) -> pd.DataFrame:
        """
        DocString of to_Dataframe:
        -------------------------
        Convierte los datos en un DataFrame de Pandas.

        Retorna un DataFrame con los datos proporcionados.
        """
        data = self.get_data() # Obtencion de la data

        if self.forma == '.json':
            df = pd.DataFrame(data)
        elif self.forma == 'db':
            df = pd.DataFrame(data[1], columns=data[0])
        else:
            raise Exception('No se ha especificado una forma de lectura')

        return df
    
    def to_image(self, **kwargs) -> plt.table:
        """
        Docstring of to_image:
        -------------------------
        Crea una tabla a partir de un DataFrame de Pandas.
        Parámetros:
        - df: Un DataFrame de Pandas que contiene los datos a insertar en la tabla.
        - title: El título de la tabla (opcional).
        - name: Nombre del archivo donde se guardará la tabla (opcional).

        Retorna una conexión a la base de datos con la tabla creada.
        """
            
        df = self.to_Dataframe()

        fig, ax = plt.subplots(figsize=(len(df.columns)*0.5, len(df)*0.24))  # Ajusta el tamaño de la figura según el número de filas
        ax.axis('off')
        ax.set_title(kwargs["title"] if "title" in kwargs else None)
        ax.table(
            cellText=df.values,
            colLabels=df.columns, 
            cellLoc='center', 
            loc='center',
            colWidths=[0.3]*len(df.columns)
        )
        plt.savefig(kwargs["name"] if "name" in kwargs else "tabla.png", bbox_inches='tight', dpi=300)
        plt.close()
      

if __name__ == "__main__":
    #lector_json = Lector.from_json("listado.json")
    #data = lector_json.get_data()
    #print(data,"\n\n\n")

    config = {
        "host": 'ep-square-rice-aie5emz3-pooler.c-4.us-east-1.aws.neon.tech',
        "database": 'neondb', 
        "user": 'neondb_owner',
        "password": 'npg_ESTpNfPh6y3a',
        "port": '5432',
        "table": 'registro'
    }

    lector_json_2 = Lector.from_db(**config)
    data_2 = lector_json_2.to_Dataframe()
    print(data_2,"\n\n\n")

    lector_json_2.to_image(name="tabla_datos.png")

    print("\n\n\n")
    hola = lector_json_2.crear_tabla(data_2, formato='tabule', showindex=True)
    print(hola)