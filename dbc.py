from sqlalchemy import Column,Integer,String,ForeignKey,Sequence,create_engine,Date,Time,Boolean
from sqlalchemy.orm import sessionmaker,relationship,declarative_base

engine=create_engine("sqlite:///quiz.db")
Session=sessionmaker(bind=engine)
s=Session()
Base=declarative_base()
class User(Base):
    __tablename__="user"
    id=Column(Integer,Sequence("user_id_seq"),primary_key=True)
    type=Column(String(20))
    name=Column(String(50))
    username=Column(String(50),unique=True,nullable=False)
    password=Column(String(50),nullable=False)
    qualification=Column(String(50))
    dob=Column(Date,nullable=False)
    #usri=relationship("Quiz",back_populates="tid")
    usr=relationship("Scores",back_populates="sc")
    tid=relationship('Subject',back_populates='teacher')
    enrollid = relationship("Enrollment", back_populates="std")
    
    
class Subject(Base):
    __tablename__ = "subject"
    id = Column(Integer, Sequence("subject_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(100))
    chapters = relationship("Chapter", back_populates="subject")
    teacher_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    
    teacher=relationship('User',back_populates='tid')
    chapters=relationship('Chapter',back_populates='subject')
    enrollsub = relationship("Enrollment", back_populates="subject")
class Chapter(Base):
    __tablename__="chapter"
    id=Column(Integer,Sequence("chapter_id"),primary_key=True)
    name=Column(String(50),nullable=False)
    description=Column(String(100))
    chapters=relationship("Quiz",back_populates="quizs")
    subject_id = Column(Integer, ForeignKey("subject.id"))
    subject = relationship("Subject", back_populates="subject")

class Quiz(Base):
    __tablename__="quiz"
    id=Column(Integer,Sequence("qid"),primary_key=True)
    cid=Column(Integer,ForeignKey("chapter.id"))
    aid=Column(Integer,ForeignKey("user.id"))
    name=Column(String,nullable=False)
    description=Column(String)
    startdate=Column(Date,nullable=False)
    enddate=Column(Date)
    dur=Column(Time)
    chapter = relationship("Chapter", back_populates="chapter")  
    qui = relationship("Question", back_populates="quiz") 
    quizz = relationship("Scores", back_populates="quizz")
    tid=relationship("User",back_populates="usri")
    
class Question(Base):
    __tablename__="question"
    id=Column(Integer,Sequence("q"),primary_key=True)
    qid=Column(Integer,ForeignKey("quiz.id"))
    description=Column(String(100),nullable=False)
    marks=Column(Integer,nullable=False)
    quiz=relationship("Question",back_populates="qui")
    tid=relationship("User",back_populates='usri')
class Scores(Base):
    __tablename__='score'
    id=Column(Integer,Sequence("Score"),primary_key=True)
    qid=Column(Integer,ForeignKey("quiz.id"))
    userid=Column(Integer,ForeignKey('user.id'))
    attempt=Column(Integer,nullable=False)
    score=Column(Integer)
    maxscore=Column(Integer)
    sc=relationship("User",back_populates="usr")
    sco=relationship('Quiz',back_populates="quizz")
class Response(Base):
    __tablename__="response"
    id=Column(Integer,Sequence("user_id_seq"),primary_key=True)
    userid=Column(Integer,ForeignKey('user.id'))
    opid=Column(Integer,ForeignKey("option.opid"))
    time=Column(Time)
class Option(Base):
    __tablename__="option"
    
    id=Column(Integer,Sequence("option_id_seq"),primary_key=True)
    desc=Column(String(100),nullable=False)
    qid=Column(Integer,ForeignKey("quiz.id"))
    flag=Column(Boolean)
    quiz = relationship("Quiz", back_populates="options")
class Enrollment(Base):
    __tablename__ = "enrollment"
    id=Column(Integer,Sequence("enrollment_id_seq"),primary_key=True)
   
    sid = Column(Integer, ForeignKey("user.id")) 
    subject_id = Column(Integer, ForeignKey("subject.id"))  
  
    std = relationship("User", back_populates="enrollid")
    subject = relationship("Subject", back_populates="enrollsub")
 


Base.metadata.create_all(engine)

s.commit()

    
    
    
Base.metadata.create_all(engine)


s.commit()