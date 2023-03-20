import flask
from flask import Flask
from flask import render_template, request, redirect, session
from datetime import datetime    #se usa para respetar nombres incluyendo el time como variable de cambio
from flask import send_from_directory    #obtiene info directamente de la imagen
import os
from flaskext.mysql import MySQL         #extension para usar MySQL en flask
from flask_session import Session


app=Flask(__name__)   #primera aplicacion __name__
app.secret_key="cesan51"
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'     #enlace a bd de MySQL
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='docente'
mysql.init_app(app)

@app.route('/')                    #se define como base de ruta principal
def inicio():
    return  render_template('sitio/index.html')


@app.route('/img/<imagen>')        #base de ruta para mostrar imagen almacenada
def imagenes(imagen):              #creacion de funcion con variable de almacenamiento variable
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route('/image/<imagen>')        #base de ruta para mostrar imagen almacenada
def images(imagen):              #creacion de funcion con variable de almacenamiento variable
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/image'),imagen)

@app.route('/docs/documento>')        #base de ruta para mostrar imagen almacenada
def documentos(documento):              #creacion de funcion con variable de almacenamiento variable
    print(documento)
    return send_from_directory(os.path.join('templates/sitio/docs'),documento)

@app.route('/css/<archivocss>')        #base de ruta para mostrar imagen almacenada
def css_link(archivocss):              #creacion de funcion con variable de almacenamiento variable
    print(archivocss)
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)


@app.route('/libros')               #creacion de ruta libros
def libros():
    conexion=mysql.connect()             #forma de muestra del almacenamiento
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `docente`")
    libros=cursor.fetchall()
    conexion.commit()                    #agrega el proceso
    print(libros)

    return  render_template('sitio/libros.html',libros=libros)      #el render funciona para renderizar y ubicar el documento en la app


@app.route('/nosotros')
def nosotros():
    return  render_template('sitio/nosotros.html')


@app.route('/admin/')
def admin_index():
    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login") 
    return  render_template('/admin/index.html')


@app.route('/admin/login', methods=['POST','GET'])
def admin_login():
     return  render_template('admin/login.html')


@app.route('/admin/login/accede', methods=['POST','GET'])
def admin_login_post():
   
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']

    print(_usuario)
    print(_password)

    if _usuario=="admin" and _password=="123":
        session["login"]=True  
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template("admin/login.html", mensaje="Acceso denegado")


@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()              #clerar es equivalente a limpiar las variables de sesion
    return redirect('/admin')


@app.route('/admin/libros')              #este incluye las conexiones a base de datos
def admin_libros():

    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")



    conexion=mysql.connect()             #forma de muestra del almacenamiento
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `docente`")
    libros=cursor.fetchall()
    conexion.commit()                    #agrega el proceso
    print(libros)
    return  render_template('/admin/libros.html',libros=libros)


@app.route('/admin/libros/guardar', methods=['POST'])       #forma en la cual se almacena los datos en la bd
def admin_libros_guardar():

    _grado=request.form['grado']                       #nuevas variables que almacena los datos recogidos en un form
    _materia=request.form['materia']
    _fecha=request.form['fecha']
    _actividad=request.form['actividad']                       #nuevas variables que almacena los datos recogidos en un form
    _descripcion=request.form['descripcion']
    _documento=request.files['documento']                       #nuevas variables que almacena los datos recogidos en un form
    _imagen=request.files['imagen']
    _comentario=request.form['comentario']                       #nuevas variables que almacena los datos recogidos en un form
    

    tiempo= datetime.now()                                  #esta evita nombres repetido añadiendo datatime
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _imagen.filename!="":
        nuevoNombre=horaActual+"_"+_imagen.filename
        _imagen.save("templates/sitio/img/"+nuevoNombre)

    if _documento.filename!="":
        documentonuevoNombre=horaActual+"_"+_documento.filename
        _imagen.save("templates/sitio/docs/"+documentonuevoNombre)

    sql="INSERT INTO `docente` (`id`,`grado`, `materia`, `fecha`, `actividad`, `descripcion`, `documento`, `imagen`, `comentario`) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s);"       #se agregan los datos a la bd en su respectivo orden
    datos=(_grado,_materia,_fecha,_actividad,_descripcion,documentonuevoNombre,nuevoNombre,_comentario)

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    print(_grado)           #los print se usan para ver la ejecucion en la consola
    print(_materia)
    print(_fecha)
    print(_actividad)           #los print se usan para ver la ejecucion en la consola
    print(_descripcion)
    print(_documento)
    print(_imagen)           #los print se usan para ver la ejecucion en la consola
    print(_comentario)
    

    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")
    return  redirect('/admin/libros')

    


