
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect('/')
        else:
           return 'Invalid username or password'
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()       
        return redirect('/login')
    return render_template('register.html')




@app.route('/', methods=['POST', 'GET'])
def index():

 if 'user_id' in session:
        # User is logged in
        user = User.query.get(session['user_id'])
        if request.method=='POST':
         task_content =request.form['content']
         if task_content.strip():  # Check if content is not empty or only whitespace
            new_task = Todo(content=task_content, user_id=user.id)  # Associate todo with user            
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return "There was an error adding your Task"
         else:
            return "Task content cannot be empty"
        else:
          tasks = Todo.query.filter_by(user_id=user.id).order_by(Todo.date_created).all()
          return render_template('index.html', tasks=tasks, user=user)
      


 else:
        return render_template('welcome.html')
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete= Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting the task'


@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    task=Todo.query.get_or_404(id)
    if request.method =='POST':
      task_content= request.form['content']
      try:
          task.content=task_content
          db.session.commit()
          return redirect('/')
      except:
          return "Sorry"
    else:
        return render_template('update.html', task=task)
 


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')


