from flask import Flask, render_template, url_for, request , redirect, make_response, session
import sqlalchemy as db
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)
dbEngine = db.create_engine("sqlite:///database.db/")
# dbConn = dbEngine.connect()
# metadata = db.MetaData() # supply metadata that holds the details of the structure of the database
# access existing table
# flashcardsTable = db.Table(
#     "flashcards", 
#     metadata,
#     autoload_with=dbEngine
# )

# database model class (inherits from DeclarativeBase)
# SQLAlchemy will be able to recognise Python classes as database models that 
# can interact with the database directly by manipulating tables and data

Session = sessionmaker(bind=dbEngine) # create a new database connection session using the sessionmaker object
dbSession = Session() # "Session" is callable btw

Base = declarative_base() # base class for database models
class Flashcard(Base):
    __tablename__ = "Flashcards"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False)
    body = db.Column(db.String(), nullable=False)
    
# automatically register all tables to the database if they don't yet exist
Base.metadata.create_all(dbEngine) 

@app.route("/create", methods=["POST", "GET"])
def createFlashcard():
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")
        if title and body:
            newFlashcard = Flashcard(title=title, body=body)
            dbSession.add(newFlashcard)
            dbSession.commit()
            return redirect(url_for("viewFlashcards", msgType=0, statusMsg=f"Successfully created flashcard '{title}'"))
        else:
            return render_template("create.html", isValid=False, callbackMsg=f"Failed to create flashcard. Please make sure to enter a title and body of the flashcard")

    return render_template("create.html", isValid=False, callbackMsg=None)


@app.route("/edit", methods=["POST", "GET"])
def editFlashcard():
    return render_template("edit.html")


@app.route("/delete/<id>", methods=["POST", "GET"])
def deleteFlashcard(id=None):
    if id == None:
        # get the url to the viewFlashcards function (aka an endpoint)
        return redirect(url_for("viewFlashcards", msgType=-1, statusMsg="Please select a flashcard to remove"))

    # queries the flashcard to delete and deletes that
    flashcard = dbSession.query(Flashcard).filter_by(id=id).first()
    
    if flashcard:
        dbSession.delete(flashcard)
        dbSession.commit()
    else:
        return redirect(url_for("viewFlashcards", msgType=-1, statusMsg=f"Deletion failed - that flashcard does not exist."))    

    return redirect(url_for("viewFlashcards", msgType=0, statusMsg=f"Successfully removed flashcard '{flashcard.title}'"))

@app.route("/")
def viewFlashcards():
    flashcards = dbSession.query(Flashcard).all()
    statusMsg = request.args.get("statusMsg", "")
    msgType = int(request.args.get("msgType", 0))
    return render_template("flashcards.html", flashcards=flashcards, msgType=msgType, statusMsg=statusMsg)

if __name__ == "__main__":
    app.run(debug=True)