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
    enrollid = db.relationship("Enrollment", back_populates="std")
class Subject(db.Model):
    __tablename__ = "subject"
    id = db.Column(db.Integer, db.Sequence("subject_id_seq"), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    
    
    teacher=db.relationship('User',back_populates='tid')
    chapters=db.relationship('Chapter',back_populates='subject')
    enrollsub = db.relationship("Enrollment", back_populates="subject")
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
    
    qui = db.relationship("Question", back_populates="quiz")
    
   # quizz = db.relationship("Scores", back_populates="quizz")

class Question(db.Model):
    __tablename__="question"
    id=db.Column(db.Integer,db.Sequence("q"),primary_key=True)
    qid=db.Column(db.Integer,db.ForeignKey("quiz.id"))
    description=db.Column(db.String(100),nullable=False)
    marks=db.Column(db.Integer,nullable=False)
    quiz=db.relationship("Quiz",back_populates="qui")
    options = db.relationship("Option", back_populates="question")
    
class Option(db.Model):
    __tablename__="option"
    
    id=db.Column(db.Integer,db.Sequence("option_id_seq"),primary_key=True)
    desc=db.Column(db.String(100),nullable=False)

    qid=db.Column(db.Integer,db.ForeignKey("question.id"))
    flag=db.Column(db.Boolean)
   
    question = db.relationship("Question", back_populates="options") 
class Enrollment(db.Model):
    __tablename__ = "enrollment"
    id=db.Column(db.Integer,db.Sequence("enrollment_id_seq"),primary_key=True)
   
    sid = db.Column(db.Integer, db.ForeignKey("user.id")) 
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))  
  
    std = db.relationship("User", back_populates="enrollid")
    subject = db.relationship("Subject", back_populates="enrollsub")
    
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
    usr = User.query.get(user_id)

  
    enrolled_subjects = Enrollment.query.filter_by(sid=user_id).all()

    subjects = []
    for enrollment in enrolled_subjects:
        subject = Subject.query.get(enrollment.subject_id)
        subjects.append(subject)

    return render_template('student.html', student=usr, subjects=subjects)  

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


@app.route('/quiz/<int:quiz_id>/questions')
def questions(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "Quiz not found", 404

    questions = Question.query.filter_by(qid=quiz_id).all()
    '''if not questions:
        print(f"No questions found for quiz_id {quiz_id}")
        return "Error loading questions", 500'''

    user = User.query.get(quiz.aid)

    return render_template('question.html', quiz=quiz, questions=questions, user=user)







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

   
    subject = Subject.query.filter_by(teacher_id=userid).all()
    return render_template('newquiz.html', teacher=user, chapters=subject)
@app.route('/quiz/<quiz_id>/add_question', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "Quiz not found", 404

    if request.method == 'POST':
        description = request.form['description']
        marks = request.form['marks']
        
        new_question = Question(
            qid=quiz.id,
            description=description,
            marks=marks
        )

        db.session.add(new_question)
        db.session.commit()

        return redirect(url_for('questions', quiz_id=quiz.id)) 

    return render_template('newq.html', quiz_id=quiz_id)



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

        if confirm == 'yes':
          
            db.session.delete(quiz)
            db.session.commit()
            return redirect(url_for('new_quiz', userid=quiz.aid))

        
        return redirect(url_for('new_quiz', userid=quiz.aid))

   
    return render_template('delete.html', quiz=quiz)
@app.route('/addsub', methods=['GET', 'POST'])
def addsub():
    if 'user_id' not in session:
        return redirect(url_for('login'))  
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        subject_id = request.form['name']  
        
        try:
            
            subject = Subject.query.filter_by(id=int(subject_id)).first()

            if not subject:
                return "Subject not found"  

          
            existing_enrollment = Enrollment.query.filter_by(sid=user.id, subject_id=subject.id).first()
            if existing_enrollment:
                return "You are already enrolled in this subject."

          
            new_enrollment = Enrollment(sid=user.id, subject_id=subject.id)
            db.session.add(new_enrollment)
            db.session.commit()

            return redirect(url_for('student', user_id=user.id))  

        except Exception as e:
            return f"Error occurred: {e}"

    return render_template('newsub.html')  
@app.route('/quiz/<int:subject_id>', methods=['GET', 'POST'])
def quiz(subject_id):
    today = datetime.today().date()
    
   
    quizzes = Quiz.query.filter(Quiz.cid == subject_id, Quiz.startdate >= today).all()
    
    return render_template('upcooming.html', quiz=quizzes, subject_id=subject_id)
@app.route('/attempt')
def attempt(id):
    return "HI"
@app.route("/edit_option")
def edit_option(ID):
        return "HI"
@app.route("/delete_option")
def delete_option(id):
    return "HI"
@app.route("/edit_question")
def edit_question(ID):
        return "HI"
@app.route('/delete_question/<int:quiz_id>/<int:question_id>', methods=['GET', 'POST'])
def delete_question(quiz_id, question_id):
   
   "return HI"
    

@app.route('/add_option/<int:question_id>', methods=['GET', 'POST'])
def add_option(question_id):
   
    question = Question.query.get(question_id)
    
    
    if request.method == 'POST':
        option_desc = request.form.get('option_desc')
        flag = request.form.get('flag') == 'on' 
        
       
        new_option = Option(
            desc=option_desc,
            qid=question.id,
            flag=flag
        )
        
        
        db.session.add(new_option)
        db.session.commit()
        return redirect(url_for('questions', quiz_id=question.id))
    return render_template('addoption.html', question=question)


   
    
   
   
    





with app.app_context():
   

 
    
   db.create_all()


if __name__=='__main__':
      app.run(debug=True)