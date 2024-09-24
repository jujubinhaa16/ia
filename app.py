from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
import cloudinary.uploader
from config_cloudinary import configurar_cloudinary
from detectar_objetos import contar_objetos
import cv2


# Configura o app Flask
app = Flask(__name__)

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sua_senha@localhost/contagem_objetos'  # Ajuste sua URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configura o Cloudinary
configurar_cloudinary()


# Modelo do banco de dados
class ObjetoContado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    foto_url = db.Column(db.String(255))


# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adminn')
def adminn():
    return render_template('admin.html')


# Rota para contar objetos e preencher o banco de dados
@app.route('/contar', methods=['POST'])
def contar():
    # Captura da câmera
    cap = cv2.VideoCapture(0)  # Use 0 para a câmera padrão
    ret, frame = cap.read()
    cap.release()

    if ret:
        # Contagem de objetos usando IA
        contagem_de_objetos = contar_objetos(frame)

        # Salva a imagem capturada
        cv2.imwrite('foto.jpg', frame)

        # Upload da imagem para o Cloudinary
        resultado_foto = cloudinary.uploader.upload('foto.jpg')
        foto_url = resultado_foto['secure_url']

        # Preencher o banco de dados com a contagem e o link da foto
        for nome, quantidade in contagem_de_objetos.items():
            novo_objeto = ObjetoContado(nome=nome, quantidade=quantidade, foto_url=foto_url)
            db.session.add(novo_objeto)
            db.session.commit()

        print("Contagem de Objetos:", contagem_de_objetos)
        print("Foto enviada para Cloudinary:", foto_url)

    return redirect('/')




@app.route('/adicionar_produtos', methods=['POST'])
def adicionar_produtos():
    nome = request.form['nome']
    quantidade = request.form['quantidade']
    foto_url = request.form['foto_url']

    ObjetoContado = ObjetoContado.query.filter_by(nome=nome).first()
    if ObjetoContado:
        flash("Produto já existente!")
        return redirect(url_for('/'))

    novo_produto = ObjetoContado(nome=nome, quantidade=quantidade, foto_url=foto_url)
    db.session.add(novo_produto)
    db.session.commit()
    return redirect(url_for('/'))

@app.route('/admin')
def admin():
    objetos = ObjetoContado.query.all()
    return render_template('admin.html', objetos=objetos)

if __name__ == '__main__':
    app.run(debug=True)
