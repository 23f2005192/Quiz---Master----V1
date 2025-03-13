from flask import Flask,redirect,render_template,url_for,request,session,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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
    usr=db.relationship("Scores",back_populates="sc")
    tid=db.relationship('Subject',back_populates='teacher')
    enrollid = db.relationship("Enrollment", back_populates="std")
    res=db.relationship("Response",back_populates="uid")
    done1=db.relationship("Attempt", back_populates="si")
    
    
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
    res=db.relationship("Response",back_populates="q")
    
    
    quizz = db.relationship("Scores", back_populates="sco")
    done1=db.relationship("Attempt", back_populates="qi")

class Question(db.Model):
    __tablename__="question"
    id=db.Column(db.Integer,db.Sequence("q"),primary_key=True)
    qid=db.Column(db.Integer,db.ForeignKey("quiz.id"))
    description=db.Column(db.String(100),nullable=False)
    marks=db.Column(db.Integer,nullable=False)
    quiz=db.relationship("Quiz",back_populates="qui")
    options = db.relationship("Option", back_populates="question")
    done1=db.relationship("Attempt", back_populates="quest")
class Option(db.Model):
    __tablename__="option"
    
    id=db.Column(db.Integer,db.Sequence("option_id_seq"),primary_key=True)
    desc=db.Column(db.String(100),nullable=False)

    qid=db.Column(db.Integer,db.ForeignKey("question.id"))
    flag=db.Column(db.Boolean)
   
    question = db.relationship("Question", back_populates="options") 
    done1=db.relationship("Attempt", back_populates="oid")
class Enrollment(db.Model):
    __tablename__ = "enrollment"
    id=db.Column(db.Integer,db.Sequence("enrollment_id_seq"),primary_key=True)
   
    sid = db.Column(db.Integer, db.ForeignKey("user.id")) 
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))  
  
    std = db.relationship("User", back_populates="enrollid")
    subject = db.relationship("Subject", back_populates="enrollsub")
class Response(db.Model):
    __tablename__="response"
    id=db.Column(db.Integer,db.Sequence("user_id_seq"),primary_key=True)
    userid=db.Column(db.Integer,db.ForeignKey('user.id'))
    qid=db.Column(db.Integer,db.ForeignKey("quiz.id"))
    time=db.Column(db.Time)
    q=db.relationship("Quiz",back_populates="res")
    uid=db.relationship("User",back_populates="res")
    attempts = db.relationship("Attempt", back_populates="response")
class Attempt(db.Model):
    __tablename__="attempt"
    id=db.Column(db.Integer,db.Sequence("user_id_seq"),primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey("user.id")) 
    qid=db.Column(db.Integer,db.ForeignKey("quiz.id"))
    question_id=db.Column(db.Integer,db.ForeignKey("question.id"))
    option_id=db.Column(db.Integer,db.ForeignKey("option.id"))
    response_id = db.Column(db.Integer, db.ForeignKey("response.id")) 
    si = db.relationship("User", back_populates="done1")
    qi=db.relationship("Quiz", back_populates="done1")
    quest=db.relationship("Question", back_populates="done1")
    oid=db.relationship("Option", back_populates="done1")
    response = db.relationship("Response", back_populates="attempts")
    
class Scores(db.Model):
    __tablename__='score'
    id=db.Column(db.Integer,db.Sequence("Score"),primary_key=True)
    qid=db.Column(db.Integer,db.ForeignKey("quiz.id"))
    userid=db.Column(db.Integer,db.ForeignKey('user.id'))
   
    score=db.Column(db.Integer)
    maxscore=db.Column(db.Integer)
    sc=db.relationship("User",back_populates="usr")
    sco=db.relationship('Quiz',back_populates="quizz")



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
    subject = Subject.query.filter_by(teacher_id=userid).all()
    quizzes = Quiz.query.filter_by(aid=userid).all()

    return render_template('quiz.html', teacher=user, quiz=quizzes, chapters=chapters, chapter_id=chapter_id,subject=subject)


