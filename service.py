from db import DatabaseConnection
import json
import datetime

from http_errors import HTTP_BAD_REQUEST, HTTP_OK

class RegisterManager:
    def __init__(self):
        self.database = DatabaseConnection()
        self.cursor = self.database.connect()
    #values = numeroAtencion, tipoEscritura, comuna, manzana, predio, enajenante, adquirente, fojas, fecha, nmroInscripcion
    def post_register_to_db(self, numeroAtencion, tipoEscritura, comuna, manzana, predio, enajenante, adquiriente, fojas, fecha, nmroInscripcion):
        try:
            senajenante = json.dumps(enajenante)
            sadquiriente = json.dumps(adquiriente)
            if len(numeroAtencion) > 0:
                string_sql = f"INSERT INTO Registros (N_Atencion, CNE, Comuna, Manzana, Predio, Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, Numero_Inscripcion) VALUES ('{numeroAtencion}', '{tipoEscritura}', '{comuna}', '{manzana}', '{predio}', '{senajenante}', '{sadquiriente}', '{fojas}', '{fecha}', '{nmroInscripcion}')"
            else:
                string_sql = f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, Numero_Inscripcion) VALUES ('{tipoEscritura}', '{comuna}', '{manzana}', '{predio}', '{senajenante}', '{sadquiriente}', '{fojas}', '{fecha}', '{nmroInscripcion}')"
            self.cursor.execute(string_sql)
            self.database.commit()

            #for i in enajenante:
            #    rut = i['rut']
            #    derecho = i['derecho']
            #    if len(derecho) > 0:
            #        string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Porcentaje_Derechos, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{derecho}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
            #    else:
            #        string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
            #    print(string_sql)
            #    self.cursor.execute(string_sql)
            #    self.database.commit()

            #for i in adquiriente:
            #    rut = i['rut']
            #    derecho = i['derecho']
            #    if len(derecho) > 0:
            #        string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Porcentaje_Derechos, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{derecho}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
            #    else:
            #        string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
            #    print(string_sql)
            #    self.cursor.execute(string_sql)
            #    self.database.commit()

            return HTTP_OK
        except Exception as e:
            print("Ocurrio un error: " + e)
            return HTTP_BAD_REQUEST

    def get_all_registers(self):
        string_sql = 'SELECT * FROM Registros'
        self.cursor.execute(string_sql)
        registers = self.cursor.fetchall()
        return registers

    def get_register_by_id(self, id: int):
        string_sql = f'SELECT * FROM Registros WHERE N_Atencion = {id}'
        self.cursor.execute(string_sql)
        register = self.cursor.fetchone()
        return register
    
    def get_multiprop(self, comuna, manzana, predio, fecha):
        string_sql = f'SELECT * FROM Multipropietarios WHERE Comuna = {comuna} AND Manzana = {manzana} AND Predio = {predio}'
        self.cursor.execute(string_sql)
        multiprop = self.cursor.fetchall()
        multiprops = []
        for i in multiprop:
            ano = int(fecha)
            fi = i['Fecha_Inscripcion']
            #fi datetime.date object
            year = fi.year
            avf = i['Ano_Vigencia_Final']
            if avf != None:
                if year < ano and avf > ano:
                    multiprops.append(i)
            else:
                avi = i['Ano_Vigencia_Inicial']
                if avi != None:
                    if year <= ano and avi >= ano:
                        multiprops.append(i)
                else:
                    if year <= ano:
                        multiprops.append(i)

        return multiprops
    
    def process_json(self, file_object):   
        try:
            file = file_object.read()
            all_registers = json.loads(file)
            errors = []
            for register in all_registers["F2890"]:
                cne = register["CNE"]
                comuna = register["bienRaiz"]["comuna"]
                manzana = register["bienRaiz"]["manzana"]
                predio = register["bienRaiz"]["predio"]
                if "enajenantes" in register.keys():
                    enajenantes = json.dumps(register["enajenantes"])
                    enan = register["enajenantes"]
                else:
                    enajenantes = json.dumps([])
                    enan = []
                if "adquirentes" in register.keys():
                    adquirentes = json.dumps(register["adquirentes"])
                    adq = register["adquirentes"]
                else:
                    adquirentes = json.dumps([])
                    adq = []
                fojas = register["fojas"]
                fecha = register["fechaInscripcion"]
                nmroInscripcion = register["nroInscripcion"]
                
                if type(cne) != int or type(comuna) != int or type(manzana) != int or type(predio) != int or type(enajenantes) != str or type(adquirentes) != str or type(fojas) != int or type(fecha) != str or type(nmroInscripcion) != int:
                    print("error")
                    errors.append(register)
                    continue
                    
                month = int(fecha.split('-')[1])
                day = int(fecha.split('-')[2])
                if month > 12 or month < 1 or day < 1 or day > 31:
                    print("error")
                    errors.append(register)
                    continue

                string_sql = f"INSERT INTO Registros (CNE, Comuna, Manzana, Predio, Enajenantes, Adquirentes, Fojas, Fecha_Inscripcion, Numero_Inscripcion) VALUES ('{cne}', '{comuna}', '{manzana}', '{predio}', '{enajenantes}', '{adquirentes}', '{fojas}', '{fecha}', '{nmroInscripcion}')"
                self.cursor.execute(string_sql)
                self.database.commit()

                #try:
                #    for i in enan:
                #        rut = i['RUNRUT']
                #        derecho = i['porcDerecho']
                #        if derecho > 0:
                #            string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Porcentaje_Derechos, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{derecho}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
                #        else:
                #            string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
                #        self.cursor.execute(string_sql)
                #        self.database.commit()
                #except Exception as e:
                #    pass
                #
                #try:
                #    for i in adq:
                #        rut = i['RUNRUT']
                #        derecho = i['porcDerecho']
                #        if derecho:
                #            string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Porcentaje_Derechos, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{derecho}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
                #        else:
                #            string_sql = f"INSERT INTO Multipropietarios (Comuna, Manzana, Predio, RUN_RUT, Fojas, Numero_Inscripcion, Fecha_Inscripcion) VALUES ('{comuna}', '{manzana}', '{predio}', '{rut}', '{fojas}', '{nmroInscripcion}', '{fecha}')"
                #        self.cursor.execute(string_sql)
                #        self.database.commit()
                #except Exception as e: 
                #    pass


            return errors
                

        except Exception as e:
            print("Ocurrio un error: ", e)
            errors.append(e)
            return errors
    
    def pprocess_json(self, file_object):
        try:
            file = file_object.read()
            all_registers = json.loads(file)
            string_sql = 'INSERT INTO Registros (texto, numero) VALUES '
            for register in all_registers:
                string_sql += f"('{register['texto']}', {register['numero']}),"
            string_sql = string_sql[:-1]
            self.cursor.execute(string_sql)
            self.database.commit()
            return HTTP_OK
        except Exception as e:
            print("Ocurrio un error: " + e)
            return HTTP_BAD_REQUEST