@app.route('/admin/libros/borrar', methods=['POST'])      #se usa para crear el borrar desde la pagina libros a la bd
def admin_libros_borrar():
    _id=request.form['txtID']
    print(_id)

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT imagen FROM `docente` WHERE id=%s", (_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)       #este almacena y verifica los datos

    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):    #Borrado de imagen temporal en img
       os.unlink("templates/sitio/img/"+str(libro[0][0]))         #pregunta si la ruta existe y se es asi se ejecuta el unlink

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("DELETE FROM docente WHERE id=%s",(_id))
    conexion.commit()   #eliminado absoluto del dato de la bd
    
    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")
    return  redirect('/admin/libros')









@app.route('/admin/libros/editar', methods=['GET', 'POST'])      #se usa para crear el borrar desde la pagina libros a la bd
def admin_libros_editar():
    _id=request.form['txtID']
    print(_id)

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT imagen FROM `docente` WHERE id=%s", (_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)       #este almacena y verifica los datos

   # if os.path.exists("templates/sitio/img/"+str(libro[0][7])):    #Borrado de imagen temporal en img
    #    os.unlink("templates/sitio/img/"+str(libro[0][7]))         #pregunta si la ruta existe y se es asi se ejecuta el unlink

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT grado, materia, fecha, actividad, descripcion, documento, imagen, comentario FROM docente WHERE id = %s", (id,))
    

     # Si se envió el formulario de edición
    if request.method == 'POST':
        # Obtener los nuevos valores del formulario
        _grado = request.form['grado']
        _materia = request.form['materia']
        _fecha = request.form['fecha']
        _actividad = request.form['actividad']
        _descripcion = request.form['descripcion']
        _documento = request.form['documento']
        _imagen = request.form['imagen']
        _comentario = request.form['comentario']

        
        # Actualizar el registro en la base de datos
        cursor.execute("UPDATE docente SET grado = %s, materia = %s, fecha = %s, actividad = %s, descripcion = %s, documento = %s, imagen = %s, comentario = %s WHERE id = %s", (_grado, _materia, _fecha, _actividad, _descripcion, _documento, _imagen, _comentario, id))
        conexion.commit()

         # Redirigir al usuario a la página de detalles del registro actualizado
        return redirect('/admin/libros')

 
    
    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")
    return  redirect('/admin/libros')



@app.route('/edit', methods=['POST','GET'])
def edit():
   return  render_template('/admin/edit.html')

@app.route('/admin/libros/edit', methods=['POST','GET'])
def edit_contact():
    ID=request.form['ID']
    print(ID)
    

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `docente` WHERE id=%s", (ID))
    #cursor.execute("SELECT grado, materia, fecha, actividad, descripcion, documento, imagen, comentario FROM docente WHERE id = %s", (txtID))
    libro=cursor.fetchall()
    print(libro)       #este almacena y verifica los datos

    return render_template('/admin/edit.html', info = libro[0])



@app.route('/update/<id>', methods=['POST','GET'])
def update(id):
    #id=request.form['id']
    #print(id)

    if request.method == 'POST':
         _grado = request.form['grado']
         _materia = request.form['materia']
         _fecha = request.form['fecha']
         _actividad = request.form['actividad']
         _descripcion = request.form['descripcion']
         _documento = request.form['documento']
         _imagen = request.form['imagen']
         _comentario = request.form['comentario']

    tiempo= datetime.now()                                  #esta evita nombres repetido añadiendo datatime
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _imagen.filename!="":
        nuevoNombre=horaActual+"_"+_imagen.filename
        _imagen.save("templates/sitio/img/"+nuevoNombre)

    if _documento.filename!="":
        documentonuevoNombre=horaActual+"_"+_documento.filename
        _documento.save("templates/sitio/docs/"+documentonuevoNombre)
    

    conexion=mysql.connect()
    cursor= conexion.cursor()
    sql="UPDATE docente SET grado = %s, materia = %s, fecha = %s, actividad = %s, descripcion = %s, documento = %s, imagen = %s, comentario = %s  WHERE id = %s"
    data= (_grado, _materia, _fecha, _actividad, _descripcion, documentonuevoNombre, nuevoNombre, _comentario)
    id_registro="id"
    cursor.execute(sql,data, id_registro)
    #cursor.execute("UPDATE * FROM `docente` WHERE id=%s", (id))
    conexion.commit()  # Guardar los cambios en la base de datos
    return redirect('/admin/libros')



@app.route('/grado', methods=['POST','GET'])
def grados():
   return  render_template('/sitio/libros.html')

@app.route('/grado/buscar', methods=['POST','GET'])
def grados_buscar():
    ID=request.form['id']
    print(ID)
    

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `docente` WHERE grado=%s", (ID))
    #cursor.execute("SELECT grado, materia, fecha, actividad, descripcion, documento, imagen, comentario FROM docente WHERE id = %s", (txtID))
    libro=cursor.fetchall()
    print(libro)       #este almacena y verifica los datos

    return render_template('/admin/edit.html', libro = libro[0])






if __name__=='__main__':   #esto significa que si aplicaipon se encuentra en la pagina principal va a correr la app
    app.run(debug= True)

