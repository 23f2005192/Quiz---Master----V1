from flask import Flask,redirect,render_template,url_for,request,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import secrets
sk=secrets.token_hex(16)
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/python/project/quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key=sk
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'check_same_thread': False  
    }
}

db=SQLAlchemy(app)
class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer,db.Sequence("user_id_seq"),primary_key=True)
    type=db.Column(db.String(20))
    name=db.Column(db.String(50))
    username=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    qualification=db.Column(db.String(50))
    dob=db.Column(db.Date,nullable=False)
    usri=db.relationship("Quiz",back_populates="tid")
    #usr=relationship("Scores",back_populates="sc")
    tid=db.relationship('Subject',back_populates='teacher')
class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, db.Sequence("subject_id_seq"), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    
    
    teacher=db.relationship('User',back_populates='tid')
    chapters=db.relationship('Chapter',back_populates='subject')
class Chapter(db.Model):
    __tablename__="chapter"
    id=db.Column(db.Integer,db.Sequence("chapter_id"),primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    description=db.Column(db.String(100))
    quizs = db.relationship("Quiz", back_populates="chapter")

    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    subject = db.relationship("Subject", back_populates="chapters")
class Quiz(db.Model):
    __tablename__="quiz"
    id=db.Column(db.Integer,db.Sequence("qid"),primary_key=True)
    cid=db.Column(db.Integer,db.ForeignKey("chapter.id"))
    aid=db.Column(db.Integer,db.ForeignKey("user.id"))
    name=db.Column(db.String,nullable=False)
    description=db.Column(db.String)
    startdate=db.Column(db.Date,nullable=False)
    enddate=db.Column(db.Date)
    dur=db.Column(db.Time)
   
    chapter = db.relationship("Chapter", back_populates="quizs")
    tid=db.relationship("User",back_populates="usri")
    
   # qui = db.relationship("Question", back_populates="quiz") 
   # quizz = db.relationship("Scores", back_populates="quizz")


    
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form['name']
        type=request.form['type']
        username=request.form['username']
        password = request.form['password']
        qualification = request.form['qualification']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d')
        user = User.query.filter_by(username=username).first()
        if user :
              emsg='User name already exists'
              return render_template('register.html', error=emsg, name=name, type=type, username=username, qualification=qualification, dob=dob)
              
            
        
        det=User( type=type,
                 name=name,
            username=username,
            password=password,
            qualification=qualification,
            dob=dob)
        db.session.add(det)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password==password:
            session['user_id']=user.id
            
            if 'user_id' not in session or session['user_id'] != user.id:
                   return redirect(url_for('login'))
            if user.type=='teacher':
                  return redirect(url_for('teacher', user_id=user.id))
            elif user.type=='student':
                 return redirect(url_for('student', user_id=user.id))
                
        emsg='Invalid user name or password'
        return render_template('login.html',error=emsg)
    return render_template('login.html')
@app.route('/')
def home():
    return "Welcome to home page "
@app.route('/teacher/<int:user_id>')
def teacher(user_id):
    usr=User.query.get(user_id)
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))  
    subjects=Subject.query.filter_by(teacher_id=user_id).all()
    
    
    
    return render_template('teacher.html',teacher=usr,subjects=subjects)
@app.route('/student/<int:user_id>')
def student(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))  
    usr=User.query.get(user_id)
  
    
    return render_template('student.html',student=usr)
@app.route('/addsubject', methods=['GET', 'POST'])
def addsubject():
    if 'user_id' not in session:
        return redirect(url_for('login'))  
    user = User.query.get(session['user_id'])
    
    if user.type != 'teacher':
        return redirect(url_for('home')) 

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        try:
            new_subject = Subject(name=name, description=description,teacher_id=user.id)
            db.session.add(new_subject)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return "Error has occured {e}"
       
        return redirect(url_for('teacher', user_id=user.id))

    return render_template('newsubject.html')
@app.route('/teacher/<int:user_id>/subject/<int:subject_id>/addchapter',methods=['GET','POST'])
def addchapter(subject_id,user_id):
    user=User.query.get(user_id)
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))
    sub=Subject.query.get(subject_id)
    if sub is None or sub.teacher_id!=user_id:
        return redirect(url_for('teacher',user_id=user_id))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('teacher',user_id=user_id))
    return render_template('nechapter.html',subject=sub)
@app.route('/teacher/<int:userid>/new_quiz', methods=['GET', 'POST'])
def new_quiz(userid):
    user = User.query.get(userid)
    if 'user_id' not in session or session['user_id'] != userid:
        return redirect(url_for('login'))

    chapter_id = request.args.get('chapter_id') 
    chapters = Chapter.query.filter_by(subject_id=chapter_id).all()  
    quizzes = Quiz.query.filter_by(aid=userid).all()


    return render_template('quiz.html', teacher=user, quiz=quizzes, chapters=chapters, chapter_id=chapter_id)





@app.route('/teacher/<int:userid>/new_quiz/add', methods=['GET', 'POST'])
def add_quiz(userid):
    user = User.query.get(userid)
    if 'user_id' not in session or session['user_id'] != userid:
        return redirect(url_for('login'))

    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        quiz_name = request.form['name']
        description = request.form['description']
        start_date = datetime.strptime(request.form['startdate'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['enddate'], '%Y-%m-%d') if request.form['enddate'] else None
        duration = request.form['duration'] 
        try:
            ob=datetime.strptime(duration,'%H:%M').time()
        except:
            return "error "

        new_quiz = Quiz(
            name=quiz_name,
            description=description,
            startdate=start_date,
            enddate=end_date,
            dur=ob,
            cid=chapter_id,
            aid=userid
        )
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for('new_quiz', userid=userid))

   
    chapters = Chapter.query.filter_by(subject_id=userid).all()
    return render_template('newquiz.html', teacher=user, chapters=chapters)
@app.route('/quiz/<quiz_id>/add_question', methods=['GET', 'POST'])
def add_question(quiz_id):
    return "HI"
@app.route('/quiz/<quiz_id>/view_responses', methods=['GET', 'POST'])
def view_responses(quiz_id):
    return "HI"

@app.route('/quiz/<int:quiz_id>/delete', methods=['GET', 'POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if quiz is None:
        return "Quiz not found", 404

    if request.method == 'POST':
        confirm = request.form.get('confirm')

        if confirm is None:
            return "Error: No confirmation selected. Please choose 'Yes' or 'No'.", 400

        if confirm == 'yes':
            db.session.delete(quiz)
            db.session.commit()
            return redirect(url_for('new_quiz', userid=quiz.aid))

        return redirect(url_for('new_quiz', userid=quiz.aid))  

    return render_template('delete.html', quiz=quiz)






    
    
    


    
with app.app_context():
   
    
    
   
    db.create_all()


if __name__=='__main__':
      app.run(debug=True)