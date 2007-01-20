import os, datetime, dbaccess

"""
El objetivo de esta clase es descargar las bases de datos comprimidas de los diferentes idiomas
que van a ser objeto de estudio por parte del programa.

Una vez descargadas, en formazo 7zip para optimizar el espacio de almacenamiento, se descomprime
la base de datos de cada idioma a su correspondiente base de datos en MySQL local.

De esta forma, la BD de cada idioma queda ya preparada para su correspondiente an�lisis.
"""
def download_bd (conf, language="furwiki"):
	# Recibe como par�metro el idioma que queremos descargar
	# La funcion usar� w-get para descubrir la �ltima versi�n correcta del volcado de ese idioma
	
	str_types={"dump_pages":"pages-meta-history.xml.7z", "dump_stub":"stub-meta-history.xml.gz"}
	
	urld="http://download.wikimedia.org/"+language+"/latest/"+language+"-latest-"+str_types.get(conf.dumptype)
	urlp="http://download.wikimedia.org/"+language+"/latest/"+language+"-latest-page.sql.gz"
	#pattern="http://download.wikimedia.org/furwiki/20060921/furwiki-20060921-pages-meta-history.xml.7z"
	#http://download.wikimedia.org/amwiki/20061014/amwiki-20061014-stub-meta-history.xml.gz
	
	print "Tratando de recuperar el archivo... "+urld+"\n"
	success=os.system("wget -P dumps -o log_"+language+" --ignore-length "+urld)
	if success== 0:
		print "Tratando de recuperar el archivo... "+urlp+"\n"
		ok=os.system("wget -P dumps -o log_"+language+" --ignore-length "+urlp)
		if ok==0:
			return (language+"-latest-"+str_types.get(conf.dumptype))
		else:
			print "Fallo en la recuperacion del archivo de datos de paginas... "+language
	else:
		print "FALLO EN recuperacion del archivo latest para el lenguage --- "+language	
	print "status= %i" % success	

def unzip_bd (conf, filename, language="furwiki"):
	# Recibe como par�metro el idioma que queremos descomprimir
	ok=__init_bd(conf, language)
	#print "traza ok = %i \n" % ok	
	if ok == 0:
		print("BD inicializada, descomprimiendo archivos...")
		if conf.dumptype=="dump_pages":
			# La funcion llama al script de descompresi�n y pasa a traves de un pipe la info a mwdumper y de ah� a MySQL
			command="7za e -so dumps/"+filename+ " | "+conf.jpath+" -jar "+conf.mwpath+" --format=sql:1.5 | mysql -u "+conf.msqlu+" -p"+conf.msqlp+" "+language+conf.dumptype.lstrip("dump")
			success=os.system(command)
			if success == 0:
				print "BD descomprimida para el idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
			else:
				print "Ocurrio algun problema al descomprimir BD del idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
		elif conf.dumptype=="dump_stub":
			command_unzip="gzip -d dumps/"+filename
			success=os.system(command_unzip)
			if success == 0:
				command_decompress=conf.jpath+" -jar "+conf.mwpath+" --format=sql:1.5 dumps/"+filename.replace(".gz", "")+" | mysql -u "+conf.msqlu+" -p"+conf.msqlp+" "+language+conf.dumptype.lstrip("dump")
				succ=os.system(command_decompress)
				if succ == 0:
					print "BD descomprimida para el idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
					command_zip="gzip dumps/"+filename.replace(".gz","")
					os.system(command_zip)
				else:
					print "Ocurrio algun problema al descomprimir BD del idioma ... "+language+conf.dumptype.lstrip("dump")+"\n\n"
			else:
				print "Problema de descompresion del archivo .zip\n"
				
		else:
			print "Error en la seleccion del tipo de archivo de descompresion"
	else:
		print "Error de inicializaci�n de la BD\n"

def __init_bd(conf, language="furwiki", dump_type="dump_stub"):
	# Construye la BD en MySQL para poder importar el dump del idioma indicado como argumento
	
	print "Inicializando BD para "+ language +"\n"
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp)
	dbaccess.createDB_SQL(acceso[1],language+conf.dumptype.lstrip("dump"))
	dbaccess.close_Connection(acceso[0])
	command_unzip="gzip -d dumps/"+language+"-latest-page.sql.gz"
	os.system(command_unzip)
	command1="mysql -u "+conf.msqlu+" -p"+conf.msqlp+" " + language+conf.dumptype.lstrip("dump") + " < "+language+"-latest-page.sql"+" > output.txt"
	os.system(command1)
	acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
	dbaccess.raw_query_SQL(acceso[1], "rename table page to aux")
	dbaccess.close_Connection(acceso[0])
	command_zip="gzip dumps/"+language+"-latest-page.sql"
	os.system(command_zip)
	command2="mysql -u "+conf.msqlu+" -p"+conf.msqlp+" " + language+conf.dumptype.lstrip("dump") + " < tables_15_09_2006.sql > output.txt"
	ok=os.system(command2)
	if ok == 0:
		acceso = dbaccess.get_Connection("localhost", 3306, conf.msqlu, conf.msqlp, language+conf.dumptype.lstrip("dump"))
		dbaccess.raw_query_SQL(acceso[1], "alter table page max_rows = 200000000000 avg_row_length = 50")
		dbaccess.raw_query_SQL(acceso[1], "alter table revision max_rows = 200000000000 avg_row_length = 50")
		dbaccess.raw_query_SQL(acceso[1], "alter table text max_rows = 200000000000 avg_row_length = 50")
		dbaccess.close_Connection(acceso[0])
		return ok
	else:
		print "Problema al crear la BD"
		return -1
	
	
