from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2 #pip install psycopg2 
import psycopg2.extras
import re
from database.db import get_conection

conn = get_conection()

app  = Flask(__name__)
app.secret_key = "capuli"

@app.route('/')
def home():
    # Comprobar si el usuario ha iniciado sesión
    if 'loggedin' in session:
    
        # El usuario ha iniciado sesión mostrarles la página de inicio
        return render_template('home.html', username=session['primer_nombre'])
    # El usuario no ha iniciado sesión redirigir a la página de inicio de sesión
    return redirect(url_for('login'))

@app.route('/perfil')
def perfil(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Comprobar si el usuario ha iniciado sesión
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM empleado WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Mostrar la página de perfil con información de la cuenta
        return render_template('perfil.html', account=account)
    # El usuario no ha iniciado sesión redirigir a la página de inicio de sesión
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
   # Comprobar si existen solicitudes POST de "nombre de usuario" y "contraseña" (formulario enviado por el usuario)
    if request.method == 'POST' and 'cedula' in request.form and 'contrasena' in request.form:
        primer_nombre = request.form['cedula']
        contrasena    = request.form['contrasena']
        print(contrasena)
 
        # Verificar si la cuenta existe usando SQL
        cursor.execute('SELECT * FROM empleado WHERE cedula = %s', (primer_nombre,))
        # Obtener un registro y devolver el resultado
        account = cursor.fetchone()
 
        if account:
            password_rs = account['contrasena']
            print(password_rs)
            # Si la cuenta existe en la tabla de usuarios en la base de datos
            if check_password_hash(password_rs, contrasena):
                # Crear datos de sesión, podemos acceder a estos datos en otras rutas
                session['loggedin']      = True
                session['id']            = account['id']
                session['primer_nombre'] = account['primer_nombre']
                # Redirigir a la página de inicio
                return redirect(url_for('home'))
            else:
                # La cuenta no existe o el nombre de usuario/contraseña son incorrectos
                flash('Nombre de usuario/contraseña incorrectos')
        else:
            # La cuenta no existe o el nombre de usuario/contraseña son incorrectos
            flash('Nombre de usuario/contraseña incorrectos')
 
    return render_template('login.html')
  
@app.route('/registro_empleados')
def registro_empleados():
    cur        = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s          = "SELECT * FROM empleado ORDER BY empleado ASC"
    cur.execute(s) # Ejecutar la instrucción SQL
    list_users = cur.fetchall()
    return render_template('registro_usuario.html', list_users = list_users)
  
@app.route('/agregar_empleado', methods=['GET', 'POST'])
def agregar_empleado():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Comprueba si existen las peticiones POST "primer_nombre", "contraseña" y "email" (formulario enviado por el usuario)
    if request.method == 'POST' and 'primer_nombre' in request.form and 'contrasena' in request.form and 'email' in request.form:
        # Create variables for easy access
        cedula           = request.form['cedula']
        primer_nombre    = request.form['primer_nombre']
        segundo_nombre   = request.form['segundo_nombre']
        primer_apellido  = request.form['primer_apellido']
        segundo_apellido = request.form['segundo_apellido']
        direccion        = request.form['direccion']
        telefono         = request.form['telefono']
        email            = request.form['email']
        contrasena       = request.form['contrasena']
        tipo_usuario     = request.form['tipo_usuario']
    
        _hashed_password = generate_password_hash(contrasena)
 
        #Comprueba si la cuenta existe usando SQL
        cursor.execute('SELECT * FROM empleado WHERE cedula = %s', (cedula,))
        account = cursor.fetchone()
        print(account)
        # Si la cuenta existe mostrar error y comprobaciones de validación
        if account:
            flash('¡La cuenta ya existe!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('¡Dirección de correo electrónico no válida!')
        elif not re.match(r'[A-Za-z0-9]+', primer_nombre):
            flash('¡El nombre de usuario debe contener solo caracteres y números!')
        elif not primer_nombre or not email or not contrasena:
            flash('¡Por favor rellena el formulario!')
        else:
            # La cuenta no existe y los datos del formulario son válidos, ahora inserta una nueva cuenta en la tabla de usuarios
            cursor.execute("INSERT INTO empleado (cedula, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, direccion, telefono, email, contrasena, tipo_usuario) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (cedula, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, direccion, telefono, email, _hashed_password, tipo_usuario))
            conn.commit()
            flash('¡Usuario registrado correctamente!')
            return redirect(url_for('registro_empleados'))
    elif request.method == 'POST':
        # El formulario está vacío... (sin datos POST)
        flash('¡Por favor rellena el formulario!')
    # Mostrar formulario de registro con mensaje (si corresponde)
    return render_template('registro_usuario.html')

# OBTENER EMPLEADOS
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_empleado(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM empleado WHERE id = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit_empleado.html', empleados = data[0])

# ACTUALIZAR EMPLEADOS
@app.route('/update_empleados/<id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        cedula           = request.form['cedula']
        primer_nombre    = request.form['primer_nombre']
        segundo_nombre   = request.form['segundo_nombre']
        primer_apellido  = request.form['primer_apellido']
        segundo_apellido = request.form['segundo_apellido']
        direccion        = request.form['direccion']
        telefono         = request.form['telefono']
        email            = request.form['email']
        contrasena       = request.form['contrasena']
        tipo_usuario     = request.form['tipo_usuario']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE empleado
            SET cedula           = %s,
                primer_nombre    = %s,
                segundo_nombre   = %s,
                primer_apellido  = %s,
                segundo_apellido = %s,
                direccion        = %s,
                telefono         = %s,
                email            = %s,
                contrasena       = %s,
                tipo_usuario     = %s
            WHERE id             = %s
        """, (cedula, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, direccion, telefono, email, contrasena, tipo_usuario, id))
        flash('Cambios guardados con éxito')
        conn.commit()
        return redirect(url_for('registro_empleados'))

# ELIMINAR EMPLEADOS
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_empleados(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM empleado WHERE id = {0}'.format(id))
    conn.commit()
    flash('Usuario Eliminado Correctamente')
    return redirect(url_for('registro_empleados'))

# OBTENER DATOS DEL PROVEEDOR
@app.route('/proveedor')
def Proveedor():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s = "SELECT * FROM proveedor ORDER BY proveedor ASC;"
    cur.execute(s) 
    list_prov = cur.fetchall()
    return render_template('registro_proveedor.html', list_prov = list_prov)

# AGREGAR PROVEEDOR
@app.route('/add_proveedor', methods=['POST'])
def add_proveedor():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        ruc          = request.form['id_proveedor']
        nombre       = request.form['nombre']
        direccion    = request.form['direccion']
        correo       = request.form['correo']
        telefono     = request.form['telefono']
        cur.execute("INSERT INTO proveedor (ruc, nombre, direccion, correo, telefono) VALUES (%s,%s,%s,%s,%s)", (ruc, nombre, direccion,correo,telefono))
        conn.commit()
        flash('¡Proveedor registrado correctamente!')
        return redirect(url_for('Proveedor'))

# EDITAR PROVEEDORES
@app.route('/edit_pro/<id>', methods = ['POST', 'GET'])
def get_proveedor(id):
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM proveedor WHERE id = %s", (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit_proveedor.html', proveedor = data[0])

# ACTUALIZAR PROVEEDORES
@app.route('/update_proveedor/<id>', methods=['POST'])
def update_proveedor(id):
    if request.method == 'POST':
        ruc          = request.form['ruc']
        nombre       = request.form['nombre']
        direccion    = request.form['direccion']
        correo       = request.form['correo']
        telefono     = request.form['telefono']
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE proveedor
            SET ruc          = %s,
                nombre       = %s,
                direccion    = %s,
                correo       = %s,
                telefono     = %s
            WHERE id         = %s
        """, (ruc, nombre, direccion, correo, telefono, id))
        flash('Cambios guardados con éxito')
        conn.commit()
        return redirect(url_for('Proveedor'))

# ELIMINAR PROVEEDORES
@app.route('/delete_Proveedor/<string:id>', methods = ['POST','GET'])
def delete_proveedor(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute('DELETE FROM proveedor WHERE id = {0}'.format(id))
    conn.commit()
    flash('Proveedor Eliminado Correctamente')
    return redirect(url_for('Proveedor'))  

# Obtener datos de Productos
@app.route('/productos')
def productos():
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curc = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s    = "SELECT producto.id, producto.nombre, producto.precio_venta, producto.cantidad, categoriat.nombre_categoria from producto, categoriat WHERE categoriat.id_categoria = producto.id_categoria ORDER BY producto ASC"
    sc   = "SELECT * FROM categoriat"
    cur.execute(s)
    curc.execute(sc)
    list_productos  = cur.fetchall()
    list_cproductos = curc.fetchall()
    return render_template('registro_productos.html', list_productos = list_productos, list_cproductos = list_cproductos)

# Insertar datos en Productos
@app.route('/add_productos', methods=['POST'])
def add_productos():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        id           = request.form['id_producto']
        nombre       = request.form['nombre']
        precioventa  = request.form['precioventa']
        cantidad     = 0
        id_categoria = request.form['estados']
        cur.execute("INSERT INTO producto (id, nombre, precio_venta, cantidad, id_categoria) VALUES (%s, %s, %s, %s, %s)", (id,nombre,precioventa,cantidad,id_categoria))
        conn.commit()
        flash('¡Producto agregado con éxito!')
        return redirect(url_for('productos'))

# Editar productos
@app.route('/edit_productos/<id>', methods = ['POST', 'GET'])
def get_productos(id):
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curc = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT producto.id, producto.nombre, producto.precio_venta, producto.cantidad, categoriat.nombre_categoria from producto, categoriat WHERE categoriat.id_categoria = producto.id_categoria and producto.id = %s", (id,))
    sc   = "SELECT * FROM categoriat"
    curc.execute(sc)
    data = cur.fetchall()
    list_cproductos = curc.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit_productos.html', productos = data[0], list_cproductos=list_cproductos)
  
#actualizar productos
@app.route('/update_productos/<id>', methods=['POST'])
def update_productos(id):
    if request.method == 'POST':
        nombre       = request.form['nombre']
        precio_venta = request.form['cantidad']
        cantidad     = request.form['cantidad']
        id_categoria = request.form['estados']
        cur          = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE producto
            SET nombre   = %s,
            precio_venta = %s,
            cantidad     = %s,
            id_categoria = %s
            WHERE id     = %s
        """, (nombre, precio_venta, cantidad, id_categoria, id))
        flash('Cambios guardados con éxito')
        conn.commit()
        return redirect(url_for('productos'))

# Eliminar productos
@app.route('/delete_productos/<string:id>', methods = ['POST','GET'])
def delete_productos(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM producto WHERE id = {0}'.format(id))
    conn.commit()
    flash('Producto Eliminado Correctamente')
    return redirect(url_for('productos'))  

# Datos de salida de productos (Ventas)
@app.route('/salida_productos')
def salida_productos():
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curc = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s    ="SELECT venta.id_venta, venta.fecha_venta, venta.precio, venta.cantidad, producto.nombre from producto, venta where venta.id_producto = producto.id ORDER BY venta ASC"
    sc   = "SELECT * FROM public.producto"
    cur.execute(s)
    curc.execute(sc)
    list_productos  = cur.fetchall()
    list_cproductos = curc.fetchall()
    return render_template('salida_productos.html', list_productos = list_productos, list_cproductos = list_cproductos)

# Salida de productos
@app.route('/add_salidaproductos', methods=['POST'])
def add_salidaproductos():
    cur     = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curactu = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        id_venta    = request.form['id_venta']
        fechaventa  = request.form['fechaventa']
        precioventa = request.form['precioventa']
        cantidad    = request.form['cantidad']
        id_producto = request.form['estados']
        cur.execute("INSERT INTO venta (id_venta, fecha_venta, precio, id_producto, cantidad) VALUES (%s, %s, %s, %s, %s)", (id_venta,fechaventa,precioventa, id_producto, cantidad))
        curactu.execute("""
            UPDATE producto
            SET cantidad = cantidad-%s
            WHERE id     = %s
        """, (cantidad, id_producto))
        conn.commit()
        flash('¡Venta realizada con éxito!')
        return redirect(url_for('salida_productos'))
    
# ENTRADA DE PRODUCTOS (COMPRAS)
@app.route('/entrada_productos')
def entrada_productos():
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curc = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curp = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curu = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    s    = "SELECT compra.id_compra, compra.fecha_compra, compra.precio_compra, compra.cantidad, producto.nombre, proveedor.nombre, empleado.primer_nombre from producto, compra, proveedor, empleado where compra.id_producto = producto.id AND compra.id_proveedor = proveedor.id AND compra.id_usuario = empleado.id ORDER BY compra ASC"
    sc   = "SELECT * FROM public.producto"
    sp   = "SELECT * FROM public.proveedor"
    su   = "SELECT * FROM public.empleado"
    
    cur.execute(s)
    curc.execute(sc)
    curp.execute(sp)
    curu.execute(su)
    
    list_productos  = cur.fetchall()
    list_cproductos = curc.fetchall()
    list_pproveedor = curp.fetchall()
    list_uuser      = curu.fetchall()
    
    return render_template('entrada_productos.html', list_productos = list_productos, list_cproductos = list_cproductos, list_pproveedor = list_pproveedor, list_uuser = list_uuser)

# ENTRADA DE PRODUCTOS (COMPRAS)
@app.route('/add_entrada_productos', methods=['POST'])
def add_entrada_productos():
    cur     = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curactu = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        id_compra     = request.form['id_compra']
        fecha_compra  = request.form['fecha_compra']
        precio_compra = request.form['precio_compra']
        cantidad      = request.form['cantidad']
        id_producto   = request.form['estados']
        id_proveedor  = request.form['mproveedor']
        id_usuario    = request.form['musuario']

        
        cur.execute("INSERT INTO compra (id_compra, fecha_compra, precio_compra, cantidad, id_producto, id_proveedor, id_usuario) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id_compra, fecha_compra, precio_compra, cantidad, id_producto, id_proveedor, id_usuario))
        curactu.execute("""
            UPDATE producto
            SET cantidad = cantidad+%s
            WHERE id     = %s
        """, (cantidad, id_producto))
        conn.commit()
        flash('¡Compra realizada con éxito!')
        return redirect(url_for('entrada_productos'))

# Obtener datos de categoria
@app.route('/categoria')
def categoria():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    s   = "SELECT * FROM categoriat ORDER BY categoriat ASC;"
    cur.execute(s) 
    list_cate = cur.fetchall()
    return render_template('registro_categoria.html', list_cate = list_cate)

# Agregar categoria en la tabla 
@app.route('/add_categoria', methods=['POST'])
def add_categoria():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        id     = request.form['id']
        nombre = request.form['nombre']
        cur.execute("INSERT INTO categoriat (id_categoria, nombre_categoria) VALUES (%s, %s)", (id,nombre))
        conn.commit()
        flash('¡Categoria agragada con éxito!')
        return redirect(url_for('categoria'))

# Editar categoria
@app.route('/edit_categoria/<id>', methods = ['POST', 'GET'])
def get_categoria(id):
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute("SELECT * FROM categoriat WHERE id_categoria = %s", (id,))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit_categoria.html', categoria = data[0])

# Actualizar categoria
@app.route('/update_categoria/<id>', methods=['POST'])
def update_categoria(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cur    = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE categoriat
            SET nombre_categoria = %s
            WHERE id_categoria   = %s
        """, (nombre, id))
        flash('Cambios guardados con éxito')
        conn.commit()
        return redirect(url_for('categoria'))

# Eliminar categoria
@app.route('/delete_categoria/<string:id>', methods = ['POST','GET'])
def delete_categoria(id):
    cur    = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curpro = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    curpro.execute('DELETE FROM producto WHERE id_categoria = {0}'.format(id))
    cur.execute('DELETE FROM categoriat WHERE id_categoria  = {0}'.format(id))
    conn.commit()
    flash('Categoria Eliminada Correctamente')
    return redirect(url_for('categoria'))  

@app.route('/logout')
def logout():
   # Eliminar datos de sesión, esto cerrará la sesión del usuario
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('primer_nombre', None)
   # Redirect to login page
   return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True) 