@app.route('/quiz/<int:quiz_id>/questions')
def questions(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    '''if not quiz:
        return "Quiz not found", 404'''#checking for redirection 

    questions = Question.query.filter_by(qid=quiz_id).all()
  

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
    scores = db.session.query(Scores, User).join(User).filter(Scores.qid == quiz_id).all()

    
    response_data = []
    for score, user in scores:
        response_data.append({
            'student_id': user.id,
            'name': user.name,
            'score': score.score,
            'max_score': score.maxscore
        })

    
    return render_template('response.html', responses=response_data)
@app.route('/quiz/<quiz_id>/response', methods=['GET', 'POST'])
def response(quiz_id):
    student_id = session.get('user_id') 
    scores = db.session.query(Scores, User).join(User).filter(Scores.qid == quiz_id, Scores.userid == student_id).all()

    
    response_data = []
    for score, user in scores:
        response_data.append({
            'student_id': user.id,
            'name': user.name,
            'score': score.score,
            'max_score': score.maxscore
        })

    
    return render_template('response.html', responses=response_data)

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
    
   
    quizzes = Quiz.query.filter(Quiz.cid == subject_id, Quiz.startdate <= today , Quiz.enddate>=today).all()
    
    return render_template('upcooming.html', quiz=quizzes, subject_id=subject_id)

@app.route('/quiz/<int:quiz_id>/start_quiz', methods=['GET', 'POST'])
def start_quiz(quiz_id):
    
    student_id = session.get('user_id')  
    
    if student_id is None:
        return redirect(url_for('login'))  
  
    quiz = Quiz.query.get_or_404(quiz_id)

   
    if request.method == 'POST':
        current_time = datetime.now().time()

      
        response = Response(
            userid=student_id,  
            qid=quiz_id, 
            time=current_time  
        )

       
        db.session.add(response)
        db.session.commit()

       
        return redirect(url_for('take_quiz', quiz_id=quiz_id,response_id=response.id))

    
    return render_template('start.html', quiz=quiz, student_id=student_id)


   
@app.route("/take_quiz/<int:quiz_id>/<int:response_id>", methods=["GET", "POST"])
def take_quiz(quiz_id,response_id ):
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    
    questions = Question.query.filter_by(qid=quiz_id).all()
    
   
    student_id = session.get('user_id')   

    if request.method == "POST":
   
        for question in questions:
            option_id = request.form.get(str(question.id))  

           
            if option_id:
                new_attempt = Attempt(
                    sid=student_id,  
                    qid=quiz.id,  
                    question_id=question.id,  
                    option_id=option_id,  
                    response_id=response_id 
                )
                db.session.add(new_attempt)

        db.session.commit()
        return redirect(url_for('quiz_result', quiz_id=quiz_id,student_id=student_id))  

    return render_template("attempt.html", quiz=quiz, questions=questions)


 
@app.route('/quiz_result/<int:quiz_id>/<int:student_id>', methods=['GET'])
def quiz_result(quiz_id, student_id):
    quiz = Quiz.query.get(quiz_id) 
    questions = Question.query.filter_by(qid=quiz_id).all()  

    total_score = 0
    max_score = 0

     

    for question in questions:
      
        attempt = Attempt.query.filter_by(qid=quiz_id, sid=student_id, question_id=question.id).order_by(Attempt.id.desc()).first()

        if attempt:
          
            correct_option = Option.query.filter_by(qid=question.id, flag=True).first()
            if attempt.option_id == correct_option.id:  
                total_score += question.marks
        
        max_score += question.marks  
   
    score_entry = Scores(
        qid=quiz_id,
        userid=student_id,
        
        score=total_score,
        maxscore=max_score
    )
    db.session.add(score_entry)
    db.session.commit()  

    return render_template('score.html', quiz=quiz, total_score=total_score, max_score=max_score, student_id=student_id)


@app.route("/edit_option")
def edit_option(ID):
        return "HI"
@app.route("/delete_option/<int:question_id>/<int:option_id>/<int:quiz_id>",methods=['GET','POST'])
def delete_option(question_id, option_id, quiz_id):
    if request.method == 'POST':
        option_to_delete = Option.query.get(option_id)
        
        if option_to_delete:
            db.session.delete(option_to_delete)
            db.session.commit()
            flash("Option deleted successfully!", "success")
        else:
            flash("Option not found!", "error")

        return redirect(url_for('questions', quiz_id=quiz_id))

    quiz = Quiz.query.get(quiz_id)
    question = Question.query.get(question_id)
    
    if not quiz or not question:
        flash("Quiz or Question not found!", "error")
        return redirect(url_for('quiz_list'))
    
    return render_template('delop.html', quiz=quiz, question=question,quiz_id=quiz_id)
    
@app.route("/edit_question/<int:quiz_id>/<int:question_id>",methods=['GET','POST'])
def edit_question(quiz_id, question_id):
    if request.method == 'POST':
        question_to_edit = Question.query.get(question_id)
        
        if question_to_edit:
            
            new_description = request.form.get('description')
            new_marks = request.form.get('marks')
            
            
            question_to_edit.description = new_description
            question_to_edit.marks = int(new_marks)  
            
          
            db.session.commit()
            
            flash("Question edited successfully!", "success")
            
           
            return redirect(url_for('questions', quiz_id=quiz_id))
        else:
            flash("Question not found!", "danger")
            return redirect(url_for('questions', quiz_id=quiz_id))

   
    quiz = Quiz.query.get(quiz_id)
    question = Question.query.get(question_id)
    return render_template('editq.html', quiz=quiz, question=question)
        
@app.route('/delete_question/<int:quiz_id>/<int:question_id>', methods=['GET', 'POST'])
def delete_question(quiz_id, question_id):
   
    if request.method == 'POST':
        
        question_to_delete = Question.query.get(question_id)
        if question_to_delete:
            db.session.delete(question_to_delete)
            db.session.commit()
            flash("Question deleted successfully!", "success")
            return redirect(url_for('questions', quiz_id=quiz_id))  
        
  
    quiz = Quiz.query.get(quiz_id)
    question = Question.query.get(question_id)
    return render_template('delq.html', quiz=quiz, question=question)
    

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
        return redirect(url_for('questions', quiz_id=question.qid))
    return render_template('addoption.html', question=question)
@app.route('/teacher/enrolled_students/<int:teacher_id>')
def enrolled_students(teacher_id):
    teacher = User.query.get(teacher_id)
    if not teacher:
        flash("Teacher not found!", "danger")
        return redirect(url_for('login')) 
    
    subjects = Subject.query.filter_by(teacher_id=teacher.id).all()

    students = []
    for subject in subjects:
        for enrollment in subject.enrollsub:
            student = User.query.get(enrollment.sid)
            students.append(student)
    
    return render_template('enrolled.html', teacher=teacher, students=students)
@app.route('/pastquiz/<int:subject_id>', methods=['GET', 'POST'])
def pastquiz(subject_id):
    today = datetime.today().date()
    
   
    quizzes = Quiz.query.filter(Quiz.cid == subject_id, Quiz.startdate < today).all()
    
    return render_template('pastq.html', quiz=quizzes, subject_id=subject_id)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    teacher = User.query.get(session['user_id'])  
    subjects = teacher.tid

    query = request.args.get('query', '')

  
    students = User.query.filter(User.name.ilike(f'%{query}%')).all() if query else []
    subjects_search = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all() if query else []
    quizzes = Quiz.query.filter(Quiz.name.ilike(f'%{query}%')).all() if query else []

    return render_template('teacher.html', teacher=teacher, subjects=subjects, 
                           students=students, subjects_search=subjects_search, quizzes=quizzes)


@app.route('/teacher_scores')
def teacher_scores():
        # Query to fetch subject names, max scores and teacher names
        subjects_data = db.session.query(
            Subject.name.label("subject_name"),
            User.name.label("teacher_name"),
            func.max(Scores.score).label("max_score")
        ).join(User, User.id == Subject.teacher_id) \
        .join(Quiz, Quiz.cid == Subject.id) \
        .join(Scores, Scores.qid == Quiz.id) \
        .group_by(Subject.id, User.id).all()

        # Preparing data for Chart.js
        subject_names = [subject.subject_name for subject in subjects_data]
        teacher_names = [subject.teacher_name for subject in subjects_data]
        max_scores = [subject.max_score for subject in subjects_data]

        return render_template('scores.html', 
                            subject_names=subject_names,
                            teacher_names=teacher_names,
                            max_scores=max_scores)

if __name__ == "__main__":
    app.run(debug=True)







   
    
   
   
    





with app.app_context():
   

  
  
   db.create_all()


if __name__=='__main__':
      app.run(debug=True)