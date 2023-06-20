from flask import(
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
from datetime import datetime, timedelta
import hashlib
from pymongo import MongoClient, DeleteMany
from werkzeug.utils import secure_filename
import jwt
import locale

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

collection_package1 = db['package1']
collection_package2 = db['package2']
collection_package3 = db['package3']
collection_package4 = db['package4']

pesan_collection = db['pesan']  # Ganti 'pesan' dengan nama koleksi Anda

SECRET_KEY = 'TRAVEL'

TOKEN_KEY = 'mytoken'


# --------------------------------------------LANDING PAGE & USERPAGE---------------------------------------------------
@app.route('/')
def home():
    data1 = db.package1.find_one(sort=[('_id', -1)])
    data2 = db.package2.find_one(sort=[('_id', -1)])
    data3 = db.package3.find_one(sort=[('_id', -1)])
    data4 = db.package4.find_one(sort=[('_id', -1)])


    return render_template('index.html', data1=data1, data2=data2, data3=data3, data4=data4)

@app.route('/userpage')
def userpage():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username = payload.get('username')
        if not username:
            return redirect(url_for('login', msg='Username not found in payload'))
        
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))

    data1 = db.package1.find_one(sort=[('_id', -1)])
    data2 = db.package2.find_one(sort=[('_id', -1)])
    data3 = db.package3.find_one(sort=[('_id', -1)])
    data4 = db.package4.find_one(sort=[('_id', -1)])
    
    

    return render_template('user.html', data1=data1, data2=data2, data3=data3, data4=data4)

    
    
    
    

@app.route('/pesan', methods=['POST'])
def pesan():
    nama_receive = request.form.get('nama_give')
    package_receive = request.form.get('package_give')
    harga_receive = request.form.get('harga_give')
    phone_receive = request.form.get('phone_give')
    tanggal_pesan = datetime.now()  # Mendapatkan tanggal saat ini

    doc = {
        'nama': nama_receive,
        'package': package_receive,
        'harga': harga_receive,
        'phone': phone_receive,
        'tanggal_pesan': tanggal_pesan
    }
    db.pesan.insert_one(doc)
    return jsonify({'result': 'success'})


# --------------------------------------------SIGN UP---------------------------------------------------
@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/sign_up/save', methods=['POST'])
def save():
    firstname_receive = request.form.get('firstname_give')
    lastname_receive = request.form.get('lastname_give')
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')

    hashed_password = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    

    user = db.users.find_one({'username': username_receive})
    if user:
        return jsonify({'message': 'Username already exists'})
    
    doc = {
        'firstname': firstname_receive,
        'lastname': lastname_receive,
        'username': username_receive,
        'password': hashed_password
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# --------------------------------------------LOGIN---------------------------------------------------
@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template('login.html')

@app.route('/user', methods=['GET'])
def user():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            # untuk menterjemahkan token
            algorithms=['HS256']
        )
        return render_template('index.html')
    # membuat jika tokennya kadaluarsa
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for('login', msg=msg))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
        return redirect(url_for('login', msg=msg))

@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form.get("username_give")
    password_receive = request.form.get("password_give")

    hashed_password = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    print(username_receive)
    print(hashed_password)

    user = db.users.find_one(
        {
            "username": username_receive,
            "password": hashed_password,
        }
    )

    print(user)
    if user:
        payload = {
            "username": username_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )



# --------------------------------------------ABOUT PAGE---------------------------------------------------
@app.route('/about')
def about():
    data1 = db.package1.find_one(sort=[('_id', -1)])
    data2 = db.package2.find_one(sort=[('_id', -1)])
    data3 = db.package3.find_one(sort=[('_id', -1)])
    data4 = db.package4.find_one(sort=[('_id', -1)])


    return render_template('about.html', data1=data1, data2=data2, data3=data3, data4=data4)






# --------------------------------------------SUPER ADMIN (PENJUMLAHAN MASIH ERROR)---------------------------------------------------
@app.route('/superadmin')
def superadmin():
    biaya_data = db.pesan.find({'harga': {'$ne': ''}}, {'harga': 1})
    order = db.pesan.count_documents({})
    print("Jumlah data pada koleksi 'pesan':", order)
    # Mengambil kumpulan data pesan
    data_pesan = list(db.pesan.find())
    
    # Menambahkan nomor urutan ke setiap pesan
    for superadmin, pesan in enumerate(data_pesan, start=1):
        pesan['nomor_urut'] = superadmin
    
    # Mengambil tanggal pesan dari setiap dokumen
    for pesan in data_pesan:
        tanggal_pesan = pesan.get('tanggal_pesan')
        if tanggal_pesan:
            pesan['tanggal_pesan'] = tanggal_pesan.strftime('%d %B %Y')  # Ubah format tanggal sesuai kebutuhan

    # Menginisialisasi variabel penjumlahan
    total_biaya = 0
    print(total_biaya)
    # Menghitung total biaya dari data1
    for doc in biaya_data:
        total_biaya += int(doc['harga'])


     # Mengatur pengaturan lokal untuk format Rupiah
    locale.setlocale(locale.LC_ALL, 'id_ID')

    # Format total_biaya menjadi format Rupiah
    total_biaya_formatted = locale.currency(total_biaya, grouping=True, symbol=False)



    # Render template HTML dan kirimkan total biaya sebagai argumen
    return render_template('superadmin.html', total_biaya=total_biaya_formatted, order=order, data_pesan=data_pesan)

@app.route('/delete_data', methods=['POST'])
def delete_data():
    delete_operations = [
        DeleteMany({}),
        DeleteMany({}),
        DeleteMany({}),
        DeleteMany({})
    ]

    for delete_op in delete_operations:
        db.package1.delete_many({})
        db.package2.delete_many({})
        db.package3.delete_many({})
        db.package4.delete_many({})

    return jsonify({'message': 'Data berhasil dihapus'})

@app.route('/superadmin/package1', methods=['POST'])
def adminpackage1():
    detail_receive = request.form.get('detail_give')
    penginapan_receive = request.form.get('penginapan_give')
    akomodasi_receive = request.form.get('akomodasi_give')
    rute_receive = request.form.get('rute_give')
    biaya_receive = request.form.get('biaya_give')

    doc = {
        'detail': detail_receive,
        'penginapan': penginapan_receive,
        'akomodasi': akomodasi_receive,
        'rute': rute_receive,
        'biaya': biaya_receive,
    }
    db.package1.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/superadmin/package2', methods=['POST'])
def adminpackage2():
    detail_receive2 = request.form.get('detail_give2')
    penginapan_receive2 = request.form.get('penginapan_give2')
    akomodasi_receive2 = request.form.get('akomodasi_give2')
    rute_receive2 = request.form.get('rute_give2')
    biaya_receive2 = request.form.get('biaya_give2')

    doc = {
        'detail': detail_receive2,
        'penginapan': penginapan_receive2,
        'akomodasi': akomodasi_receive2,
        'rute': rute_receive2,
        'biaya': biaya_receive2,
    }
    db.package2.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/superadmin/package3', methods=['POST'])
def adminpackage3():
    detail_receive3 = request.form.get('detail_give3')
    penginapan_receive3 = request.form.get('penginapan_give3')
    akomodasi_receive3 = request.form.get('akomodasi_give3')
    rute_receive3 = request.form.get('rute_give3')
    biaya_receive3 = request.form.get('biaya_give3')

    doc = {
        'detail': detail_receive3,
        'penginapan': penginapan_receive3,
        'akomodasi': akomodasi_receive3,
        'rute': rute_receive3,
        'biaya': biaya_receive3,
    }
    db.package3.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/superadmin/package4', methods=['POST'])
def adminpackage4():
    detail_receive4 = request.form.get('detail_give4')
    penginapan_receive4 = request.form.get('penginapan_give4')
    akomodasi_receive4 = request.form.get('akomodasi_give4')
    rute_receive4 = request.form.get('rute_give4')
    biaya_receive4 = request.form.get('biaya_give4')

    doc = {
        'detail': detail_receive4,
        'penginapan': penginapan_receive4,
        'akomodasi': akomodasi_receive4,
        'rute': rute_receive4,
        'biaya': biaya_receive4,
    }
    db.package4.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    nama = data.get('nama')
    status = data.get('status')

    # Memperbarui status pesanan dalam database
    db.pesan.update_one({'nama': nama}, {'$set': {'status': status}})

    return jsonify({'message': 'Status pesanan berhasil diperbarui.'})



if __name__ == '__main__':
    app.run(debug=True)