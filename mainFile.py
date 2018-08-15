#graphics1.py
#Austin Teshuba ICS3U 
#this is a tutoring app made for a grade 11
#overall this is like a forum made just for tutoring featuring cloud connection, asynchronous loading, object oriented design, and the ability to replort, like, post, reply , and view objects

from __future__ import absolute_import
from pygame import * #all graphics programs will need this
from firebase import firebase
import tkMessageBox
import tkFileDialog
from Tkinter import *
from google.cloud import storage#finish cloud upload
from enum import Enum
import os
from io import *
from urllib2 import urlopen
import urllib2
import cStringIO
import time as t
import threading
from oauth2client.client import GoogleCredentials
import requests

init()
root = Tk()#init pygame
root.withdraw()
print(t.time())
    #r   g b
RED  =(255,0,0) #tuple - a list that can not be changed!
GREEN=(0,255,0)
BLUE= (0,0,255)
BLACK=(0,0,0)
WHITE=(255,255,255)#declare colors
MYYELLOW=(204,224,90)
BUTTONCOLOR=(190,237,170)
CLICKEDBUTTONCOLOR=(213,255,217)


##move down

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Python27/ComputerScienceFSE-7ea9339e6f65.json"#os environment variables for google 
credentials = GoogleCredentials.get_application_default()
client = storage.Client()#this opens the cloud buckets for storage
profileBucket = client.get_bucket('profilepict')
verificationBucket = client.get_bucket("verificationpict")#open storage buckets to put things in
postBucket = client.get_bucket('postpict')
repliesBucket = client.get_bucket("replypict")#reply pictures

def uploadPhotoToFirebase(imageObject, pictype, idNumber=None, photoNumber=None):#this uploads to firebase
    global currentPerson #this just lets the function update the class instance
    if pictype == "verificationPic" and currentPerson.__class__.__name__=="Tutor":#check type of person/photo
        print("Verif")
        blob = verificationBucket.blob(currentPerson.username)#upload to blob
        blob.upload_from_filename(imageObject)
        downloadURL = blob.public_url#get url from blob
        currentPerson.verificationURL = downloadURL#give url to class
        path = "tutors/"+currentPerson.username
        firebase.put(path, "verificationURL", downloadURL)#put url in database
    elif pictype == "profilePic":
        print("profile")
        blob = profileBucket.blob(currentPerson.username)#upload to blob
        blob.upload_from_filename(imageObject)
        downloadURL = blob.public_url#get url from blob
        currentPerson.profileURL = downloadURL
        if currentPerson.__class__.__name__=="Tutor":#check type of person
            path = "tutors/"+currentPerson.username#put the url in the instance and put thgat in the databse
            firebase.put(path, "profileURL", downloadURL)
        elif currentPerson.__class__.__name__=="User":
            path = "users/"+currentPerson.username
            firebase.put(path, "profileURL", downloadURL)
        else:
            print("error! check ur code austin")
    elif pictype == "postPic":
        print("post")
        blob = postBucket.blob(str(idNumber)+","+str(photoNumber))#upload to blob
        blob.upload_from_filename(imageObject)
        downloadURL = blob.public_url
        return downloadURL#return public url
    elif pictype=="replyPic":
        print("reply")
        blob = repliesBucket.blob(str(idNumber)+","+str(photoNumber))#upload to blob
        blob.upload_from_filename(imageObject)
        downloadURL = blob.public_url
        return downloadURL#return public url
    
    else:
        print("Invalid arguments. Nothing happened.")
        
    
##end move down
font.init()#init font
fontString = "Helvetica" # this is the font I will be using throughout the program
welcomeFont = font.SysFont(fontString, 100)#declare fonts - all dofferent sizes
subtitleFont = font.SysFont(fontString, 50)
majorQuestionFont = font.SysFont(fontString, 75)
smallTitleFont = font.SysFont(fontString, 60)
largeButtonFont = font.SysFont(fontString, 40)
smallerFont = font.SysFont(fontString, 30)
minorFont = font.SysFont(fontString, 20)
size=(1280,800) #screen resolution
screen=display.set_mode(size)#creating a 800x600 window

#display.set_caption("My first graphics program")

running=True #boolean variable

myClock = time.Clock()#start a clock
fps=30#control the FPS here

screenNumber = 1 #this indicates which screen the user is starting from.

backgroundImage = transform.scale(image.load("background.jpg"), (1280,800))#background image

#firebase things
firebase = firebase.FirebaseApplication("https://computersciencefse.firebaseio.com/")#init firebase

#firebase.get(path, None) is the command to get
#firebase.post(path, key:value in dict form) is the command to post. uses random
#variable as parent
#firebase.put(path, key, value) doesnt create a random variable

leftArrowSurfaceRect = Rect(20,20,50,50)#left arrow image
leftArrow = transform.scale(image.load("leftArrow.png"), (leftArrowSurfaceRect.width, leftArrowSurfaceRect.height))#this is the back arrow

###button reset func
def buttonReset(rect, text, color = BUTTONCOLOR, surface = screen): #after a button is clicked
    draw.rect(surface, color, rect)
    screen.blit(text, (rect.x+rect.width/2-text.get_width()/2, rect.y+rect.height/2-text.get_height()/2))

    
#screen 1 variables
welcomeTextBlock = welcomeFont.render("Welcome", True, BLACK)#make the welcome text
welcomeTextBlockRect = Rect(size[0]/2 - welcomeTextBlock.get_width()/2, 250 - welcomeTextBlock.get_height(), welcomeTextBlock.get_width(), welcomeTextBlock.get_height())

questionTextBlock = subtitleFont.render("Are you a:", True, BLACK) # make the qeustion text
questionTextBlockRect = Rect(size[0]/2  - questionTextBlock.get_width()/2, welcomeTextBlockRect.y + welcomeTextBlock.get_height() +25, questionTextBlock.get_width(), questionTextBlock.get_height())

buttonWidth = (300,100)#width and height of buttons
buttonBuffer = 60 #distance between buttons
#button to make a tutor
tutorButtonRect = Rect((size[0]/2 - buttonWidth[0]/2, (size[1] - questionTextBlockRect.y - questionTextBlockRect.height)/2 - buttonBuffer/2 - buttonWidth[1] + questionTextBlockRect.y + questionTextBlockRect.height-buttonWidth[1]/2), buttonWidth)

personButtonRect = Rect((tutorButtonRect.x, tutorButtonRect.y + buttonBuffer/2 + tutorButtonRect.height), buttonWidth)    #this is the button to make a user
tutorTextBlock = largeButtonFont.render("Tutor", True, BLACK) # this is the text that goes on the tutor button
tutorTextBlockRect = (tutorButtonRect.x+tutorButtonRect.width/2-tutorTextBlock.get_width()/2, tutorButtonRect.y + tutorButtonRect.height/2 - tutorTextBlock.get_height()/2, tutorTextBlock.get_width(), tutorTextBlock.get_height())

studentTextBlock = largeButtonFont.render("Student", True, BLACK) # this is the text that goes on the student button
studentTextBlockRect = (personButtonRect.x+personButtonRect.width/2-studentTextBlock.get_width()/2, personButtonRect.y + personButtonRect.height/2 - studentTextBlock.get_height()/2, studentTextBlock.get_width(), studentTextBlock.get_height())


logInButtonRect = Rect(personButtonRect.x, personButtonRect.y + buttonWidth[1] + buttonBuffer/2, buttonWidth[0], buttonWidth[1])#button to log in
logInTextBlock = largeButtonFont.render("Existing User", True, BLACK)

questionMark = transform.scale(image.load("questionMark.png"), (50,50))#instructions button
questionMarkRect = Rect(20,size[1]-70, 50,50)

toTutor = False
toStudent=False#destinations controlled by flag variables
toLogIn = False
#grabs all Users and tutors in the database, except if database is null
try:
    existingUsers = [str(x) for x in firebase.get("/users", None).keys()]#get existing users and tutors. if the result is none, therte are no people therfore empty array
except:
    existingUsers = []
try:
    existingTutors = [str(x) for x in firebase.get("/tutors", None).keys()]
except:
    existingTutors = []
print(existingUsers, existingTutors)
#initialize the first screen
tutorObjects=[]
tutorObjectsRetrieved=[]
def getTutorObjects():#grabs all tutors from database
    def do():#define function for async
        global existingTutors
        global tutorObjects
        global tutorObjectsRetrieved
        for name in existingTutors:#if the name is already in tutors and not retrieved
            if name not in tutorObjectsRetrieved: 
                username = name
                password = str(firebase.get("tutors/"+name, "password"))#all of these gets populate an instance of tutor
                profileURL = str(firebase.get("tutors/"+name, "profileURL"))
                verified = str(firebase.get("tutors/"+name, "verified"))
                subjectDictionary = firebase.get("tutors/"+name+"/subjects", None)#grabs each thing from the tutor database
                tempDict = dict()
                for item in subjectDictionary.keys():
                    tempDict[str(item)] = subjectDictionary[item]
                verificationURL = str(firebase.get("tutors/"+name, "verificationURL"))
                tutorObjects.append(Tutor(username, password, tempDict, profileURL, verificationURL, verified))#adds to tutor objects array
                tutorObjectsRetrieved.append(name)
        print(tutorObjects)
    a_thread = threading.Thread(target=do)#does the above function asynchronously
    a_thread.start()
    return a_thread
    

tutorThread = getTutorObjects()#this populates all class instances asynchronously and puts in list
def startFirstScreen():
    global screenNumber # use the global vwersion of this
    screenNumber = 1 #sets the current screen property to screen 1
    screen.blit(backgroundImage, (0,0))
    screen.blit(welcomeTextBlock, (welcomeTextBlockRect.x, welcomeTextBlockRect.y))
    screen.blit(questionTextBlock, (questionTextBlockRect.x, questionTextBlockRect.y))

    #button
    draw.rect(screen, BUTTONCOLOR, tutorButtonRect)#these are the buttons for tutor user and log in
    draw.rect(screen, BUTTONCOLOR, personButtonRect)
    draw.rect(screen, BUTTONCOLOR, logInButtonRect)

    #text
    screen.blit(tutorTextBlock, tutorTextBlockRect)
    screen.blit(studentTextBlock, studentTextBlockRect)#text for buttons
    buttonReset(logInButtonRect, logInTextBlock)

    screen.blit(questionMark, questionMarkRect)

#Instructions screen
instructionsScreenTitle = welcomeFont.render("Instructions", True, BLACK)
instructionsScreenRect = Rect(size[0]/2-instructionsScreenTitle.get_width()/2, instructionsScreenTitle.get_height()+5, instructionsScreenTitle.get_width(), instructionsScreenTitle.get_height())

instructionsBody = """
This is an app all about tutoring and bettering yourself. Register as a tutor or as a student and start to get answers to your burning questions. Post by pressing the plus sign in the upper right at the home page. Press on the title of a post to see it in its entirity. Press on the reply titles inside of that view to see the replies in their entirety. Press on photos to download them to further review. Like objects by pressing the thumb twice (first press is to select the post, second is to like it). Report posts to administrators if they are offensive.
"""#instructions text

instructionsRect = Rect(100, instructionsScreenRect.bottom+100, size[0]-200, 300)#rect for the text



continBut = Rect(size[0]/2-buttonWidth[0]/2, size[1]-buttonWidth[1]-20, buttonWidth[0], buttonWidth[1])#continue Button
continText = largeButtonFont.render("Continue", True, BLACK)
continTextRect = Rect(continBut.x+continBut.width/2-continText.get_width()/2, continBut.y+continBut.height/2-continText.get_height()/2, continText.get_width(), continText.get_height())

def instructions():
    global screenNumber
    screenNumber=0#change screenNumber to 0 to control in hile running
    screen.blit(backgroundImage, (0,0))
    screen.blit(instructionsScreenTitle, instructionsScreenRect)
    draw.rect(screen, BUTTONCOLOR, continBut)#blit continue Button
    screen.blit(continText, continTextRect)#blit the text 
    drawText(instructionsRect, instructionsBody, False, False, largeButtonFont, screen, 30)#draw the text in a text wrap
    #screen.blit(instructionsObj, instructionsRect)
    
#2nd screen variables - tutor screen

titleText = majorQuestionFont.render("Let's Get You Set Up", True, BLACK)#title for 2nd screen
titleTextRect = Rect(size[0]/2 - titleText.get_width()/2, 50, titleText.get_width(), titleText.get_height())

leftMargin2 = 50
rightMargin2 = 50#this will control how things are laid out in terms of how far things are from the edges of the screen
majBuffer2 = 75
minorBuffer2 = 50
miniBuffer2 = 20

usernameText = smallerFont.render("Username:", True, BLACK)#these are text objects
usernameTextRect = Rect(leftMargin2, titleTextRect.y+titleTextRect.height+majBuffer2, usernameText.get_width(), usernameText.get_height())

passwordText = smallerFont.render("Password:", True, BLACK)#password text
passwordTextRect = Rect(leftMargin2, usernameTextRect.y + usernameTextRect.height + minorBuffer2, passwordText.get_width(), passwordText.get_height())

subjectQuestionText = smallTitleFont.render("Which Subjects Will You Tutor?", True, BLACK)#subject text
subjectQuestionTextRect = Rect(size[0]/2 - subjectQuestionText.get_width()/2, passwordTextRect.y+passwordTextRect.height+minorBuffer2, subjectQuestionText.get_width(), subjectQuestionText.get_height())
#user and password text fields (will be white rects)
usernameTextFieldRect = Rect(usernameTextRect.x+usernameTextRect.width+10, usernameTextRect.y-10, size[0]-10-10-usernameTextRect.x-usernameTextRect.width, usernameTextRect.height+20)
passwordTextFieldRect = Rect(usernameTextFieldRect.x, passwordTextRect.y-10, usernameTextFieldRect.width, passwordTextRect.height+20)

subjectTitle = subtitleFont.render("Subjects:", True, BLACK)#subject title
subjectTitleRect = Rect(leftMargin2, subjectQuestionTextRect.y+subjectQuestionTextRect.height+miniBuffer2, subjectTitle.get_width(), subjectTitle.get_height())
gradeTitle = subtitleFont.render("Your Grade:", True, BLACK)#grade title
gradeTitleRect = Rect(size[0]/2-gradeTitle.get_width()/2+200, subjectTitleRect.y, gradeTitle.get_width(), gradeTitle.get_height())

#make subject 1 and two boxes as well as a continue button. May have spacing issues. 

subjectOneText = smallerFont.render("#1:", True, BLACK)#text for subject one, two and the grades
subjectOneTextRect = Rect(leftMargin2-10, subjectTitleRect.y+subjectTitleRect.height+miniBuffer2, subjectOneText.get_width(), subjectOneText.get_height())
subjectTwoText = smallerFont.render("#2:", True, BLACK)
subjectTwoTextRect = Rect(leftMargin2-10, subjectOneTextRect.y+subjectOneTextRect.height + 40, subjectTwoText.get_width(), subjectTwoText.get_height())
#text fieklds for grades and subject input
subjectOneTextField = Rect(subjectOneTextRect.x+subjectOneTextRect.width+10, subjectOneTextRect.y-10, gradeTitleRect.x-10-subjectOneTextRect.x-subjectOneTextRect.width, subjectOneTextRect.height+20)
subjectTwoTextField = Rect(subjectTwoTextRect.x+subjectTwoTextRect.width+10, subjectTwoTextRect.y-10, gradeTitleRect.x-10-subjectTwoTextRect.x-subjectTwoTextRect.width, subjectTwoTextRect.height+20)
print(subjectOneTextField, subjectOneTextRect)
gradeOneTextField = Rect(gradeTitleRect.x+10, subjectOneTextField.y, size[0]-10-subjectOneTextField.x-subjectOneTextField.width-10, subjectOneTextField.height)
gradeTwoTextField = Rect(gradeOneTextField.x, gradeOneTextField.y+gradeOneTextField.height + 20, gradeOneTextField.width, gradeOneTextField.height)

screenTwoTextList = [usernameTextFieldRect, passwordTextFieldRect, subjectOneTextField, subjectTwoTextField, gradeOneTextField, gradeTwoTextField]
#continue button
buttonWidth2= 200
continueButton2 = Rect(size[0]/2-buttonWidth2/2, gradeTwoTextField.y+gradeTwoTextField.height+10, buttonWidth2, size[1]-(gradeTwoTextField.y+gradeTwoTextField.height+10+10))

continueText = largeButtonFont.render("Continue", True, BLACK)#continue button
continueTextRect = Rect(continueButton2.x+continueButton2.width/2-continueText.get_width()/2, continueButton2.y+continueButton2.height/2-continueText.get_height()/2, continueText.get_width(), continueText.get_height())

toNext=False #please change the name wheny ou figure out what ur doing

screenTwoTextArray = ["","","","","",""] #0 is username, 1 is password, 2 is subject 1, 3 is subject 2, 4 is grade 1, 5 is grade 2
textIndex2=None#this is the index of the above array currently being affected
typedLetters=""#this is how the typed things will be kept track of

#secondScreenInit
def startSecondScreen():
    global screenNumber
    global mode
    mode="tutor"#mode is now tutor. for sign up things this will be very helpful
    screenNumber=2
    screen.blit(backgroundImage, (0,0))#blit/draw to screen
    screen.blit(leftArrow, leftArrowSurfaceRect)#back button
    screen.blit(titleText, titleTextRect)
    draw.rect(screen, WHITE, usernameTextFieldRect)#blit text fields
    draw.rect(screen, WHITE, passwordTextFieldRect)

    screen.blit(usernameText, usernameTextRect)#bl;it text
    screen.blit(passwordText, passwordTextRect)
    screen.blit(subjectQuestionText, subjectQuestionTextRect)

    screen.blit(subjectTitle, subjectTitleRect)#blit titles
    screen.blit(gradeTitle, gradeTitleRect)
    screen.blit(subjectOneText, subjectOneTextRect)
    screen.blit(subjectTwoText, subjectTwoTextRect)

    draw.rect(screen, WHITE, subjectOneTextField)#blit text fields for subjects and grades
    draw.rect(screen, WHITE, subjectTwoTextField)
    
    draw.rect(screen, WHITE, gradeOneTextField)
    draw.rect(screen, WHITE, gradeTwoTextField)

    #button draw
    draw.rect(screen, BUTTONCOLOR, continueButton2)
    screen.blit(continueText, continueTextRect)

#third screen (user log in)
#reuse everything from second screen exzcept for the suibject and grades and the title text for that section
userSubjectQuestionText = smallTitleFont.render("Which subjects do you need help with?", True, BLACK)#text objects and rects
userSubjectQuestionTextRect = Rect(size[0]/2-userSubjectQuestionText.get_width()/2, subjectQuestionTextRect.y, subjectQuestionTextRect.width, subjectQuestionTextRect.height)

userSubjectOneTextField = Rect(subjectOneTextField.x, subjectOneTextField.y, size[0]-leftMargin2-rightMargin2, subjectOneTextField.height)#text field for the first subject
userSubjectTwoTextField = Rect(userSubjectOneTextField.x, userSubjectOneTextField.y+userSubjectOneTextField.height+20, userSubjectOneTextField.width, userSubjectOneTextField.height)

screenThreeTextList = [usernameTextFieldRect, passwordTextFieldRect, userSubjectOneTextField, userSubjectTwoTextField]
screenThreeTextArray = ["","","",""] #0 is username, 1 is password, 2 is subject 1, 3 is subject 2
textIndex3=None#index of above array being affected

choosePhotoName = None#flags for checking if photos were picked
profilePictureName = None

def startThirdScreen():
    global screenNumber
    global mode
    mode="users"#indicates user is signing up
    screenNumber=3
    screen.blit(backgroundImage, (0,0))#blit to screen
    screen.blit(leftArrow, leftArrowSurfaceRect)
    screen.blit(titleText, titleTextRect)
    draw.rect(screen, WHITE, usernameTextFieldRect)#blit text fields
    draw.rect(screen, WHITE, passwordTextFieldRect)

    screen.blit(usernameText, usernameTextRect)#blit text
    screen.blit(passwordText, passwordTextRect)
    screen.blit(userSubjectQuestionText, userSubjectQuestionTextRect)

    screen.blit(subjectTitle, subjectTitleRect)
    screen.blit(subjectOneText, subjectOneTextRect)#SUBJECT TEXT RECTS
    screen.blit(subjectTwoText, subjectTwoTextRect)

    draw.rect(screen, WHITE, userSubjectOneTextField)
    draw.rect(screen, WHITE, userSubjectTwoTextField)
    
    #button draw
    draw.rect(screen, BUTTONCOLOR, continueButton2)
    screen.blit(continueText, continueTextRect)

    print(tutorObjects)
##fourth screen
fourthLeftMargin=10#this is the left margin
verifyFont = majorQuestionFont.render("Let's Verify", True, BLACK)
verifyFontRect = Rect(size[0]/2-verifyFont.get_width()/2, 10, verifyFont.get_width(), verifyFont.get_height())#title 




verificationWidth=size[0]/2-200#this sets how big you want this section to be
verificationText=largeButtonFont.render("Is This Correct?", True, BLACK)#verificatiom title
verificationTextRect = Rect(fourthLeftMargin+(verificationWidth//2)-verificationText.get_width()//2,leftArrowSurfaceRect.y+leftArrowSurfaceRect.height+20, verificationText.get_width(), verificationText.get_height())

verificationSurface = Surface((verificationWidth, size[1]-2*(verifyFontRect.y+verifyFontRect.height)-100))#verification information surface
verificationSurfaceRect = Rect(fourthLeftMargin, verificationTextRect.y+verificationTextRect.height+10,verificationSurface.get_width(), verificationSurface.get_height()) 

verificationSurface.fill(WHITE)#make rects and fill the s8urfaces

choosePhotoText = largeButtonFont.render("Grades Verification", True, BLACK)#title texts
choosePhotoText2 = largeButtonFont.render("Profile Picture", True, BLACK)

widthHeight = (size[1]-(verificationSurfaceRect.y+verificationSurfaceRect.height)-20, size[1]-(verificationSurfaceRect.y+verificationSurfaceRect.height)-20)#width height of surface
choosePhotoSurface = Surface(widthHeight)#make surface from width height
choosePhotoRect = Rect((verificationSurfaceRect.x, verificationSurfaceRect.y+verificationSurfaceRect.height+10), (widthHeight))
photoX = transform.scale(image.load("photoX.jpg"), widthHeight)#photo for no photo
choosePhotoSurface.blit(photoX, (0,0))
choosePhotoTextRect = Rect(choosePhotoRect.x+choosePhotoRect.width+5, choosePhotoRect.y+choosePhotoRect.height/2-choosePhotoText.get_height()/2, choosePhotoText.get_width(), choosePhotoText.get_height())

#thumbTack = image.load("thumbTack.png")#maybe use

profilePictureSurface = Surface((size[0]-(verificationSurfaceRect.x+verificationSurfaceRect.width)-200, 300))#profilePicutres surface
profilePictureSurfaceRect = Rect(verificationSurfaceRect.x+verificationSurfaceRect.width+100, (size[1]-(verifyFontRect.y+verifyFontRect.height))//2-150, size[0]-(verificationSurfaceRect.x+verificationSurfaceRect.width)-200, 300)
profilePictureSurface.fill(WHITE)

profilePictureSurface.blit(transform.scale(photoX, (290,290)), ((profilePictureSurface.get_width()-290)//2,5))#blit the not pphoto on the surface

yourProfileText = largeButtonFont.render("Your Profile", True, BLACK)#your profile title
yourProfileTextRect = Rect(profilePictureSurfaceRect.x+profilePictureSurfaceRect.width//2-yourProfileText.get_width()//2, profilePictureSurfaceRect.y-yourProfileText.get_height()-5, yourProfileText.get_width(), yourProfileText.get_height())

secondChoosePhotoRect = Rect(yourProfileTextRect.x+yourProfileTextRect.width/2-choosePhotoText2.get_width()/2, yourProfileTextRect.y+profilePictureSurfaceRect.height+choosePhotoText2.get_height()+5, choosePhotoText2.get_width(), choosePhotoText2.get_height())

confirmButton = Rect(secondChoosePhotoRect.x, choosePhotoRect.y-20, secondChoosePhotoRect.width, choosePhotoRect.height)
confirmText = largeButtonFont.render("Confirm", True, BLACK)#confirm text title

profileFilename = None#flags to see if the pictures were selected
verifFilename = None
def startFourthScreen():
    global screenNumber
    global currentPerson
    screenNumber = 4#change screen number
    screen.blit(backgroundImage, (0,0))
    screen.blit(leftArrow, leftArrowSurfaceRect)
    screen.blit(verifyFont, verifyFontRect)
    screen.blit(verificationText, verificationTextRect)#blit to screen
    screen.blit(leftArrow, leftArrowSurfaceRect)
    if mode=="tutor":
        screen.blit(choosePhotoSurface, choosePhotoRect)#change it that this doesnt matter if the persojn is a user
        screen.blit(choosePhotoText, choosePhotoTextRect)
    screen.blit(profilePictureSurface, profilePictureSurfaceRect)
    screen.blit(yourProfileText, yourProfileTextRect)
    screen.blit(choosePhotoText2, secondChoosePhotoRect)
    buttonReset(confirmButton, confirmText)#implicitly makes a rect for the text obj and blits the button to the screen
    
    usernameVerifyText=smallerFont.render("Username: %s"%(currentPerson.username), True, BLACK)
    passwordVerifyText=smallerFont.render("Password: %s"%(currentPerson.password), True, BLACK)
    if mode=="tutor":#make proper text objects based on whether or not the person 
        subjectsDictKeys = currentPerson.subjectDict.keys()
        subjectOneVerifyText=smallerFont.render("Subject 1: %s, Grade: %s"%(subjectsDictKeys[0][0].upper()+subjectsDictKeys[0][1:], currentPerson.subjectDict[subjectsDictKeys[0]]), True, BLACK)
        if len(subjectsDictKeys)>1:
            subjectTwoVerifyText=smallerFont.render("Subject 2: %s, Grade: %s"%(subjectsDictKeys[1][0].upper()+subjectsDictKeys[1][1:], currentPerson.subjectDict[subjectsDictKeys[1]]), True, BLACK)
        else:
            subjectTwoVerifyText = None
    elif mode=="users":
        subjectList = currentPerson.subjects
        subjectOneVerifyText = minorFont.render("Subject 1: %s"%(subjectList[0][0].upper()+subjectList[0][1:]), True, BLACK)
        if len(subjectList)>1:
            subjectTwoVerifyText = minorFont.render("Subject 2: %s"%(subjectList[1][0].upper()+subjectList[1][1:]), True, BLACK)
        else:
            subjectTwoVerifyText = None
    if subjectTwoVerifyText!=None:
        length = 4
    else:
        length = 3

    surfaceBufferHeight = (verificationSurface.get_height()-usernameVerifyText.get_height()*length)/(length+1)


    verificationSurface.blit(usernameVerifyText, (verificationSurfaceRect.width/2-usernameVerifyText.get_width()/2, surfaceBufferHeight))
    verificationSurface.blit(passwordVerifyText, (verificationSurfaceRect.width/2-passwordVerifyText.get_width()/2, surfaceBufferHeight*2+usernameVerifyText.get_height()))
    verificationSurface.blit(subjectOneVerifyText, (verificationSurfaceRect.width/2-subjectOneVerifyText.get_width()/2, surfaceBufferHeight*3+usernameVerifyText.get_height()+passwordVerifyText.get_height()))
    if subjectTwoVerifyText != None:
        verificationSurface.blit(subjectTwoVerifyText, (verificationSurfaceRect.width/2-subjectTwoVerifyText.get_width()/2, surfaceBufferHeight*4+usernameVerifyText.get_height()+passwordVerifyText.get_height()+subjectOneVerifyText.get_height()))
    
    screen.blit(verificationSurface, verificationSurfaceRect)
    
##fifth screen
#reuse welcome text object 'welcomeTextBlock'
#animation
def startFifthScreen(offset=0):
    global screenNumber
    screenNumber=5
    screen.blit(backgroundImage, (0,0))#blit at the offset
    screen.blit(welcomeTextBlock, (size[0]/2-welcomeTextBlock.get_width()/2, size[1]/2-welcomeTextBlock.get_height()/2-offset))

totalIncrement = size[1]/2-welcomeTextBlock.get_height()/2#make the welcome font move by a total increment determined by how fast it will be moving ans for how long
time=1#60 second
increment = totalIncrement/(time*fps)
offset = 0
finalWelcomeTextRect = Rect(size[0]/2-welcomeTextBlock.get_width()/2, size[1]/2-welcomeTextBlock.get_height()/2-totalIncrement, welcomeTextBlock.get_width(), welcomeTextBlock.get_height())


#log in screen
topBuffer6=20
logInWelcomeText = welcomeFont.render("Welcome Back", True, BLACK)#log in text block
loginWelcomeTextRect = Rect(size[0]/2-logInWelcomeText.get_width()/2, topBuffer6, logInWelcomeText.get_width(), logInWelcomeText.get_height())

##usernameText = smallerFont.render("Username:", True, BLACK)
##usernameTextRect = Rect(leftMargin2, titleTextRect.y+titleTextRect.height+majBuffer2, usernameText.get_width(), usernameText.get_height())
##
##passwordText = smallerFont.render("Password:", True, BLACK)
##passwordTextRect = Rect(leftMargin2, usernameTextRect.y + usernameTextRect.height + minorBuffer2, passwordText.get_width(), passwordText.get_height())
##usernameTextFieldRect = Rect(usernameTextRect.x+usernameTextRect.width+10, usernameTextRect.y-10, size[0]-10-10-usernameTextRect.x-usernameTextRect.width, usernameTextRect.height+20)
##passwordTextFieldRect = Rect(usernameTextFieldRect.x, passwordTextRect.y-10, usernameTextFieldRect.width, passwordTextRect.height+20)
##screenTwoTextArray = ["","","","","",""] #0 is username, 1 is password, 2 is subject 1, 3 is subject 2, 4 is grade 1, 5 is grade 2
##textIndex2=None
#make text rects
usernameTextFieldRectSix = Rect(usernameTextFieldRect.x, size[1]/2-30-usernameTextFieldRect.height, usernameTextFieldRect.width, usernameTextFieldRect.height)
passwordTextFieldRectSix = Rect(passwordTextFieldRect.x, size[1]/2+30, passwordTextFieldRect.width, passwordTextFieldRect.height)

usernameTextRectSix = Rect(leftMargin2, usernameTextFieldRectSix.y+usernameTextFieldRectSix.height/2-usernameText.get_height()/2, usernameText.get_width(), usernameText.get_height())
passwordTextRectSix = Rect(usernameTextRectSix.x, passwordTextFieldRectSix.y+passwordTextFieldRectSix.height/2-passwordText.get_height()/2, passwordText.get_width(), passwordText.get_height())

screenSixTextArray = ["",""]#0 is username, 1 is password
screenSixTextList = [usernameTextFieldRectSix, passwordTextFieldRectSix]

continueButtonSix = Rect(size[0]-buttonWidth[0]-topBuffer6, size[1]-buttonWidth[1]-topBuffer6, buttonWidth[0], buttonWidth[1])
continueButtonTextSix = largeButtonFont.render("Log in", True, BLACK)
continueButtonTextRectSix = Rect(continueButtonSix.x+continueButtonSix.width/2-continueButtonTextSix.get_width()/2, continueButtonSix.y+continueButtonSix.height/2-continueButtonTextSix.get_height()/2, continueButtonTextSix.get_width(), continueButtonTextSix.get_height())
textIndex6=None#index to see which stering is going to be changed in screenSixTextArray

toNextSix=False#flag to see if advancing to next screen (7)

def startSixthScreen():#blit to screen
    global screenNumber
    screenNumber=6

    screen.blit(backgroundImage, (0,0))
    screen.blit(leftArrow, leftArrowSurfaceRect)
    screen.blit(logInWelcomeText, loginWelcomeTextRect)
    screen.blit(usernameText, usernameTextRectSix)
    screen.blit(passwordText, passwordTextRectSix)
    
    draw.rect(screen, WHITE, usernameTextFieldRectSix)
    draw.rect(screen, WHITE, passwordTextFieldRectSix)

    draw.rect(screen, BUTTONCOLOR, continueButtonSix)
    screen.blit(continueButtonTextSix, continueButtonTextRectSix)




##seventh screen
toolbarHeight = 0 #for future implementation of toolbar
surfaceBuffer=20
postSurfaceWidthHeight = (500, size[1]-finalWelcomeTextRect.y-finalWelcomeTextRect.height+5-toolbarHeight)
postSurfaceRect = Rect((size[0]/2-postSurfaceWidthHeight[0]/2, finalWelcomeTextRect.y+finalWelcomeTextRect.height+5), postSurfaceWidthHeight)
postSurface = Surface(postSurfaceWidthHeight)
postSurface.fill(WHITE)

#make rects and text objects
postSurfaceTitle = largeButtonFont.render("Posts", True, BLACK)
postSurfaceTitleRect = Rect((postSurfaceWidthHeight[0]/2-postSurfaceTitle.get_width()/2)+postSurfaceRect.x, postSurfaceRect.y, postSurfaceTitle.get_width(), postSurfaceTitle.get_height())

postSurfaceTitleBRect = Rect(postSurfaceRect.x, postSurfaceRect.y, postSurfaceWidthHeight[0], postSurfaceTitleRect.height)

connectSurfaceWidthHeight = (size[0]-surfaceBuffer*2-postSurfaceRect.x-postSurfaceRect.width, postSurfaceRect.height)
connectSurface = Surface(connectSurfaceWidthHeight)
connectSurfaceRect = Rect((postSurfaceRect.x+postSurfaceRect.width+surfaceBuffer, postSurfaceRect.y), connectSurfaceWidthHeight)

connectSurface.fill(WHITE)
accountTitle = largeButtonFont.render("Current Account", True, BLACK)
accountTitleRect = Rect(surfaceBuffer+(postSurfaceRect.x-surfaceBuffer)/2-accountTitle.get_width()/2, postSurfaceRect.y, accountTitle.get_width(), accountTitle.get_height())

def getImageFromURL(url):
    i=0
    while True:
        try:
            imageFile = cStringIO.StringIO(urlopen(url).read())#reads the string and stores a "filename" that can be accessed
            break
        except:
            i+=1
            print("Failed", i)#THIS IS DISGUSTING 
            pass
    img = image.load(imageFile)#loads file
    return img # returns file



usernameTextSeven = None#this will be text and rect objects (to be defined later)
usernameTextRectSeven = None

profilePictureRect = Rect(surfaceBuffer, accountTitleRect.y+accountTitleRect.height+5, postSurfaceRect.x-surfaceBuffer, 200)
profilePicture = None

likeFilled = image.load("likeFilled.png")
likeUnfilled = image.load("likeUnfilled.png")
#text and rects again!

verifiedText = smallerFont.render("Status: Verified", True, BLACK)#verified text
notVerifiedText = smallerFont.render("Status: Non-Verified", True, BLACK)

verifiedTextRect = Rect(profilePictureRect.x+profilePictureRect.width/2-verifiedText.get_width()/2, profilePictureRect.y+profilePictureRect.height+5+smallerFont.size("Uq")[1]+5, verifiedText.get_width(), verifiedText.get_height())
#rects for verified twext
notVerifiedTextRect = Rect(profilePictureRect.x+profilePictureRect.width/2-notVerifiedText.get_width()/2, verifiedTextRect.y, notVerifiedText.get_width(), notVerifiedText.get_height())

settingsRect = Rect(surfaceBuffer, notVerifiedTextRect.bottom+surfaceBuffer , postSurfaceRect.x - surfaceBuffer*2, size[1]-(notVerifiedTextRect.bottom+surfaceBuffer)-surfaceBuffer*2 )
#settings rect

settingsText = largeButtonFont.render("Settings", True, BLACK)
settingsTextRect = Rect(settingsRect.x+settingsRect.width/2 - settingsText.get_width()/2, settingsRect.y+5, settingsText.get_width(),settingsText.get_height())

photoSelecterText = smallerFont.render("New Profile Picture:", True, BLACK)
photoSelecterTextRect = Rect(settingsRect.x+5, settingsTextRect.y+settingsTextRect.height+8, photoSelecterText.get_width(), photoSelecterText.get_height())



photoSelectImage = transform.scale(photoX, (100,100))#rect for photo select
photoSelectImageRect = Rect(settingsRect.x+settingsRect.width/2 - photoSelectImage.get_width()/2, photoSelecterTextRect.bottom+5, photoSelectImage.get_width(), photoSelectImage.get_height())

logOutWords = smallTitleFont.render("Log out", True, BLUE)
logOutWordsRect = Rect(settingsRect.x+settingsRect.width/2-logOutWords.get_width()/2, settingsRect.y +settingsRect.height - logOutWords.get_height()-surfaceBuffer, logOutWords.get_width(), logOutWords.get_height())

    
connectText = largeButtonFont.render("Connect", True, BLACK)#conntect text
connectTextRect = Rect(connectSurfaceWidthHeight[0]/2-connectText.get_width()/2, accountTitleRect.y-connectSurfaceRect.y, connectText.get_width(), connectText.get_height())


plusImage = transform.scale(image.load("plus.png"), (50,50))
plusImageRect = Rect(size[0]-plusImage.get_width()-surfaceBuffer, surfaceBuffer, plusImage.get_width(), plusImage.get_height())
plusText = smallerFont.render("New", True, BLACK)
plusTextRect = Rect(plusImageRect.x+plusImageRect.width/2-plusText.get_width()/2, plusImageRect.y+plusImageRect.height+5, plusText.get_width(), plusText.get_height())

postArray=[]#ARRAY OF SURFACES CONTAINING ALL INFORMATION
postArrayRects = []#ARRAY OF THE RECTS THAT OUTLINE THE SURFACES
numbersIncluded = []#array of numbers that are already loaded
postInstances=[]#this is an array of post instances

likesRect=None

maxScroll = 0#this is the y coordinate of the topmost rect affter which scrolling will stop
top=0#this is the lowest it can go


def makePosts(numbersInclude, postHeight, length):
    postArraySeven = []#init arrays to nothing
    postArrayRectsSeven = []
    numbers = []
    instances=[]
    maxScroll=0
    top=0
    instances=[]
    likeRect=Rect(10000,100000,1000000,100000)#reset rect 
    global postSurfaceRect#access the surface rect
    
    try:
        idNumberArray=[int(x) for x in firebase.get("posts", None).keys()]#get all the id numbers we have to pull
    except:
        idNumberArray=[]

    fontSize=40#find the optimal font size
    while True:
        if font.SysFont(fontString, fontSize).get_height()*2+4>95:#if its too big, keep making it smaller
            fontSize-=1
        else:
            break
    textFont = font.SysFont(fontString, fontSize)#make a gont with fint size from the system wide font string
    textFont.set_underline(True)
    counter=0
    for number in idNumberArray:#iterate through list ( O(n) efficiency, albeit with high supressed constants). this will take time and will cause a lag.
        print(number)
        if number not in numbersInclude:
            ownerName = str(firebase.get("posts/"+str(number), "owner"))#get all the info from the database for each post
            print(ownerName)
            if ownerName in existingUsers:
                photoURL = str(firebase.get("users/"+ownerName, "profileURL"))
                print(photoURL)
                accType = "User"
                
            elif ownerName in existingTutors:
                photoURL = str(firebase.get("tutors/"+ownerName, "profileURL"))
                print(photoURL)
                accType = "Tutor"
            else:
                firebase.delete("posts/", str(number))
                print("DELETED")
                continue
            print("not deleted")
            
            tempSurface = Surface((postSurfaceRect.width-10, postHeight))#make a surface for the post
            tempSurface.fill((122,122,122))#this creates a rect that is ther aize of the post pane.

            titleText = str(firebase.get("posts/"+str(number), "title"))
            titleTextRect = Rect(110,5,tempSurface.get_width()-110-5, 95)

            i=0#blit the title onto the surface with a proper font size
            while textFont.size(titleText[:i])[0] < titleTextRect.width and i<len(titleText)-1:
                i+=1
            if titleText.rfind(" ", 0, i) != -1 and i<len(titleText)-2:
                print("splitting", i, len(titleText)-1)
                i = titleText.rfind(" ", 0, i+1)
            i+=1
            tempSurface.blit(textFont.render(titleText[:i], True, BLACK), titleTextRect)
            print("font decided")
            if i<len(titleText)-1 and len(titleText.strip())!=0:
                if textFont.size(titleText[i:])[0]>=titleTextRect.width:
                    j = len(titleText)-1
                    while textFont.size(titleText[i:j])[0]>titleTextRect.width+textFont.size("...")[0]:
                        j-=1
                    tempSurface.blit(textFont.render(titleText[i:j]+"...", True, BLACK), (titleTextRect.x, titleTextRect.y+textFont.get_height()+4))#if its cut off, add ...
                else:
                    tempSurface.blit(textFont.render(titleText[i:], True, BLACK), (titleTextRect.x, titleTextRect.y+textFont.get_height()+4))
            else:
                titleTextRect.height = titleTextRect.height - textFont.get_height()-4
            subjectText = str(firebase.get("posts/"+str(number), "subject"))
            subjectTextObj = minorFont.render("Subject:"+subjectText, True, (200,200,200))
            subjectTextRect = Rect(titleTextRect.x, titleTextRect.y+titleTextRect.height+5, subjectTextObj.get_width(), subjectTextObj.get_height())
            print("slow but steady")
            tempSurface.blit(subjectTextObj, subjectTextRect)#blit to surface
            

            bodyText = str(firebase.get("posts/"+str(number), "message"))
            bodyTextRect = Rect(titleTextRect.x, subjectTextRect.y+subjectTextRect.height+5, titleTextRect.width, postHeight-40-(subjectTextRect.y+subjectTextRect.height+5))

            print("start draw text")
            bottomY = drawText(bodyTextRect, bodyText, False, False, None, tempSurface, 25)#draw the text ion the rect
            print("draw text done")
            profilePostPicture = getImageFromURL(photoURL)
            print(profilePostPicture.get_width(), profilePostPicture.get_height())
            w,h = profilePostPicture.get_width(), profilePostPicture.get_height()
            arg = int(round((100/w)*100))#aspect ratio 
            postPic = transform.scale(profilePostPicture, (100, 100))
            print(w)
            postPicRect = Rect(5,5,100,postPic.get_height())
            print(postPic.get_width(), postPic.get_height())
            print(postPic)


            tempSurface.blit(postPic, postPicRect)
            try:
                likeMembers = [str(x) for x in firebase.get("posts/"+str(number), "likeMembers")]
            except:
                likeMembers=[]
            print(likeMembers)
##            except:
##                print("no like members")
##                likeMembers=[]
            nameText = minorFont.render(ownerName, True, BLACK)#make text rects and blit them
            nameTextXY = (postPicRect.x+postPicRect.width/2-nameText.get_width()/2, postPicRect.y+postPicRect.height+2)
            tempSurface.blit(nameText, nameTextXY)

            typeText = minorFont.render(accType, True, (200,200,200))
            typeTextXY = (postPicRect.x+postPicRect.width/2-typeText.get_width()/2, nameTextXY[1]+nameText.get_height()+2)
            tempSurface.blit(typeText, typeTextXY)

            likeRect = Rect(postPicRect.x+postPicRect.width/2-likeUnfilled.get_width()/2, typeTextXY[1]+typeText.get_height()+5, likeUnfilled.get_width(), likeUnfilled.get_height())
            if currentPerson.username not in likeMembers:
                tempSurface.blit(likeUnfilled, likeRect)#if it isnt likes, put the unfilled thumb. else, put filled thumb
            else:
                tempSurface.blit(likeFilled, likeRect)
            if currentPerson.username not in likeMembers:
                tLiked=False
            else:
                tLiked=True
            likes = int(firebase.get("posts/"+str(number), "likes"))#make text with amount of likes
            likesT = "%i Likes"%(likes)
            likesText = minorFont.render(likesT, True, BLACK)
            likesTextRect=Rect(likeRect.x+likeRect.width/2-likesText.get_width()/2, likeRect.y+likeRect.height+5, likesText.get_width(), likesText.get_height())#rect for the likes text
            tempSurface.blit(likesText, likesTextRect)
            
            print("time handling start")
            timeNumber = float(firebase.get("posts/"+str(number), "time"))
            timeText = t.strftime("Posted: %a, %d %b %Y %I:%M:%S %p", t.localtime(timeNumber))#make time stamp
            timeObj = minorFont.render(timeText, True, (200,200,200))
            tempSurface.blit(timeObj, (tempSurface.get_width()/2-timeObj.get_width()/2, tempSurface.get_height()-timeObj.get_height()-5))#blit time stamp
            print("appending")
            postArraySeven.append(tempSurface)
            numbers.append(number)
            print("done")
            status = str(firebase.get("posts/"+str(number), "status"))

            photoArray=[]
            try:
                listOfID = [str(x) for x in firebase.get("posts/"+str(number)+"/photos", None)]#get a lis of photoURLs
                print(listOfID)
            except:
                listOfID=[]
                #will happen when photos==0
##            
##            for i in listOfID:
##                photoArray.append(getImageFromURL(i))
           # try:
                #listOfPeople = firebase.
            try:
                repli = [int(x) for x in firebase.get("posts/"+str(number), "replies")]#get a list of replyIDs
            except:
                repli=[]
                print("ERROR/EMPTY")
            #make an instance of post and add it to the array
            instances.append(Post(bodyText, timeNumber, titleText, repli, ownerName, status, subjectText, str(number), listOfID, likes, likeMembers, tLiked, titleTextRect, postPic))
            print("REVIEW", instances[-1].likes)
##    postArrayRectsSeven=[]
    for item in range(len(postArraySeven)):
        tempRect = Rect(5, postSurfaceTitleRect.bottom-postSurfaceRect.y + postHeight*(item+length) + 10*(item+length), postSurfaceRect.width-10, postHeight)#RECT MUST CHANGE
        postArrayRectsSeven.append(tempRect)#make the rect objects for the posts
        if item==len(postArraySeven)-1:
            top = postSurfaceTitleRect.bottom-postSurfaceRect.y #find out how far you can scroll
            bottom = tempRect.bottom#bottom of the rect
            dist = bottom - (postSurfaceRect.height-postSurfaceRect.y+(postSurfaceTitleRect.bottom-postSurfaceRect.y) + 10*(item+length+2)) #how far the thing can scroll
            maxScroll = top - dist#min y of top rect 
    if len(postArraySeven)==0:
        tempRect = Rect(5, postSurfaceTitleRect.bottom-postSurfaceRect.y + postHeight*(length) + 10*(length), postSurfaceRect.width-10, postHeight)#RECT MUST CHANGE

        top = postSurfaceTitleRect.bottom-postSurfaceRect.y #figure out scrolling
        bottom = tempRect.bottom
        dist = bottom - (postSurfaceRect.height-postSurfaceRect.y+(postSurfaceTitleRect.bottom-postSurfaceRect.y) + 10*(length+2)) 
        maxScroll = top - dist

    postArraySeven.reverse()
    postArrayRectsSeven.reverse()
    numbers.reverse()
    instances.reverse()#reverse the orders and return a huge tuple
    
    print("returning")
    return (postArraySeven, postArrayRectsSeven, numbers, maxScroll, top, instances, likeRect)

likeClicked=False#flags for if like clicked
likeCollided=False

def startSeventhScreen():
    global screenNumber
    global mode
    global profilePicture
    global usernameTextSeven
    global usernameTextRectSeven
    global postArray
    global postArrayRects
    global numbersIncluded
    global maxScroll
    global top
    global postInstances
    global likesRect
    screenNumber=7

    tup = makePosts(numbersIncluded, 300, len(postArray))#get the values from make postsd and add them to data structures
    postArray = tup[0] + postArray
    postArrayRects = tup[1] + postArrayRects
    numbersIncluded = tup[2] + numbersIncluded
    maxScroll = tup[3]
    top = tup[4]
    postInstances = tup[5] + postInstances
    likesRect = tup[6]

    #calculate max scroll
    '''
    top = postSurfaceTitleRect.bottom-postSurfaceRect.y # this is the top most point of a rect on the surface
    bottom = postArrayRects[0].y+postArrayRects[0].height # this is the bottom most point of a rect
    dist = bottom - (postSurfaceRect.height - 10)
    maxScroll = top-dist#this is the highest a rect can go
    '''

    
    postSurface.fill(WHITE)
    #blitting and making/placing text
    for surface in range(len(postArray)):
        postSurface.blit(postArray[surface], postArrayRects[surface])
    print(currentPerson.profileURL)
    profilePic = getImageFromURL(currentPerson.profileURL)
    print(profilePic.get_height(),profilePic.get_width())
    aspectRatio = float(profilePic.get_width())/float(profilePic.get_height()) #width:height
    print(aspectRatio)
    w = int(round(profilePictureRect.height*aspectRatio))
    h = int(round(profilePictureRect.height))
    print(w,h)
    profilePicture = transform.scale(profilePic, (w,h))#this only works if aspect ratio is less than 1
    profilePictureRect.x = profilePictureRect.width/2-profilePicture.get_width()/2 + surfaceBuffer/2
    usernameTextSeven = smallerFont.render(str(currentPerson.username), True, BLACK)
    print(str(currentPerson.username))
    usernameTextRectSeven = Rect(accountTitleRect.x+accountTitleRect.width/2-usernameTextSeven.get_width()/2, profilePictureRect.y+profilePictureRect.height+5, usernameText.get_width(), usernameText.get_height())

    screen.blit(backgroundImage, (0,0))
    screen.blit(welcomeTextBlock, finalWelcomeTextRect)
    screen.blit(accountTitle, accountTitleRect)
    screen.blit(profilePicture, profilePictureRect)
    print(profilePicture, profilePictureRect)
    screen.blit(usernameTextSeven, usernameTextRectSeven)
    if mode=="tutor":#if the person is a tutor, check if they are a verified tutor
        if str(currentPerson.verified)=="True":
            screen.blit(verifiedText, verifiedTextRect)
        elif str(currentPerson.verified)=="False":
            screen.blit(notVerifiedText, notVerifiedTextRect)
        else:
            print("Logic error austin!")
    screen.blit(postSurface, postSurfaceRect)
    draw.rect(screen, WHITE, postSurfaceTitleBRect)
    screen.blit(postSurfaceTitle, postSurfaceTitleRect)
    

    screen.blit(plusImage, plusImageRect)#blit images
    screen.blit(plusText, plusTextRect)
    #connectSurface.blit(connectText, connectTextRect)#blitting
    #screen.blit(connectSurface, connectSurfaceRect)
    draw.rect(screen, WHITE, settingsRect)

    screen.blit(settingsText, settingsTextRect)#blit text objects
    screen.blit(photoSelecterText, photoSelecterTextRect)
    screen.blit(photoSelectImage, photoSelectImageRect)
    screen.blit(logOutWords, logOutWordsRect)

#eighth screen
surfaceBuffer8=20#design buffer
postTitle = majorQuestionFont.render("New Post", True, BLACK)#make rects for the screen
postTitleRect = Rect(size[0]/2-postTitle.get_width()/2, surfaceBuffer8, postTitle.get_width(), postTitle.get_height())

descriptionText = largeButtonFont.render("Please fill in the following information:", True, BLACK)
descriptionTextRect = Rect(size[0]/2-descriptionText.get_width()/2, postTitleRect.y+postTitleRect.height, descriptionText.get_width(), descriptionText.get_height())

postButton = Rect(size[0]-buttonWidth[0]-surfaceBuffer8, size[1]-surfaceBuffer8-buttonWidth[1], buttonWidth[0], buttonWidth[1])#button to post
postButtonText = largeButtonFont.render("Post", True, BLACK)
postButtonTextRect = Rect(postButton.x+postButton.width/2-postButtonText.get_width()/2, postButton.y+postButton.height/2-postButtonText.get_height()/2, postButtonText.get_width(), postButtonText.get_height())

enterEnabled = False#activates the enter key

questionTitle = largeButtonFont.render("Question:", True, BLACK)#question title
questionTitleRect = Rect(surfaceBuffer8, descriptionTextRect.y+descriptionTextRect.height+50, questionTitle.get_width(), questionTitle.get_height())

questionTextFieldRect = Rect(questionTitleRect.x+questionTitleRect.width+10, questionTitleRect.y+questionTitleRect.height/2-30, size[0]-surfaceBuffer8-(questionTitleRect.x+questionTitleRect.width+10), 60)

messageText = largeButtonFont.render("Question Details:", True, BLACK)#question text
messageTextRect = Rect(surfaceBuffer8, questionTextFieldRect.y+questionTextFieldRect.height+10, messageText.get_width(), messageText.get_height())

photoSelectText = largeButtonFont.render("Select Photos:", True, BLACK)

rectWidth=100
photoSelectRect1 = Rect(surfaceBuffer8, postButton.y-25-rectWidth, rectWidth, rectWidth)
photoSelectRect2 = Rect(photoSelectRect1.x+rectWidth+(size[0]-surfaceBuffer8*2-rectWidth*4)/3, photoSelectRect1.y, rectWidth, rectWidth)#photo rects
photoSelectRect3 = Rect(photoSelectRect2.x+rectWidth+(size[0]-surfaceBuffer8*2-rectWidth*4)/3, photoSelectRect2.y, rectWidth, rectWidth)
photoSelectRect4 = Rect(photoSelectRect3.x+rectWidth+(size[0]-surfaceBuffer8*2-rectWidth*4)/3, photoSelectRect3.y, rectWidth, rectWidth)

finalFirstPhoto=None
finalFirstPhotoFile=None
finalSecondPhoto = None#init the photo files and photo objects to nothing
finalSecondPhotoFile=None
finalThirdPhoto=None
finalThirdPhotoFile=None
finalFourthPhoto=None
finalFourthPhotoFile=None

photoSelectTextRect = Rect(surfaceBuffer8,photoSelectRect1.y-5-photoSelectText.get_height(), photoSelectText.get_width(), photoSelectText.get_height())

messageTextFieldRect = Rect(surfaceBuffer8, messageTextRect.y+messageTextRect.height+5, size[0]-surfaceBuffer8*2, photoSelectTextRect.y-(messageTextRect.y+messageTextRect.height+5))

subjectText = largeButtonFont.render("Subject:", True, BLACK)#subject text
subjectTextRect = Rect(surfaceBuffer8, postButton.y+postButton.height/2-subjectText.get_height()/2, subjectText.get_width(), subjectText.get_height())

subjectTextField = Rect(subjectTextRect.x+subjectTextRect.width+5, subjectTextRect.y+subjectTextRect.height/2-30, postButton.x-(subjectTextRect.x+subjectTextRect.width+5)-5, 60)





eighthScreenTextArray = ["","",""]#title, message, subject
eighthScreenTextList = [questionTextFieldRect, messageTextFieldRect,subjectTextField]#title, message, subject

confirmPost=False
symbolsAllowed=False#Flags that let me see if spaces are enabled for text, symbols, etc

spaceEnabled=False
textIndex8=0
def startEighthScreen():
    global screenNumber
    global enterEnabled
    global symbolsAllowed
    global spaceEnabled

    screenNumber = 8
    symbolsAllowed=True#symbols are allowed for key entry
    screen.blit(backgroundImage, (0,0))
    screen.blit(postTitle, postTitleRect)#blit to screen

    screen.blit(photoSelectText, photoSelectTextRect)#blit text
    screen.blit(descriptionText, descriptionTextRect)

    screen.blit(questionTitle, questionTitleRect)
    screen.blit(messageText, messageTextRect)

    screen.blit(leftArrow, leftArrowSurfaceRect)

    draw.rect(screen, WHITE, questionTextFieldRect)#blit text fields
    draw.rect(screen, WHITE, messageTextFieldRect)
    draw.rect(screen, WHITE, subjectTextField)
    screen.blit(subjectText, subjectTextRect)
    if finalFirstPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect1)#blit images or placeholders
    else:
        screen.blit(finalFirstPhoto, photoSelectRect1)
    if finalSecondPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect2)
    else:
        screen.blit(finalSecondPhoto, photoSelectRect2)
    if finalThirdPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect3)
    else:
        screen.blit(finalThirdPhoto, photoSelectRect3)
    if finalFourthPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect4)#draw the images
    else:
        screen.blit(finalFourthPhoto, photoSelectRect4)

    draw.rect(screen, BUTTONCOLOR, postButton)#blit the butto
    screen.blit(postButtonText, postButtonTextRect)

    

    enterEnabled=True#enters are enables and spaces enabled
    spaceEnabled = True


def clickedButton(rect, text, color = CLICKEDBUTTONCOLOR, surface = screen):#clicking a button
    draw.rect(surface, color, rect)#draw the button and the text
    surface.blit(text, (rect.x+rect.width/2-text.get_width()/2, rect.y+rect.height/2-text.get_height()/2))

def drawText(field, text, selected=True, center=True, font = largeButtonFont, surface=screen, fontSize=20):
    global fontString #uses the global font string
    global screenNumber
    print("1")
    draw.rect(surface, WHITE, field)
    print("2")
    if center:#if its centered, make the text object with specified font
        textObj = font.render(text, True, BLACK)
    if selected:
        draw.rect(surface, GREEN, field, 1)#draw green thing around text
    print("3")
    if center:
        if textObj.get_width() > field.width-10:#make a text wrap display
            testFontSize = 40
            while True:
                from pygame import font
                testFont = font.SysFont(fontString, testFontSize)
                width = testFont.size(text)[0]
                if width < field.width-10:
                    break
                testFontSize-=2
            textObj = font.SysFont(fontString, testFontSize).render(text, True, BLACK)
            print("4")
    else:#error with word wrap with long strings that dont contain spaces or new line characters. fix before continuing
        from pygame import font 
        font = font.SysFont(fontString, fontSize)#make the font
        fontHeight = font.size("Hg")[1]
        y=field.y+5
        lineSpacing = 2#spacing for lines
        print(text)
        while len(text)>0:#taken from pygame wiki
            print(text)
            if text[0]=="\n":
                try:
                    text=text[1:]
                except:
                    break
            i = 1
            enter=False
            print("5")
            # determine if the row of text will be outside our area
            if y + fontHeight > field.y+field.height:
                break
                

            # determine maximum width of line
            while font.size(text[:i])[0] < field.width and i < len(text):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(text) and " " in text[:i]:
                i = text.rfind(" ", 0, i) + 1
            if "\n" in text[:i]:
                i = text.find("\n", 0, i)
                print(i, "this is the index")
                enter=True
            # render the line and blit it to the surface
            print(text[:i])
            image = font.render(text[:i], True, BLACK)

            surface.blit(image, (field.x+5, y))
            y += fontHeight + lineSpacing
            text = text[i:]
            print("6")
        return y

    if center:
        screen.blit(textObj, (field.x+5, field.y+field.height/2-textObj.get_height()/2))


##NINTH SCREEN
postDetailsText = largeButtonFont.render("Post Details", True, BLACK)#make rects and text objects
postDetailsTextRect = Rect(size[0]/2-postDetailsText.get_width()/2, surfaceBuffer, postDetailsText.get_width(), postDetailsText.get_height())


postDetailsSurface = Surface((size[0]/2-surfaceBuffer*2, size[1]-surfaceBuffer*2 - postDetailsTextRect.bottom))#surface for details 
postDetailsSurfaceRect = Rect(surfaceBuffer, postDetailsTextRect.y+postDetailsTextRect.height+surfaceBuffer, size[0]/2-surfaceBuffer*2, size[1]-surfaceBuffer*2-postDetailsTextRect.bottom)

postRepliesSurface = Surface((size[0]/2-surfaceBuffer*2, size[1]-surfaceBuffer*2 - postDetailsTextRect.bottom))#surface replies
postRepliesSurfaceRect = Rect(size[0]/2+surfaceBuffer, postDetailsSurfaceRect.y, size[0]/2-surfaceBuffer*2, size[1]-surfaceBuffer*2 - postDetailsTextRect.bottom)

proPicRect=Rect(surfaceBuffer, surfaceBuffer, 100, 100)#rect for new pic

#rect for the post titles
postTitlesRects = Rect(proPicRect.x+proPicRect.width+surfaceBuffer, proPicRect.y, postDetailsSurfaceRect.width-(proPicRect.x+proPicRect.width+surfaceBuffer*2), proPicRect.height)
#rect for the time titles
timeStampRect = Rect(surfaceBuffer, postTitlesRects.y+postTitlesRects.height+5, postDetailsSurfaceRect.width-surfaceBuffer*2, minorFont.size("Hg")[1])

photoSelectText = largeButtonFont.render("Select Photos:", True, BLACK)


#report button
reportButtonRect = Rect(surfaceBuffer, postDetailsSurfaceRect.height-buttonWidth[1]-surfaceBuffer, buttonWidth[0], buttonWidth[1])
reportButtonText = largeButtonFont.render("Report", True, BLACK)
reportButtonTextRect = Rect(reportButtonRect.x+reportButtonRect.width/2-reportButtonText.get_width()/2, reportButtonRect.y+reportButtonRect.height/2-reportButtonText.get_height()/2, reportButtonText.get_width(), reportButtonText.get_height())

#use like button images: likeFilled, likeUnfilled


likesTextsRect = Rect(postDetailsTextRect.width-likeFilled.get_width()/2-surfaceBuffer+minorFont.size("Likes: X")[0]/2, postDetailsSurfaceRect.height-surfaceBuffer-minorFont.size("Hg")[1], minorFont.size("Likes: X")[0], minorFont.size("Hg")[1])

postLikeButtonRect = Rect(postDetailsSurfaceRect.width-surfaceBuffer-likeFilled.get_width(), likesTextsRect.y-likeFilled.get_height()-5, likeFilled.get_width(), likeFilled.get_height())

sHW = (postDetailsSurfaceRect.width - surfaceBuffer*2, 110)
imageViewSurface = Surface(sHW)
imageViewSurfaceRects=[]#this will be initialized containing the rct agrugments for thwe photos to be mdisplayed inside of thw surface.

imageViewSurfaceRect = Rect((surfaceBuffer, reportButtonRect.y - sHW[1] - surfaceBuffer), sHW)#CHECK DESIGN. IN IT THE START FUNC TION. MAKE THE FUNCTION TO POPULASTE THE REPLIES INSTANCES



postBodyRect = Rect(proPicRect.x, proPicRect.y+surfaceBuffer+proPicRect.height, postDetailsSurfaceRect.width-surfaceBuffer*2, imageViewSurfaceRect.y - timeStampRect.bottom)

imageViewArray=[]#this is an array of images and image rects 
imageViewArrayRects=[]

replySurfaceArray=[]
replySurfaceRects=[]#list of replies, surfaces and rects. linked by index 
replyOwners=[]

def getReplies(idNumber):
    try:
        replyIDs = [int(x) for x in firebase.get("posts/"+str(idNumber), "replies")]#get the ids of the replies in question
    except TypeError:
        replyIDs = []
        print("empty replies")

    replyRects=[]
    replySurfaces=[]#start with empty arrays
    replyObjects=[]

    surfaceHeight=300
    for num in replyIDs:
        info = {str(x): y for x,y in firebase.get("replies", str(num)).iteritems()}#make all keys strings
        print(info)
        message = str(info["message"])
        title = str(info["title"])
        timeNumber = float(info["time"])
        owner = str(info["owner"])#parse dictionary and get all info needed
        parentID = str(info["parentID"])
        replyID = num
        try:
            photos = [str(x) for x in info["photos"]]
        except:#if databasev empty
            photos=[]
        likes = int(info["likes"])
        try:
            likeMembers = [str(y) for y in info["likeMembers"].values()]
        except:#if empty amke empty array
            likeMembers=[]
        if currentPerson.username in likeMembers:#set liked flag
            liked=True
        else:
            liked=False
        replyObjects.append(Replies(message, timeNumber, title, owner, parentID, replyID, photos, likes, likeMembers, liked))#append object to array


        replySurface = Surface((postRepliesSurfaceRect.width-surfaceBuffer*2, surfaceHeight))
        replySurface.fill((128,128,128))#make surface and fill with light frey

        if owner in existingUsers:
            profileLink = firebase.get("users/"+owner, "profileURL")#check database if verified. if user = false. if tutor then check
            isVerified=False
            print(profileLink)
        elif owner in existingTutors:
            profileLink = firebase.get("tutors/"+owner, "profileURL")
            isVerified = firebase.get("tutors/"+owner, "verified")
            


            
            print(profileLink)

        profilePict = transform.scale(getImageFromURL(profileLink), (100,100))#blit profile pic
        profilePictRect = Rect(surfaceBuffer, surfaceBuffer, 100, 100)
        replySurface.blit(profilePict, profilePictRect)

        ownerTextObj = minorFont.render(owner, True, (200,200,200))
        ownerTextObjRect = Rect(profilePictRect.x+profilePictRect.width/2-ownerTextObj.get_width()/2, profilePictRect.y+profilePictRect.height+5, ownerTextObj.get_width(), ownerTextObj.get_height())

        if isVerified=="True":#if verified, add tutor badge
            verifiedTextObj = minorFont.render("Tutor", True, BLACK)
            verifiedTextRect = Rect(profilePictRect.x+profilePictRect.width/2-verifiedTextObj.get_width()/2, ownerTextObjRect.bottom+5, verifiedTextObj.get_width(), verifiedTextObj.get_height())
            replySurface.blit(verifiedTextObj, verifiedTextRect)
        timeText = t.strftime("Posted: %a, %d %b %Y %I:%M:%S %p", t.localtime(timeNumber))#make timestamp using time module
        timeObj = minorFont.render(timeText, True, (200,200,200))
        
        replySurface.blit(ownerTextObj, ownerTextObjRect)
        
#make rects and text objects 
        replyTitleRectangle = Rect(profilePictRect.x+profilePictRect.width+10, profilePictRect.y, replySurface.get_width()-20-(profilePictRect.x+profilePictRect.width), profilePictRect.height)
        #rect for time stamp
        timeRect = Rect(replyTitleRectangle.x+replyTitleRectangle.width/2-timeObj.get_width()/2, replySurface.get_height()-10-timeObj.get_height() , timeObj.get_width(), timeObj.get_height())
        replySurface.blit(timeObj, timeRect)
        #rect for body text
        replyBodyRectangle = Rect(replyTitleRectangle.x, replyTitleRectangle.bottom+5, replyTitleRectangle.width, timeRect.y-10-(replyTitleRectangle.bottom+5))
        #rect for the like icon 
        likeIconRect = Rect(profilePictRect.x+profilePictRect.width/2-likeFilled.get_width()/2, ownerTextObjRect.bottom+5+(replySurface.get_height() - (ownerTextObjRect.bottom+5))/2 - likeFilled.get_height()/2 - minorFont.size("Hg")[1]/2, likeFilled.get_width(), likeFilled.get_height())
        replyLikeText = "Likes: %i"%(replyObjects[-1].likes)
        replyLikeTextObj = minorFont.render(replyLikeText, True, (200,200,200))
        replyLikeTextRect = Rect(likeIconRect.x+likeIconRect.width/2-replyLikeTextObj.get_width()/2, likeIconRect.bottom+5, replyLikeTextObj.get_width(), replyLikeTextObj.get_height())

        if replyObjects[-1].liked:#if its like, use the filled icon. if not, use unfilled
            replySurface.blit(likeFilled, likeIconRect)
            print("liked")
        else:
            replySurface.blit(likeUnfilled, likeIconRect)


        replySurface.blit(replyLikeTextObj, replyLikeTextRect)


        i=0#blit the title at appropriate location
        fontSize=40
        while True:
            if font.SysFont(fontString, fontSize).get_height()*2+4>replyTitleRectangle.height:#find right font size
                fontSize-=1
            else:
                break
        textFont = font.SysFont(fontString, fontSize)
        textFont.set_underline(True)
        
        while textFont.size(title[:i])[0] < replyTitleRectangle.width-10 and i<len(title)-1:
            i+=1
        if title.rfind(" ", 0, i) != -1 and i<len(title)-2:
            print("splitting", i, len(title)-1)#find the font size and then blit the good font size
            i = titleText.rfind(" ", 0, i+1)
        i+=1
        replySurface.blit(textFont.render(title[:i], True, BLACK), replyTitleRectangle)
        print("font decided")
        if i<len(title)-1 and len(title.strip())!=0:
            if textFont.size(title[i:])[0]>=replyTitleRectangle.width-10:
                j = len(title)-1
                while textFont.size(title[i:j])[0]>replyTitleRectangle.width-10+textFont.size("...")[0]:
                    j-=1
                replySurface.blit(textFont.render(title[i:j]+"...", True, BLACK), (replyTitleRectangle.x, replyTitleRectangle.y+textFont.get_height()+4))
            else:
                replySurface.blit(textFont.render(title[i:], True, BLACK), (replyTitleRectangle.x, replyTitleRectangle.y+textFont.get_height()+4))
        else:
            replyTitleRectangle.height = replyTitleRectangle.height - textFont.get_height()-4

        drawText(replyBodyRectangle, message, False, False, largeButtonFont, replySurface)

        replySurfaces.append(replySurface)
    if len(replyIDs)==0:#if there are no ids, make an empty object
        replyRects=[]
        replySurfaces=[]
        replyObjects=[]
        likeIconRect = None
        replyTitleRectangle = None
        replyLikeTextRect = None
        maxScroll=0
        top=0
    maxScroll = 0
    for rectangle in range(len(replySurfaces)):
        replyRect = Rect(surfaceBuffer, surfaceBuffer + (surfaceHeight+10)*rectangle, surfaceHeight, postRepliesSurfaceRect.width - surfaceBuffer*2)
        replyRects.append(replyRect)
        if rectangle==len(replySurfaces)-1:#make the rectangles for each obj and find out how much scrolling is possibkle 
            top = surfaceBuffer
            bottom = replyRect.bottom
            dist = bottom - postRepliesSurfaceRect.height
            maxScroll = top - dist
    
    
    replyRects.reverse()
    replySurfaces.reverse()
    replyObjects.reverse()#reverse them 

    

    return replyRects, replySurfaces, replyObjects, replyIDs, likeIconRect, replyTitleRectangle, replyLikeTextRect, maxScroll, top#return tuple

        
        
        
hoverBool=False
reportClicked=False

parentID=None
parentInstance=None#these will be the variebles to access the parent instance for the 9th screen
repliesRects=[]
repliesObjects=[]
repliesSurfaces=[]
repliesIDs=[]
repliesLikeIconRect=None
repliesTitleRectangle=None
repliesLikesTextsRects=None
maxReplyScroll=0
replyTop = 0
likeClicked=False
def goToNinthScreen(instance):
    global imageViewArray
    global imageViewArrayRects
    global screenNumber
    global parentID
    global parentInstance#will be accessed for adding to instances
    global likesTextsRect
    global repliesRects
    global repliesObjects#these are globals so they cahn be accessed for collision detection outside of the function
    global repliesSurfaces
    global repliesIDs
    global repliesLikeIconRect
    global repliesTitleRectangle
    global repliesLikesTextsRects
    global postLikeButtonRect
    global maxReplyScroll
    global replyTop
    global likeClicked

    
    parentID = instance.idNumber#set global variables to appropriate ionstances of replies
    parentInstance = instance
    getReplies(parentInstance.idNumber)

    print(parentInstance.photos, parentInstance.__class__.__name__, "Photos")
    toArrowCursor()#switch cursor
    
    screen.blit(backgroundImage, (0,0))
    screen.blit(leftArrow, (leftArrowSurfaceRect.x, leftArrowSurfaceRect.y))

    screen.blit(postDetailsText, postDetailsTextRect)

    #blit to postDetailsSurface
    postDetailsSurface.fill((200,200,200))

    postDetailsSurface.blit(instance.profilePic, proPicRect)#make rects and blit them

    nameText = minorFont.render(instance.owner, True, BLACK)
    nameTextRect = Rect(proPicRect.x+proPicRect.width/2-nameText.get_width()/2, proPicRect.bottom+7, nameText.get_width(), nameText.get_height())

    postBodyRect.y = nameTextRect.y+nameTextRect.height+surfaceBuffer#rect for the body of the post
    postBodyRect.height = imageViewSurfaceRect.y-postBodyRect.y-surfaceBuffer
    postDetailsSurface.blit(nameText, nameTextRect)

    #draw.rect(postDetailsSurface, (200,200,200), postTitleRects)
    titleText = instance.title
    i=0
    postTitlesRects = Rect(proPicRect.x+proPicRect.width+surfaceBuffer, proPicRect.y, postDetailsSurfaceRect.width-(proPicRect.x+proPicRect.width+surfaceBuffer*2), proPicRect.height)

    draw.rect(postDetailsSurface, WHITE, postTitlesRects)
    fontSize=40
    while True:#blit title text (same algo as above)
        if font.SysFont(fontString, fontSize).get_height()*2+4>postTitlesRects.height:
            fontSize-=1
        else:
            break
    textFont = font.SysFont(fontString, fontSize)
    textFont.set_underline(True)
    
    while textFont.size(titleText[:i])[0] < postTitlesRects.width-10 and i<len(titleText)-1:
        i+=1
    if titleText.rfind(" ", 0, i) != -1 and i<len(titleText)-2:
        print("splitting", i, len(titleText)-1)
        i = titleText.rfind(" ", 0, i+1)
    i+=1
    postDetailsSurface.blit(textFont.render(titleText[:i], True, BLACK), postTitlesRects)
    print("font decided")
    if i<len(titleText)-1 and len(titleText.strip())!=0:
        if textFont.size(titleText[i:])[0]>=postTitlesRects.width-10:
            j = len(titleText)-1
            while textFont.size(titleText[i:j])[0]>postTitlesRects.width-10+textFont.size("...")[0]:
                j-=1
            postDetailsSurface.blit(textFont.render(titleText[i:j]+"...", True, BLACK), (postTitlesRects.x, postTitlesRects.y+textFont.get_height()+4))
        else:
            postDetailsSurface.blit(textFont.render(titleText[i:], True, BLACK), (postTitlesRects.x, postTitlesRects.y+textFont.get_height()+4))
    else:
        postTitlesRects.height = postTitlesRects.height - textFont.get_height()-4
##check after the reply if the title for the posrt comes up right on svreen 9. this is wherte you pleft off at 7:11pm
    bodyText = str(instance.message)
    drawText(postBodyRect, bodyText, selected=False, center=False, font = largeButtonFont, surface=postDetailsSurface, fontSize=20)#make the textwraped body text

    #blit with image surface
    imageViewSurface.fill(WHITE)
    imageViewArrayRects = []
    for url in range(len(instance.photos)):
        imageViewArray.append(transform.scale(getImageFromURL(instance.photos[url]), (100,100)))
        imageViewArrayRects.append(Rect(10+110*url, 10, 100, 100))#get picture objects from url, scale, add to array
        imageViewSurface.blit(imageViewArray[-1], imageViewArrayRects[-1])
    if len(instance.photos)==0:
        imageText = largeButtonFont.render("No Images To Display", True, BLACK)
        imageTextRect9 = Rect(imageViewSurfaceRect.width/2-imageText.get_width()/2, imageViewSurfaceRect.height/2-imageText.get_height()/2, imageText.get_width(), imageText.get_height())
        imageViewSurface.blit(imageText, imageTextRect9)#if no images, say that. and blit it
    
    #end image surface
    postDetailsSurface.blit(imageViewSurface, imageViewSurfaceRect)
    

    draw.rect(postDetailsSurface, BUTTONCOLOR, reportButtonRect)#draw report button
    postDetailsSurface.blit(reportButtonText, reportButtonTextRect)

    if instance.liked==True or instance.liked=="True":
        postDetailsSurface.blit(likeFilled, postLikeButtonRect)#see which thumb to load
    else:
        postDetailsSurface.blit(likeUnfilled, postLikeButtonRect)

    likesText = minorFont.render("Likes: %i"%(instance.likes), True, WHITE)#likes text init
                                                                      
    likesTextsRect.x = postLikeButtonRect.x+postLikeButtonRect.width/2-likesText.get_width()/2
    postDetailsSurface.blit(likesText, likesTextsRect)
    #end post surface
    screen.blit(postDetailsSurface, postDetailsSurfaceRect)#blit the details surface 
    
    screen.blit(plusImage, (plusImageRect.x, plusImageRect.y-5))
    plusText = minorFont.render("Reply", True, BLACK)
    plusTextRect = Rect(plusImageRect.x+plusImageRect.width/2-plusText.get_width()/2, plusImageRect.bottom-10, plusText.get_width(), plusText.get_height())
    screen.blit(plusText, plusTextRect)#plus icon

    postRepliesSurface.fill((200,200,200))#fill surface with grey

    #populate the surface

    tu = getReplies(parentID)
    repliesRects = tu[0]
    repliesObjects = tu[2]
    repliesSurfaces = tu[1]#get output for posts and store them for future use
    repliesIDs = tu[3]
    repliesLikeIconRect = tu[4]
    repliesTitleRectangle = tu[5]
    repliesLikesTextsRects = tu[6]
    maxReplyScroll = tu[7]
    replyTop = tu[8]

    for index in range(len(repliesSurfaces)):
        postRepliesSurface.blit(repliesSurfaces[index], repliesRects[index])#blit to screen
    
    screen.blit(postRepliesSurface, postRepliesSurfaceRect)
    screenNumber=9

    

######SCREEN 10 IS THE CREATE REPLY SCREEN
repliesWelcomeText = welcomeFont.render("Replies", True, BLACK)
repliesWelcomeTextRect = Rect(size[0]/2-repliesWelcomeText.get_width()/2, surfaceBuffer, repliesWelcomeText.get_width(), repliesWelcomeText.get_height())
#make the replies text and the title textfield
titleTextField10 = Rect(surfaceBuffer + largeButtonFont.size("Title:")[0]+10, repliesWelcomeTextRect.bottom+surfaceBuffer, size[0] - surfaceBuffer - (surfaceBuffer + largeButtonFont.size("Title:")[0]+10), 60)
#title rect
titleInputText = largeButtonFont.render("Title:", True, BLACK)
titleInputTextRect = Rect(surfaceBuffer, titleTextField10.y+titleTextField10.height/2-titleInputText.get_height()/2, titleInputText.get_width(), titleInputText.get_height())
#reply rect
replyConfirm = Rect(size[0]/2-buttonWidth[0]/2, size[1]-surfaceBuffer-buttonWidth[1], buttonWidth[0], buttonWidth[1])
replyText = largeButtonFont.render("Reply", True, BLACK)
replyTextRect = Rect(replyConfirm.x+replyConfirm.width/2-replyText.get_width()/2, replyConfirm.y+replyConfirm.height/2-replyText.get_height()/2, replyText.get_width(), replyText.get_height())
#photos selected
replyRectWidth=100
replyPhotoSelect1 = Rect(surfaceBuffer, replyConfirm.y-surfaceBuffer - replyRectWidth, replyRectWidth, replyRectWidth)
replyPhotoSelect2=Rect(replyPhotoSelect1.x+replyRectWidth+(size[0]-surfaceBuffer*2-replyRectWidth*4)/3, replyPhotoSelect1.y, replyRectWidth, replyRectWidth)#rects
replyPhotoSelect3 = Rect(replyPhotoSelect2.x+replyRectWidth+(size[0]-surfaceBuffer*2-replyRectWidth*4)/3, replyPhotoSelect1.y, replyRectWidth, replyRectWidth)
replyPhotoSelect4=Rect(replyPhotoSelect3.x+replyRectWidth+(size[0]-surfaceBuffer*2-replyRectWidth*4)/3, replyPhotoSelect1.y, replyRectWidth, replyRectWidth)

replyFirstPhoto=None
replyFirstPhotoFile = None
replySecondPhoto=None
replySecondPhotoFile=None#files for blitting. init to none
replyThirdPhoto=None
replyThirdPhotoFile=None
replyFourthPhoto=None
replyFourthPhotoFile=None

replyPhotoSelectText = largeButtonFont.render("Select Photos:", True, BLACK)
replyPhotoSelectTextRect = Rect(surfaceBuffer, replyPhotoSelect1.y-surfaceBuffer-replyPhotoSelectText.get_height(), replyPhotoSelectText.get_width(), replyPhotoSelectText.get_height())

detailsText = largeButtonFont.render("Details:", True, BLACK)
detailsTextRect = Rect(surfaceBuffer, titleTextField10.bottom+20, detailsText.get_width(), detailsText.get_height())

detailsTextField = Rect(surfaceBuffer, detailsTextRect.bottom+5, size[0]-surfaceBuffer*2, replyPhotoSelectTextRect.y-surfaceBuffer*2-(detailsTextRect.bottom+5))


textIndex10=None#0 is for title, 1 is for body
tenthReplyTextList = ["",""]#text list for the tenth screen (reply)
tenthReplyTextArray = [titleTextField10,detailsTextField]



confirmedReply=False#flag for 10 screen


replyInstance = None
def startTenthScreen(parentID):
    global screenNumber
    global replyInstance
    screenNumber=10#change screen number
    
    screen.blit(backgroundImage, (0,0))
    replyInstance = Replies(None, None, None, None, parentID, None)#make a reply instance (empty. will be filled with input)
    screen.blit(repliesWelcomeText, repliesWelcomeTextRect)
    screen.blit(titleInputText, titleInputTextRect)

    draw.rect(screen, WHITE, titleTextField10)#make te3xt field

    screen.blit(replyText, replyTextRect)#make the reply text
    screen.blit(detailsText, detailsTextRect)
    draw.rect(screen, WHITE, detailsTextField)#make text field

    screen.blit(replyPhotoSelectText, replyPhotoSelectTextRect)#blitting
    draw.rect(screen, BUTTONCOLOR, replyConfirm)
    screen.blit(replyText, replyTextRect)

    screen.blit(leftArrow, leftArrowSurfaceRect)
    #LEFT OFF HERE
    if replyFirstPhoto==None:#if there are photos, blit.if not thenm dont. 
        draw.rect(screen, (100,100,100), photoSelectRect1)
    else:
        screen.blit(replyFirstPhoto, photoSelectRect1)
    if replySecondPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect2)
    else:
        screen.blit(replySecondPhoto, photoSelectRect2)
    if replyThirdPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect3)
    else:
        screen.blit(replyThirdPhoto, photoSelectRect3)
    if replyFourthPhoto==None:
        draw.rect(screen, (100,100,100), photoSelectRect4)
    else:
        screen.blit(replyFourthPhoto, photoSelectRect4)


##reply details

replyDetailsTexts = welcomeFont.render("Reply Details", True, BLACK)#make text objects and blit them
replyDetailsRects = Rect(size[0]/2-replyDetailsTexts.get_width()/2, surfaceBuffer, replyDetailsTexts.get_width(), replyDetailsTexts.get_height())



profilePicRects = Rect(surfaceBuffer, replyDetailsRects.bottom+10, 150,150)#make rects for the profile pi and the reply title
replyTitleRects = Rect(profilePicRects.x+profilePicRects.width+surfaceBuffer, profilePicRects.y, size[0] - profilePicRects.width-profilePicRects.x-surfaceBuffer*2, profilePicRects.height)

reportButt = Rect (size[0]/2 - buttonWidth[0]/2, size[1]-surfaceBuffer-buttonWidth[1], buttonWidth[0], buttonWidth[1])
reportButtText = largeButtonFont.render("Report", True, BLACK)#report button text and dimensions
reportButtTextRect = Rect(reportButt.x+reportButt.width/2-reportButtText.get_width()/2, reportButt.y+reportButt.height/2-reportButtText.get_height()/2, reportButtText.get_width(), reportButtText.get_height())

imageDisplaySurf = Surface((size[0]-surfaceBuffer*2, 120))
imageDisplaySurfRect = Rect(surfaceBuffer, reportButt.y - surfaceBuffer - 120, size[0]-surfaceBuffer*2, 120)

imageDisplaySurf.fill(WHITE)#fill display with white

replyBody = Rect(surfaceBuffer, replyTitleRects.bottom+ surfaceBuffer*2, size[0] - surfaceBuffer*2, imageDisplaySurfRect.y - surfaceBuffer*3 - replyTitleRects.bottom)
pArray=[]#photo array
parentReply=None#global arent reply will be used later for accessing data
pArrayRects=[]
#use
def startEleventhScreen(parent):
    global screenNumber
    global pArray
    global parentReply
    global pArrayRects
    global replyBody

    parentReply = parent
    screenNumber=11

#blitting
    screen.blit(backgroundImage, (0,0))
    screen.blit(leftArrow, leftArrowSurfaceRect)

    screen.blit(replyDetailsTexts, replyDetailsRects)

    draw.rect(screen, BUTTONCOLOR, reportButt)
    screen.blit(reportButtText, reportButtTextRect)
    
    if parentInstance.owner in existingUsers:
        #this means they're a user
        profPicURL = firebase.get("users/"+parent.owner, "profileURL")
    else:
        profPicURL = firebase.get("tutors/"+parent.owner, "profileURL")
    if profPicURL!=None:
        profPic = getImageFromURL(profPicURL)
        finalProfPic = transform.scale(profPic, (150,150))#blit them ikmage and username
        screen.blit(finalProfPic, profilePicRects)
        ownerText = minorFont.render(str(parent.owner), True, BLACK)
        oTextRect = Rect(profilePicRects.x+profilePicRects.width/2-ownerText.get_width()/2, profilePicRects.bottom+5, ownerText.get_width(), ownerText.get_height())
        screen.blit(finalProfPic, profilePicRects)
        screen.blit(ownerText, oTextRect)

    imageDisplaySurf.fill(WHITE)
    #gwet images to put in the imageDisplaySurf
    
    for item in range(len(parent.photos)):#iterate through photos and make an array
        ph = transform.scale(getImageFromURL(parent.photos[item]), (100,100))
        pArray.append(ph)
        pArrayRects.append(Rect(surfaceBuffer+110*item, 10, 100,100))
        imageDisplaySurf.blit(ph, (surfaceBuffer + 110*item, 10))

        
    screen.blit(imageDisplaySurf, imageDisplaySurfRect)

    #end get photos
    #draw text
    i=0
    fontSize=40
    titleText = parent.title
    #resizes font if text is too large for textbox 
    while True:
        if font.SysFont(fontString, fontSize).get_height()*2+4>replyTitleRects.height:
            fontSize-=1
        else:
            break
    textFont = font.SysFont(fontString, fontSize)
    textFont.set_underline(True)
    
    while textFont.size(titleText[:i])[0] < replyTitleRects.width-10 and i<len(titleText)-1:
        i+=1
    if titleText.rfind(" ", 0, i) != -1 and i<len(titleText)-2:
        print("splitting", i, len(titleText)-1)
        i = titleText.rfind(" ", 0, i+1)
    i+=1
    screen.blit(textFont.render(titleText[:i], True, BLACK), replyTitleRects)
    print("font decided")
    if i<len(titleText)-1 and len(titleText.strip())!=0:
        if textFont.size(titleText[i:])[0]>=replyTitleRects.width-10:
            j = len(titleText)-1
            while textFont.size(titleText[i:j])[0]>replyTitleRects.width-10+textFont.size("...")[0]:
                j-=1
            screen.blit(textFont.render(titleText[i:j]+"...", True, BLACK), (replyTitleRects.x, replyTitleRects.y+textFont.get_height()+4))
        else:
            screen.blit(textFont.render(titleText[i:], True, BLACK), (replyTitleRects.x, replyTitleRects.y+textFont.get_height()+4))
    else:
        replyTitleRects.height = replyTitleRects.height - textFont.get_height()-4
##check after the reply if the title for the posrt comes up right on svreen 9. this is wherte you pleft off at 7:11pm
    bodyText = str(parentReply.message)
    print(replyBody, bodyText)
    drawText(replyBody, bodyText, False, False)#blit body
    
    
                                   


def selectedRect(index, rectList, textList):#if rect is selected
    global screenNumber
    draw.rect(screen, GREEN, rectList[index],1)#make a green thing around the rect
    for item in range(len(rectList)):
        if (screenNumber==8 and item==1 and rectList[item]!= rectList[index]) or (screenNumber==10 and item==1 and rectList[item] != rectList[index]):#not body
            drawText(rectList[item], textList[item], False, False, largeButtonFont)
        elif rectList[item]!= rectList[index]:
            drawText(rectList[item], textList[item], False, True, largeButtonFont)#body
'''
error=False#this is a flag vbariable to indicate whether an error has been shown
def makeError(message):#will return an error button rect
    errorSurface = Surface(size[0],size[1])
    errorSurface.fill(BLACK)
    errorSurface.set_alpha(255//2)
    screen.blit(errorSurface, (0,0))
    draw.rect
'''
def makeError(title, message):
    tkMessageBox.showerror(title, message)#show error message
errorMade=False#flag variable to track errors
##algortihmic variables
keysActivate=False # this will let the computer know whether or not it should listen to key presses.
backspace = False # this will let us know whether or not the backspace key is being pressed.
keyPressed= False # this checks if there has been a key pressed
        
handActivate = False # flag to track if the flag cursor is being used

defaultArg = mouse.get_cursor()#regular cursor arguments
class Person():#person class - parent class to user and tutor
    def __init__(self, username, password, profileURL = None):
        self.username = username
        self.password = password
        self.profileURL = profileURL

class Tutor(Person):#tutor inherits from persn and adds am few extra properties
    def __init__(self, username, password, subjectDict, profileURL=None, verificationURL=None, verified=False):
        Person.__init__(self, username, password, profileURL)
        #assert bool(verified)#verified MUST BE A BOOL
        self.verified = verified
        self.subjectDict = subjectDict#WARNING BY ADDING THROUGH INIT THERE IS NO CASE CHECKER. ENTER IN ALL LOWERCASE
        self.verificationURL = verificationURL#possibly add a method to easily retrieve this image
        
    def addToSubject(self, subject, grade):#adds to subject array
        self.subjectDict[subject.lower()] = grade
class User(Person):#inherits from person and adds a few properties
    def __init__(self, username, password, subjectList, profileURL=None):
        Person.__init__(self, username, password, profileURL)
        self.subjects = [x.lower() for x in subjectList]#adds subjects with lowercase protection

    def addToSubject(self, subject):#add to subkects
        self.subjects.append(subject.lower())

class Post():#POST OBJECT 
    def __init__(self,message,time,title, replies, owner, status, subject, idNumber, photos=[], likes=0, likeMembers=[], liked=False, titleRect=None, profilePic=None):
        self.message = message#body
        self.time = time#time numbner since epoch
        self.title = title#title
        self.photos = photos#array of URLS
        self.replies = replies #array of reply objects reply ids
        self.owner = owner # who posted
        self.profilePic = profilePic
        self.status = status
        self.subject = subject #subject
        self.idNumber = idNumber #id
        self.likes = likes#get a list of who liked it. maybe put that in firebase instead. THIS IS WHERE YOU LEFT OFF. DEAL WITH COLLISION AND THE CHANGING OF ICONS. AFTER, CREATE THE QUESTION DETAILS SCREEN
        self.likeMembers = likeMembers#list of people
        self.liked = liked #bool that staates if it is currently liked
        self.titleRect = titleRect

    def upload(self, filenames=[]):#upload to firebase
        for name in range(len(filenames)):
            downloadURL = uploadPhotoToFirebase(filenames[name], "postPic", self.idNumber, name+1)
            self.photos.append(downloadURL)
        firebase.put("posts/"+str(self.idNumber), "title", self.title)
        firebase.put("posts/"+str(self.idNumber), "message", self.message)
        firebase.put("posts/"+str(self.idNumber), "owner", self.owner)
        firebase.put("posts/"+str(self.idNumber), "status", self.status)
        firebase.put("posts/"+str(self.idNumber), "subject", self.subject)
        firebase.put("posts/"+str(self.idNumber), "time", self.time)#FLOATING POINT NUMBER
        firebase.put("posts/"+str(self.idNumber), "likes", self.likes)
        firebase.put("posts/"+str(self.idNumber), "likeMembers", self.likeMembers)
        firebase.put("posts/"+str(self.idNumber), "replies", self.replies)
        if len(self.photos)!=0:
            firebase.put("posts/"+str(self.idNumber), "photos", self.photos)

    def uploadAsync(self, filenames=[]):#upload to firebase asynchronously
        def threadIt(filenames):
            for name in range(len(filenames)):
                downloadURL = uploadPhotoToFirebase(filenames[name], "postPic", self.idNumber, name+1)
                self.photos.append(downloadURL)
            firebase.put("posts/"+str(self.idNumber), "title", self.title)
            firebase.put("posts/"+str(self.idNumber), "message", self.message)
            firebase.put("posts/"+str(self.idNumber), "owner", self.owner)
            firebase.put("posts/"+str(self.idNumber), "status", self.status)
            firebase.put("posts/"+str(self.idNumber), "subject", self.subject)
            firebase.put("posts/"+str(self.idNumber), "time", self.time)#FLOATING POINT NUMBER
            firebase.put("posts/"+str(self.idNumber), "likes", self.likes)
            firebase.put("posts/"+str(self.idNumber), "likeMembers", self.likeMembers)
            print(self.likeMembers)
            firebase.put("posts/"+str(self.idNumber), "replies", self.replies)
            if len(self.photos)!=0:
                firebase.put("posts/"+str(self.idNumber), "photos", self.photos)
        threading.Thread(target = threadIt, args = [filenames]).start()
    def updateReplies(self):#update replies
        firebase.put("posts/"+str(self.idNumber), "replies", self.replies)
        print(self.replies)
    def updateRepliesAsync(self):#update asyncronously
        def t():
            firebase.put("posts/"+str(self.idNumber), "replies", self.replies)
        threading.Thread(target=t).start()

    #maybe implement an async method
        
class Replies():#replies object
    def __init__(self,message, time, title, owner, parentID, replyID, photos=[], likes=0, likeMembers=[], liked=False):
        self.message = message#message
        self.title = title#title
        self.time = time#time number
        self.photos = photos # array of URLS
        self.owner = owner #who replied
        self.parentID = parentID #the id number of the post
        self.replyID = replyID#replyID
        self.likes = likes#likes int
        self.likeMembers = likeMembers#;list of likers
        self.liked = liked#BOOL TO TELL WHETHER THE THING IS CURRENTLY LIKED BY THE OWNER
    def uploadReply(self, filenames):#upload to firebase
        for name in range(len(filenames)):
            downloadURL = uploadPhotoToFirebase(filenames[name], "replyPic", self.replyID, name+1)
            self.photos.append(downloadURL)
        if len(self.photos)!=0:
            firebase.put("replies/"+str(self.replyID), "photos", self.photos)
        firebase.put("replies/"+str(self.replyID), "message", self.message)
        firebase.put("replies/"+str(self.replyID), "title", self.title)
        firebase.put("replies/"+str(self.replyID), "owner", self.owner)
        firebase.put("replies/"+str(self.replyID), "parentID", self.parentID)
        firebase.put("replies/"+str(self.replyID), "likes", self.likes)
        firebase.put("replies/"+str(self.replyID), "likeMembers", self.likeMembers)
        firebase.put("replies/"+str(self.replyID), "time", self.time)
    def updateLikes(self):#update likes
        def do():
            firebase.put("replies/"+str(self.replyID), "likes", self.likes)
            firebase.put("replies/"+str(self.replyID), "likeMembers", self.likeMembers)
            
        threading.Thread(target = do).start()
        
    

def populateInstance(mode, instance):
    if mode=="tutor":
        subjectDictionary = firebase.get("tutors/"+instance.username+"/subjects", None)#fix dict to get rid of unicode thing
        tempDict = dict()#populate instance based on inputs from start 
        for item in subjectDictionary.keys():
            tempDict[str(item)] = subjectDictionary[item]
        instance.subjectDict = tempDict
        verifiedText = firebase.get("tutors/"+instance.username, "verified")
        instance.verified = str(verifiedText)
        verifiedurl = firebase.get("tutors/"+instance.username, "verificationURL")
        instance.verifiedURL = str(verifiedurl)
        profileurl = firebase.get("tutors/"+instance.username, "profileURL")
        instance.profileURL = str(profileurl)
        print(instance.verifiedURL, instance.profileURL, instance.verified, instance.username, instance.password, instance.subjectDict)

    elif mode=="users":#populate instance based on inputs from start 
        subjectDict = firebase.get("users/"+instance.username+"/subjects", None)
        finalSubjectArr = [str(x) for x in subjectDict]
        instance.subjects = finalSubjectArr
        profileurl = firebase.get("users/"+instance.username, "profileURL")
        instance.profileURL = str(profileurl)
        print(instance.profileURL, instance.username, instance.password, instance.subjects)
def getIDNumber():#get the next id number from firebase
    currentNumber = int(firebase.get("settings", "idNumber"))
    newNumber = currentNumber+1
    firebase.put("settings", "idNumber", newNumber)
    return newNumber
##person = Tutor("user", "pass", {})
##person.addToSubject("Physics", 95)
##print(person.subjectDict)
##print(person.username)
def uploadToFirebase(instance, mode):#upload instances to firebase
    global existingUsers
    global existingTutors
    if mode == "tutor":
        name = instance.username
        passw = instance.password
        firebase.put("tutors", name, {"password":passw})
        pushDict = instance.subjectDict
        firebase.put("tutors/"+name, "subjects", pushDict)
        existingTutors.append(name)
        firebase.put("settings/unverified", name, "True")
        '''
        for item in instance.subjectDict.items():
            firebase.put("tutors/"+name, "subjects", {item[0]:item[1]})
            print(item[0],item[1])
        '''
    elif mode == "users":
        name = instance.username
        passw = instance.password
        firebase.put("users", name, {"password":passw})
        pushList = instance.subjects
        firebase.put("users/"+name, "subjects", pushList)
        existingUsers.append(name)
    #define upload to fire base procedure


def isNumber(x):#check if its a number
    try:
        int(x)
        return True
    except:
        return False

def toSelectCursor():#make little arrow cursor (cursor bitmap stolen from pygame docs)
    global handActivate
    mouse.set_cursor((16, 16), (14, 1), (0, 0, 0, 6, 0, 30, 0, 124, 1, 252, 7, 248, 31, 248, 127, 240, 127, 240, 1, 224, 1, 224, 1, 192, 1, 192, 1, 128, 1, 128, 0, 0), (0, 7, 0, 31, 0, 127, 1, 254, 7, 254, 31, 252, 127, 252, 255, 248, 255, 248, 127, 240, 3, 240, 3, 224, 3, 224, 3, 192, 3, 192, 1, 128))
    handActivate = True

def toArrowCursor():#make default cursor
    global handActivate
    mouse.set_cursor(defaultArg[0], defaultArg[1], defaultArg[2], defaultArg[3])
    handActivate = False

def getReplyID():#get next reply id
    currentID = int(firebase.get("settings", "replyNumber"))
    currentID+=1
    def sendNewID(idN):
        firebase.put("settings", "replyNumber", idN)
    c_thread = threading.Thread(target=sendNewID, args=[currentID])
    c_thread.start()
    return currentID

def sendReport(idNumber):#report a post and put it in the database for review
    def t(idNumber):
        currentReport = firebase.get("settings/reports", None)
        if currentReport==None:
            currentReport=[]
        currentReport.append(idNumber)
        firebase.put("settings", "reports", currentReport)#this goes to the database for manual review. in the future, a helper propgram could be created for this task.
    threading.Thread(target = t, args=[idNumber]).start()


def sendReplyReport(idNumber):#report a reply
    def t(idNumber):
        currentReports = firebase.get("settings/replyReports", None)
        if currentReports==None:
            currentReports=[]
        currentReports.append(idNumber)
        firebase.put("settings", "reports", currentReports)
    threading.Thread(target = t, args=[idNumber]).start()
    
mode = ""#once you figure out who the user is, you can do it this way

currentPerson = None # this is where the class instance will go. It is in global scope

toNinth=False # used for tenth screen arrow
replyReport=False # flag to see if report button pressed
to9=False
to7=False
goToStart=False
startFirstScreen()
while running:
    leftClick,middleClick,rightClick=mouse.get_pressed()#get the  and right click events
    mx,my = mouse.get_pos()# get mouse position
    for evt in event.get():
        #print(evt)
        if evt.type==QUIT:
            running=False
        if evt.type==MOUSEBUTTONUP:
            if screenNumber==0:
                if goToStart:
                    startFirstScreen()
                    goToStart=False
            if screenNumber==1:
                if toTutor:# go to screen indicated by button on screen
                    buttonReset(tutorButtonRect, tutorTextBlock)
                    toTutor=False#reset flag
                    mode = "tutor" 
                    startSecondScreen()
                    print("totutor")
                elif toStudent:
                    buttonReset(personButtonRect, studentTextBlock)
                    toStudent=False
                    mode = "student"
                    startThirdScreen()
                    print("hfjc")
                elif toLogIn:
                    buttonReset(logInButtonRect, logInTextBlock)
                    toLogIn = False
                    startSixthScreen()
                    #startLog in screen
            elif screenNumber==2:
                if toNext:#go to next screen
                    buttonReset(continueButton2, continueText)
                    toNext=False
                    print("Blah")
                    #check this stuff for safety. throw error at user if any of this will fail.
                    if screenTwoTextArray[0]=="":#check if input is valid. if not throw error
                        makeError("Error", "Username must have content")
                        errorMade=True
                    if screenTwoTextArray[0] in existingTutors:
                        makeError("Error", "Username taken.")
                        errorMade=True
                    if screenTwoTextArray[1]=="":
                        makeError("Error", "Password must have content")
                        errorMade = True
                    currentPerson = Tutor(screenTwoTextArray[0], screenTwoTextArray[1], {})#make a person and make it current person
                    if screenTwoTextArray[2]!="" and isNumber(screenTwoTextArray[4]):
                        currentPerson.addToSubject(screenTwoTextArray[2], int(screenTwoTextArray[4]))
                    else:
                        if screenTwoTextArray[2]=="":#check for valid input
                            makeError("Error", "One field must be filled")
                            errorMade = True
                        elif isNumber(screenTwoTextArray[4])==False:
                            makeError("Error", "Must be a number")
                            errorMade = True
                    if screenTwoTextArray[3]!="" and isNumber(screenTwoTextArray[5]):
                        currentPerson.addToSubject(screenTwoTextArray[3], int(screenTwoTextArray[5]))#add to subject
                    if errorMade==False:
                        startFourthScreen() #go to next screen
                    errorMade=False
                                 
                    #cue the start fourth screen function here
            elif screenNumber==3:
                if toNext:
                    buttonReset(continueButton2, continueText)
                    toNext=False
                    print("Success!")
                    #check this stuff for safety. throw error at user if this will fail
                    currentPerson = User(screenThreeTextArray[0], screenThreeTextArray[1], [])
                    if screenThreeTextArray[0]=="":#make sure info entered is a valid input. if not, throw error
                        makeError("Error", "Username must be filled")
                        errorMade=True
                    if screenThreeTextArray[0] in existingUsers:
                        makeError("Error", "Username taken.")
                        errorMade=True
                    if screenThreeTextArray[1]=="":
                        makeError("Error", "Password must be filled")
                        errorMade=True
                    if screenThreeTextArray[2]!="":
                        currentPerson.addToSubject(screenThreeTextArray[2])#add to subject if there is ones
                    else:
                        makeError("Error", "First subject field must be filled")
                        errorMade=True
                    if screenThreeTextArray[3]!="":
                        currentPerson.addToSubject(screenThreeTextArray[3])
                    if not errorMade:
                        #uploadToFirebase(mode, currentPerson)
                        startFourthScreen()#go to next screen and disable keyboard
                        keysActivate=False
                        #screen.blit(backgroundImage, (0,0))#commount out later
                    errorMade=False
            elif screenNumber==4:
                if toNext:
                    errorMade=False
                    buttonReset(confirmButton, confirmText)
                    
                    if profilePictureName==None:#check if input was valid
                        makeError("Error!", "Please select a profile picture")
                        errorMade=True
                    if mode=="tutor":
                        if choosePhotoName==None:
                            makeError("Error!", "Please select a verification photo")#throw error
                            errorMade=True
                    if errorMade==False:
                        uploadToFirebase(currentPerson,mode)
                        uploadPhotoToFirebase(profilePictureName, "profilePic")#upload photos to firebase
                        if mode=="tutor":
                            uploadPhotoToFirebase(choosePhotoName, "verificationPic")
                            firebase.put("tutors/"+currentPerson.username, "verified", "False")
                            #firebase.put("settings/unverified", currentPerson.username, "True")
                        startFifthScreen()#start fifth screen
                    errorMade=False
                    toNext=False
                    #upload images to firebase
                    #startFourthScreen()
                    #cue the next screen
            elif screenNumber==6:#5 is skipped because its a transition. 
                if toNextSix:
                    buttonReset(continueButtonSix, continueButtonTextSix)
                    if screenSixTextArray[0] in existingUsers:
                        #auth for users
                        password = str(firebase.get("users/"+screenSixTextArray[0]+"/password", None))
                        if screenSixTextArray[1] != password:
                            makeError("Error!", "Invalid password (Case Sensitive)")
                        else:
                            #to the next screen AND POPULATE THE INSTANCE (FUNCTION)
                            currentPerson=User(screenSixTextArray[0], screenSixTextArray[1], [])
                            mode="users"
                            populateInstance(mode, currentPerson)
                            startSeventhScreen()
                    elif screenSixTextArray[0] in existingTutors:
                        #auth for tutors
                        password = str(firebase.get("tutors/"+screenSixTextArray[0]+"/password", None))
                        if screenSixTextArray[1] != password:
                            makeError("Error!", "Invalid password (Case Sensitive)")
                        else:
                            #to next screen AND POPULATE THE INSTANCE (FUNCTION)
                            currentPerson = Tutor(screenSixTextArray[0], screenSixTextArray[1], None)
                            mode="tutor"
                            populateInstance(mode, currentPerson)
                            startSeventhScreen()
                            
                    else:
                        makeError("Error!", "Invalid username (Case Sensitive)")
                    toNextSix=False
            elif screenNumber==7:
                likeClicked=False#reset flag
                
                
            elif screenNumber==8:
                if confirmPost:
                    buttonReset(postButton, postButtonText)
                    if eighthScreenTextArray[0]=="":#check for valid input. if invalid thgrow error
                        makeError("Error!", "Title must be filled")
                    elif eighthScreenTextArray[1]=="":
                        makeError("Error!", "Post must have details")
                    elif len(eighthScreenTextArray[1])<20:
                        makeError("Error!", "Post must be at least 20 characters long")
                    elif eighthScreenTextArray[2]=="":
                        makeError("Error!", "Subject must be filled")
                    else:
                        idNum = getIDNumber()#get id number and make a post object
                        filenames=[]
                        photos=[]
                        if finalFirstPhotoFile!=None:
                            filenames.append(finalFirstPhotoFile)
                            photos.append(finalFirstPhoto)
                        if finalSecondPhotoFile!=None:
                            filenames.append(finalSecondPhotoFile)
                            photos.append(finalSecondPhoto)
                        if finalThirdPhotoFile!=None:
                            filenames.append(finalThirdPhotoFile)
                            photos.append(finalThirdPhoto)
                        if finalFourthPhotoFile!=None:
                            filenames.append(finalFourthPhotoFile)
                            photos.append(finalFourthPhoto)
                        if len(photos)==0:
                            photos=None#get photos array
                        timeNumber = t.time()#this is time since epoch whcih on unix is Jan 1st 1970. Used on other platforms as well.
                        #append post object
                        currentPost = Post(eighthScreenTextArray[1], timeNumber, eighthScreenTextArray[0], [], currentPerson.username, "open", eighthScreenTextArray[2], idNum)
                        currentPost.upload(filenames)#upload to firebase
                        
                        startSeventhScreen()#start next screen
                    confirmPost=False
            elif screenNumber==9:
                if reportClicked:
                    reportClicked=False
                    makeError("Success", "Reported")

                    sendReport(parentID)
                    ####file report / add to database
                if likeClicked:
                    likeClicked=False#reset 
                if to7:
                    to7=False
                    startSeventhScreen()#to next screen (7th)
                
            elif screenNumber==10:
                if toNinth:
                    goToNinthScreen(parentInstance)#go to 9th screen
                if confirmedReply:
                    if len(tenthReplyTextList[0]) == 0:#check for valid input. 
                        makeError("Error!", "Title must be non empty")
                    elif len(tenthReplyTextList[1])<20:
                        makeError("Error!", "Details must be at least 20 characters")
                    else:
                        postID = getReplyID()#if valid, make reply object and add to database and local arrays. 
                        filenames=[]
                        photos=[]

                        if replyFirstPhoto!=None:
                            photos.append(replyFirstPhoto)
                            filenames.append(replyFirstPhotoFile)
                        if replySecondPhoto!=None:
                            photos.append(replySecondPhoto)
                            filenames.append(replySecondPhotoFile)
                        if replyThirdPhoto!=None:
                            photos.append(replyThirdPhoto)
                            filenames.append(replyThirdPhotoFile)
                        if replyFourthPhoto!=None:
                            photos.append(replyFourthPhoto)
                            filenames.append(replyFourthPhotoFile)
                        if len(photos)==0:
                            photos=[]
                            
                        timeNumber = t.time()#this is time since epoch whcih on unix is Jan 1st 1970. Used on other platforms as well.
                        replyInstance.message = tenthReplyTextList[1]
                        replyInstance.time = timeNumber
                        replyInstance.title = tenthReplyTextList[0]
                        replyInstance.owner = currentPerson.username
                        replyInstance.replyID = postID
                        #replyInstance.photos = photos
                        parentInstance.replies.append(postID)
                        print(parentInstance.replies)
                        replyInstance.uploadReply(filenames)
                        parentInstance.updateReplies()#throw to database
                        goToNinthScreen(parentInstance)
                        '''
                        currentPost = Post(eighthScreenTextArray[1], timeNumber, eighthScreenTextArray[0], [], currentPerson.username, "open", eighthScreenTextArray[2], idNum)
                        currentPost.upload(filenames)
                        startSeventhScreen()
                        '''

                    #buttonReset(replyConfirm, replyText)
                    confirmedReply=False#reset
                    
                    #populate classes and upload here
                    #getIDNumber()
            if screenNumber==11:
                if replyReport==True:
                    replyReport==False
                    sendReplyReport(parentReply.replyID)
                    makeError("Success", "Reported Successfully")#report and send to firebase for human review
                    buttonReset(reportButt, reportButtText)
                if to9:
                    to9==False
                    goToNinthScreen(parentInstance)


                    
        if evt.type==MOUSEBUTTONDOWN:
            if evt.button==4:#scrolling up
                if screenNumber==7:
                    print(maxScroll)
                    if postSurfaceRect.collidepoint(mx,my) and postArrayRects[-1].y>maxScroll:#control scrolling.
                        print(postArrayRects[0].y, maxScroll)#if the top object goes too faer, dont let it scroll. If it starts to slide down to far, dont let it scroll. clamp in range
                        postSurface.fill(WHITE)
                        for item in range(len(postArrayRects)):
                            postArrayRects[item].y-=6
                            postSurface.blit(postArray[item], postArrayRects[item])#blit
                        screen.blit(postSurface, postSurfaceRect)
                        draw.rect(screen, WHITE, postSurfaceTitleBRect)
                        screen.blit(postSurfaceTitle, postSurfaceTitleRect)
                elif screenNumber==9:
                    print(repliesRects[-1].y, maxReplyScroll)
                    if postRepliesSurfaceRect.collidepoint(mx,my) and repliesRects[-1].y>maxReplyScroll:
                        print("COLLIDED")
                        postRepliesSurface.fill((200,200,200))
                        for item in range(len(repliesRects)):
                            repliesRects[item].y-=6
                            postRepliesSurface.blit(repliesSurfaces[item], repliesRects[item])#blit
                        screen.blit(postRepliesSurface, postRepliesSurfaceRect)

            if evt.button==5:#scrolling down
                if screenNumber==7:
                    if postSurfaceRect.collidepoint(mx,my) and postArrayRects[-1].y<top:
                        postSurface.fill(WHITE)
                        print(top)
                        for item in range(len(postArrayRects)):
                            postArrayRects[item].y+=6
                            postSurface.blit(postArray[item], postArrayRects[item])#blit
                        screen.blit(postSurface, postSurfaceRect)
                        draw.rect(screen, WHITE, postSurfaceTitleBRect)
                        screen.blit(postSurfaceTitle, postSurfaceTitleRect)
                elif screenNumber==9:
                    print(repliesRects[-1].y, replyTop)
                    if postRepliesSurfaceRect.collidepoint(mx,my) and repliesRects[-1].y<replyTop:
                        postRepliesSurface.fill((200,200,200))
                        for item in range(len(repliesRects)):
                            repliesRects[item].y+=6
                            postRepliesSurface.blit(repliesSurfaces[item], repliesRects[item])#blit
                        screen.blit(postRepliesSurface, postRepliesSurfaceRect)
                        
                
        if evt.type==KEYDOWN:
            if keysActivate:
                keys= key.get_pressed()#returns all of the key codes in a dictionary
                if keys[8]==1:#if backspace
                    backspace=True
                else:
                    keyPressed=True
                    for item in range(33,256,1):#key generating function
                        if keys[item]==1 and item!=304:
                            if (item<48 or item>122) and symbolsAllowed==False:
                                makeError("Error!", "Symbols and spaces not permitted")
                            elif (keys[304]==1 or keys[303]==1) and (item>48 and item<122):
                                #this means its capital
                                typedLetters+=chr(item-32)#ascii to english
                            elif (keys[304]==1 or keys[303]==1) and (item<48 or item>122):
                                if symbolsAllowed==False:
                                    makeError("Error!", "Symbols and spaces not permitted")
                                else:
                                    print("Yes!")
                                    if item==48:#checks all symbols and adds them to the typesdLetters. font doesnt support some symbols - can be changed at later date
                                        typedLetters+=")"
                                    elif item==49:
                                        typedLetters+="!"
                                    elif item==50:
                                        typedLetters+="@"
                                    elif item==51:
                                        typedLetters+="#"
                                    elif item==52:
                                        typedLetters+="$"
                                    elif item==53:
                                        typedLetters+="%"
                                    elif item==54:
                                        typedLetters+="^"
                                    elif item==55:
                                        typedLetters+="&"
                                    elif item==56:
                                        typedLetters+="*"
                                    elif item==57:
                                        typedLetters+="("
                                    elif item==47:
                                        typedLetters+="?"
                                    elif item==44:
                                        typedLetters+="<"
                                    elif item==46:
                                        typedLetters+=">"
                                    elif item==59:
                                        typedLetters+=":"
                                    elif item==91:
                                        typedLetters+="{"
                                    elif item==93:
                                        typedLetters+="}"
                                    elif item==92:
                                        typedLetters+="|"
                                    elif item==96:
                                        typedLetters+="~"
                                    elif item==45:
                                        typedLetters+="_"
                            else:
                                typedLetters+=chr(item)
                            print(typedLetters)
                    if enterEnabled:
                        if keys[13]==1 and (textIndex8==1 or (screenNumber==10 and textIndex10==1)):#add a newline if enter pressed
                            typedLetters+="\n"
                    if spaceEnabled:
                        if keys[32]==1:
                            typedLetters+=" "#add spaces if they exist
                if screenNumber==2 and (keyPressed or backspace):#FOR ALL LINES BELOW chaneg the respective string of the screen's text array. handle backspaces, and backspace extra if there is a \n. these lines are the same all the way down, just diff variable names

                    screenTwoTextArray[textIndex2] = screenTwoTextArray[textIndex2] + typedLetters
                    if backspace:
                        screenTwoTextArray[textIndex2] = screenTwoTextArray[textIndex2][:-1]
                    if textIndex2==0:
                        drawText(usernameTextFieldRect, screenTwoTextArray[textIndex2])#COULD CONDENSE LATER 
                    elif textIndex2==1:
                        drawText(passwordTextFieldRect, screenTwoTextArray[textIndex2])
                    elif textIndex2==2:
                        drawText(subjectOneTextField, screenTwoTextArray[textIndex2])
                    elif textIndex2==3:
                        drawText(subjectTwoTextField, screenTwoTextArray[textIndex2])
                    elif textIndex2==4:
                        drawText(gradeOneTextField, screenTwoTextArray[textIndex2])
                    elif textIndex2==5:
                        drawText(gradeTwoTextField, screenTwoTextArray[textIndex2])# this is your next step. Here this is where you will copy the text to the screen.
                elif screenNumber==3 and (keyPressed or backspace):
                    screenThreeTextArray[textIndex3] = screenThreeTextArray[textIndex3] + typedLetters
                    if backspace:
                        screenThreeTextArray[textIndex3] = screenThreeTextArray[textIndex3][:-1]
                    if textIndex3==0:
                        drawText(usernameTextFieldRect, screenThreeTextArray[textIndex3])
                    elif textIndex3==1:
                        drawText(passwordTextFieldRect, screenThreeTextArray[textIndex3])
                    elif textIndex3==2:
                        drawText(userSubjectOneTextField, screenThreeTextArray[textIndex3])
                    elif textIndex3==3:
                        drawText(userSubjectTwoTextField, screenThreeTextArray[textIndex3])
                elif screenNumber==6 and (keyPressed or backspace):
                    screenSixTextArray[textIndex6] = screenSixTextArray[textIndex6] + typedLetters
                    if backspace:
                        screenSixTextArray[textIndex6] = screenSixTextArray[textIndex6][:-1]
                    if textIndex6==0:
                        drawText(usernameTextFieldRectSix, screenSixTextArray[textIndex6])
                    elif textIndex6==1:
                        drawText(passwordTextFieldRectSix, screenSixTextArray[textIndex6])
                elif screenNumber==8 and (keyPressed or backspace):
                    eighthScreenTextArray[textIndex8] += typedLetters
                    if backspace:
                        if len(eighthScreenTextArray[textIndex8])>=2:
                            if textIndex8==1 and eighthScreenTextArray[textIndex8][-2]=="\n":
                                print("Yes!")
                                eighthScreenTextArray[textIndex8] = eighthScreenTextArray[textIndex8][:-2]
                            else:
                                eighthScreenTextArray[textIndex8] = eighthScreenTextArray[textIndex8][:-1]
                        else:
                            eighthScreenTextArray[textIndex8] = eighthScreenTextArray[textIndex8][:-1]
                    if textIndex8==0:
                        drawText(eighthScreenTextList[textIndex8], eighthScreenTextArray[textIndex8])
                    elif textIndex8==1:
                        drawText(eighthScreenTextList[textIndex8], eighthScreenTextArray[textIndex8], True, False)
                    elif textIndex8==2:
                        drawText(eighthScreenTextList[textIndex8], eighthScreenTextArray[textIndex8])
                elif screenNumber==10 and (keyPressed or backspace):
                    tenthReplyTextList[textIndex10]+=typedLetters
                    if backspace:
                        if len(tenthReplyTextList[textIndex10])>=1:
                            if textIndex10==1 and tenthReplyTextList[textIndex10]=="\n":
                                tenthReplyTextList[textIndex10] = tenthReplyTextList[textIndex10][:-2]
                        if len(tenthReplyTextList[textIndex10])>=1:
                            tenthReplyTextList[textIndex10] = tenthReplyTextList[textIndex10][:-1]
                            
                    if textIndex10==0:
                        drawText(tenthReplyTextArray[textIndex10], tenthReplyTextList[textIndex10])
                        selectedRect(textIndex10, tenthReplyTextArray, tenthReplyTextList)
                    elif textIndex10==1:
                        drawText(tenthReplyTextArray[textIndex10], tenthReplyTextList[textIndex10], False, False)
                        selectedRect(textIndex10, tenthReplyTextArray, tenthReplyTextList)
                    
                backspace=False #reset
                keyPressed=False #reset
    
            #mouse released
    #screen.fill(MYYELLOW)#background
    
    if screenNumber==0:
        if leftClick==1:
            if continBut.collidepoint(mx,my) and goToStart==False:
                clickedButton(continBut, continText)
                goToStart=True
                
    if screenNumber==1:
        if leftClick==1:
        #this is the  code the system will run for the first screen
            #print("yes")
        #tutorButtonListener
            if tutorButtonRect.collidepoint(mx,my) and toTutor==False:
                print("clicked")#control button clicks and trigger flags to go to right screen
                clickedButton(tutorButtonRect, tutorTextBlock)
                toTutor=True
            if personButtonRect.collidepoint(mx,my) and toStudent==False:
                print("Clicked")
                clickedButton(personButtonRect, studentTextBlock)
                toStudent=True
            if logInButtonRect.collidepoint(mx,my) and toLogIn==False:
                clickedButton(logInButtonRect, logInTextBlock)
                toLogIn=True
            if questionMarkRect.collidepoint(mx,my):
                instructions()
    elif screenNumber==2:
        if leftClick==1:
            if continueButton2.collidepoint(mx,my) and toNext==False:
                print("toNext")#control button clicks and trigger flags to go to the right screen
                clickedButton(continueButton2, continueText)
                toNext=True
            if usernameTextFieldRect.collidepoint(mx,my):
                textIndex2=0
                selectedRect(textIndex2, screenTwoTextList, screenTwoTextArray)
                keysActivate=True
            if passwordTextFieldRect.collidepoint(mx,my):
                textIndex2=1
                selectedRect(textIndex2, screenTwoTextList, screenTwoTextArray)
                keysActivate=True
            if subjectOneTextField.collidepoint(mx,my):
                textIndex2=2
                selectedRect(textIndex2, screenTwoTextList, screenTwoTextArray)
                keysActivate=True
            if subjectTwoTextField.collidepoint(mx,my):
                textIndex2=3
                selectedRect(textIndex2, screenTwoTextList, screenTwoTextArray)
                keysActivate=True
            if gradeOneTextField.collidepoint(mx,my):
                textIndex2=4
                selectedRect(textIndex2, screenTwoTextList, screenTwoTextArray)
                keysActivate=True
            if gradeTwoTextField.collidepoint(mx,my):
                textIndex2=5
                selectedRect(textIndex2, screenTwoTextList, screenTwoTextArray)
                keysActivate=True
            if leftArrowSurfaceRect.collidepoint(mx,my):
                startFirstScreen()
                screenTwoTextArray=["","","","","",""]#reset the text and go back to the first screen
                keysActivate=False
    elif screenNumber==3:
        if leftClick==1:
            if continueButton2.collidepoint(mx,my) and toNext==False:
                print("toNext")
                clickedButton(continueButton2, continueText)
                toNext=True
            if usernameTextFieldRect.collidepoint(mx,my):
                textIndex3=0
                selectedRect(textIndex3, screenThreeTextList, screenThreeTextArray)
                keysActivate=True
            if passwordTextFieldRect.collidepoint(mx,my):
                textIndex3=1
                selectedRect(textIndex3, screenThreeTextList, screenThreeTextArray)
                keysActivate=True
            if userSubjectOneTextField.collidepoint(mx,my):
                textIndex3=2
                selectedRect(textIndex3, screenThreeTextList, screenThreeTextArray)
                keysActivate=True
            if userSubjectTwoTextField.collidepoint(mx,my):
                textIndex3=3#Ehandle button presses and go to the correctm screen/ handle typing into the right box
                selectedRect(textIndex3, screenThreeTextList, screenThreeTextArray)
                keysActivate=True
            if leftArrowSurfaceRect.collidepoint(mx,my):
                startFirstScreen()
                screenThreeTextArray=["","","",""]#go back to first screen and reset strings
                keysActivate=False
    elif screenNumber==4:
        if leftClick==1:
            if confirmButton.collidepoint(mx,my) and toNext==False:
                toNext=True#check button click and send to right screen
                clickedButton(confirmButton, confirmText)
                #this means it should move on
            if profilePictureSurfaceRect.collidepoint(mx,my):
                profilePictureName = tkFileDialog.askopenfilename(filetypes=[("Images","*.png; *.bmp; *.jpg; *.jpeg")])#tkinter file load window
                if profilePictureName!='':#load photo from a file name
                    profilePicture = image.load(profilePictureName)
                    profilePictureSurface.fill(WHITE)
                    tranformedPic = transform.scale(profilePicture, (profilePictureSurface.get_height()*profilePicture.get_width()/profilePicture.get_height(), profilePictureSurface.get_height()))
                    profilePictureSurface.blit(tranformedPic, ((profilePictureSurface.get_width() - tranformedPic.get_width())/2, 0))
                    screen.blit(profilePictureSurface, profilePictureSurfaceRect)
            if choosePhotoRect.collidepoint(mx,my) and mode=="tutor":
                choosePhotoName = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#tkinter file load box
                if choosePhotoName!='':#get photo and load it into the program
                    choosePhoto = image.load(choosePhotoName)
                    choosePhotoSurface.fill(WHITE)
                    transformedPicture = transform.scale(choosePhoto, (choosePhotoSurface.get_height()*choosePhoto.get_width()/choosePhoto.get_height(), choosePhotoSurface.get_height()))
                    choosePhotoSurface.blit(transformedPicture, ((choosePhotoSurface.get_width() - choosePhotoSurface.get_width())/2, 0))
                    screen.blit(choosePhotoSurface, choosePhotoRect)
            if leftArrowSurfaceRect.collidepoint(mx,my):
                if mode=="users":
                    startThirdScreen()#go back to respective screen if asked
                    for field in range(len(screenThreeTextList)):
                        drawText(screenThreeTextList[field], screenThreeTextArray[field], largeButtonFont, False)
                elif mode=="tutor":
                    startSecondScreen()
                    for field in range(len(screenTwoTextList)):
                        drawText(screenTwoTextList[field], screenTwoTextArray[field], largeButtonFont, False)
                            
    elif screenNumber==5:
       offset+=increment
       startFifthScreen(offset)
       if offset >= totalIncrement:
           startSeventhScreen()#incrememnt the animation and then go to seventh screen when done
           #screenNumber=5.5 # cue the fifth screen. exit scope of animation
    elif screenNumber==6:
        if leftClick==1:
            if usernameTextFieldRectSix.collidepoint(mx,my):
                textIndex6 = 0
                selectedRect(textIndex6, screenSixTextList, screenSixTextArray)
                keysActivate=True
            if passwordTextFieldRectSix.collidepoint(mx,my):
                textIndex6=1
                selectedRect(textIndex6, screenSixTextList, screenSixTextArray)#check clicks and make sure text is being handled into the right box
                keysActivate=True
            if continueButtonSix.collidepoint(mx,my):
                toNextSix=True
                clickedButton(continueButtonSix, continueButtonTextSix)
            if leftArrowSurfaceRect.collidepoint(mx,my):
                startFirstScreen()
                screenSixTestArray=["",""]
                keysActivate6=False
    elif screenNumber==7:
        likeCollided=False
        if plusImageRect.collidepoint(mx,my):
            likeCollided=True
            if leftClick==1:#check key presses and make sure the user goes to the right screen
                startEighthScreen()
                likeCollided=False
        if logOutWordsRect.collidepoint(mx,my):
            likeCollided=True
            if leftClick==1:
                currentPerson=None
                makeError("Success.", "You have successfully logged out. Please restart/close the app")
                screen.blit(backgroundImage, (0,0))#if logged out, log out and cue user to close the app.
                te=welcomeFont.render("Please Close the Program", True, BLACK)
                screen.blit(te, (size[0]/2-te.get_width()/2, size[1]/2-te.get_height()/2))



                
                likeCollided=False
        
                '''
                choosePhotoSurface.fill(WHITE)
                transformedPicture = transform.scale(choosePhoto, (choosePhotoSurface.get_height()*choosePhoto.get_width()/choosePhoto.get_height(), choosePhotoSurface.get_height()))
                choosePhotoSurface.blit(transformedPicture, ((choosePhotoSurface.get_width() - choosePhotoSurface.get_width())/2, 0))
                screen.blit(choosePhotoSurface, choosePhotoRect)
                '''
        
        for item in range(len(postArrayRects)):
            #print(mx-postSurfaceRect.x, my-postSurfaceRect.y-postArrayRects[item].y)
            if likesRect.collidepoint(mx-postSurfaceRect.x, my-postSurfaceRect.y-postArrayRects[item].y):#iterate through the posts and then check if like was collided with
                likeCollided=True
                if leftClick==1:
                    if currentPerson.username not in postInstances[item].likeMembers and likeClicked==False:#if it wasnt liked
                        postInstances[item].likes+=1#add one to the likes, put that in the instance and datrabse, and then blit the proper icon 
                        postInstances[item].likeMembers.append(currentPerson.username)
                        postInstances[item].liked=True
                        likeClicked=True
                        draw.rect(postArray[item], (122,122,122), likesRect)
                        likesText = minorFont.render("Likes:%i"%(postInstances[item].likes), True, (200,200,200))
                        likesTextRect = Rect(likesRect.x+likesRect.width/2-likesText.get_width()/2, likesRect.y+likesRect.height+5, likesText.get_width(), likesText.get_height())
                        draw.rect(postArray[item], (122,122,122), likesTextRect)
                        postArray[item].blit(likeFilled, likesRect)
                        postArray[item].blit(likesText, likesTextRect)
                        postSurface.fill(WHITE)
                        for item in range(len(postArrayRects)):
                            postSurface.blit(postArray[item], postArrayRects[item])
                        screen.blit(postSurface, postSurfaceRect)
                        draw.rect(screen, WHITE, postSurfaceTitleBRect)
                        screen.blit(postSurfaceTitle, postSurfaceTitleRect)
                        postInstances[item].uploadAsync()#asynchronously upload
                        print("happened")
                        
                        
                    elif likeClicked==False:#if it was liked
                        postInstances[item].likes-=1#remove a like, reflect that in the instance, and upload it to the database
                        postInstances[item].likeMembers.remove(currentPerson.username)
                        postInstances[item].liked=False
                        print("unliked")
                        likeClicked=True
                        
                        draw.rect(postArray[item], (122,122,122), likesRect)
                        likesText = minorFont.render("Likes:%i"%(postInstances[item].likes), True, (200,200,200))
                        likesTextRect = Rect(likesRect.x+likesRect.width/2-likesText.get_width()/2, likesRect.y+likesRect.height+5, likesText.get_width(), likesText.get_height())
                        draw.rect(postArray[item], (122,122,122), likesTextRect)
                        postArray[item].blit(likeUnfilled, likesRect)
                        postArray[item].blit(likesText, likesTextRect)
                        postSurface.fill(WHITE)
                        for item in range(len(postArrayRects)):
                            postSurface.blit(postArray[item], postArrayRects[item])
                        screen.blit(postSurface, postSurfaceRect)
                        draw.rect(screen, WHITE, postSurfaceTitleBRect)
                        screen.blit(postSurfaceTitle, postSurfaceTitleRect)
                        postInstances[item].uploadAsync()
            if postInstances[item].titleRect.collidepoint(mx-postSurfaceRect.x, my-postSurfaceRect.y-postArrayRects[item].y):
                likeCollided=True
                if leftClick==1:
                    likeCollided=False
                    goToNinthScreen(postInstances[item])#go to the ninth screen and pass through thism instance
        if photoSelectImageRect.collidepoint(mx,my):
            likeCollided=True
            if leftClick==1:
                chooseProfilePhotoName = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#ask to open the file and get the filename
                if chooseProfilePhotoName!='':
                    chooseProfilePhoto = image.load(chooseProfilePhotoName)
                    
                    uploadPhotoToFirebase(chooseProfilePhotoName, "profilePic")
                    if currentPerson.__class__.__name__ == "Tutor":#upload the photo to firebase and empty out the lists
                        uploadToFirebase(currentPerson, "tutors")
                    else:
                        uploadToFirebase(currentPerson, "user")
                    postArray=[]
                    postArrayRects=[]
                    postInstances=[]
                    numbersIncluded=[]
                    startSeventhScreen()
                
        if likeCollided==False and handActivate:
            toArrowCursor()#change cursor to little arrow
        elif likeCollided and handActivate==False:
            toSelectCursor()#change cursor to select thing
                


    elif screenNumber==8:
        if leftClick==1:
            if postButton.collidepoint(mx,my):#check clicks and go to right screen
                clickedButton(postButton, postButtonText)
                confirmPost=True
            if messageTextFieldRect.collidepoint(mx,my):
                keysActivate=True
                textIndex8=1
                selectedRect(textIndex8, eighthScreenTextList, eighthScreenTextArray)
            if questionTextFieldRect.collidepoint(mx,my):
                keysActivate=True
                textIndex8=0#text boxes - detect which one is currently selected
                selectedRect(textIndex8, eighthScreenTextList, eighthScreenTextArray)
            if photoSelectRect1.collidepoint(mx,my):
                finalFirstPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#load image and upload to firebase/blit to screen if needed
                if finalFirstPhotoFile!='':
                    firstPhoto = image.load(finalFirstPhotoFile)
                    aRatio1 = firstPhoto.get_width()/firstPhoto.get_height() #*height = width
                    finalFirstPhoto = transform.scale(firstPhoto, (photoSelectRect1.height*aRatio1, photoSelectRect1.height))
                    startEighthScreen()
                    for item in range(len(eighthScreenTextList)):
                        if item!=1:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, True)#draw the text
                        else:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, False)
                
                
            if photoSelectRect2.collidepoint(mx,my):
                finalSecondPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#photo select (same as above
                if finalSecondPhotoFile!='':
                    secondPhoto = image.load(finalSecondPhotoFile)
                    aRatio2 = secondPhoto.get_width()/secondPhoto.get_height()
                    finalSecondPhoto = transform.scale(secondPhoto, (photoSelectRect2.height*aRatio2, photoSelectRect2.height))
                    startEighthScreen()
                    for item in range(len(eighthScreenTextList)):
                        if item!=1:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, True)
                        else:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, False)
                
                
            if photoSelectRect3.collidepoint(mx,my):
                finalThirdPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#photoselect (same as above)
                if finalThirdPhotoFile!='':
                    thirdPhoto = image.load(finalThirdPhotoFile)
                    aRatio3 = thirdPhoto.get_width()/thirdPhoto.get_height()
                    finalThirdPhoto = transform.scale(thirdPhoto, (photoSelectRect3.height*aRatio3, photoSelectRect3.height))
                    startEighthScreen()
                    for item in range(len(eighthScreenTextList)):
                        if item!=1:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, True)
                        else:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, False)
                
                
            if photoSelectRect4.collidepoint(mx,my):
                finalFourthPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#photo select (same as above)
                if finalFourthPhotoFile!='':
                    fourthPhoto = image.load(finalFourthPhotoFile)
                    aRatio4 = fourthPhoto.get_width()/fourthPhoto.get_height()#get the aspect ratio - make sure that the photo doesnt look stretched or compressed
                    finalFourthPhoto = transform.scale(fourthPhoto, (photoSelectRect4.height*aRatio4, photoSelectRect4.height))
                    startEighthScreen()#go to eighth screen
                    for item in range(len(eighthScreenTextList)):
                        if item!=1:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, True)
                        else:
                            drawText(eighthScreenTextList[item], eighthScreenTextArray[item], False, False)
            if subjectTextField.collidepoint(mx,my):
                textIndex8=2
                keysActivate=True
                selectedRect(textIndex8, eighthScreenTextList, eighthScreenTextArray)#select the rectangle and then add it to the text list
                print(mx+postSurfaceRect.x+likesRect.x, my+postSurfaceRect.y+likesRect.y)
            

                
            if leftArrowSurfaceRect.collidepoint(mx,my):
                startSeventhScreen()#go to the 7th screen
    if screenNumber==9:
        hoverBool=False
        if plusImageRect.collidepoint(mx,my):
            hoverBool=True
            if leftClick==1:
                startTenthScreen(parentID)#go to 10th screen
                hoverBool=False
        if reportButtonRect.collidepoint(mx-postDetailsSurfaceRect.x, my-postDetailsSurfaceRect.y):
            hoverBool=True
            if leftClick==1:
                clickedButton(reportButtonRect, reportButtonText, surface = postDetailsSurface)
                screen.blit(postDetailsSurface,postDetailsSurfaceRect)#start the reporting process
                reportClicked = True
        for itemt in range(len(imageViewArrayRects)):
            if imageViewArrayRects[itemt].collidepoint(mx-imageViewSurfaceRect.x-postDetailsSurfaceRect.y, my-imageViewSurfaceRect.y-postDetailsSurfaceRect.y):
                url = parentInstance.photos[itemt]
                f = open(parentInstance.idNumber+"_"+str(itemt)+".jpg",'wb')#download images from url to harddrive
                f.write(requests.get(url).content)
                f.close()
                makeError("Success", "downloaded image")
        if postLikeButtonRect.collidepoint(mx-postDetailsSurfaceRect.x, my-postDetailsSurfaceRect.y):
            hoverBool=True
            if leftClick==1:
                 if currentPerson.username not in parentInstance.likeMembers and likeClicked==False:#if the post is already not liked
                    parentInstance.likes+=1#add a like, add to like members, reflect this in the instance, blit the right icon to the nscreen and upload asynchronously
                    parentInstance.likeMembers.append(currentPerson.username)
                    parentInstance.liked=True
                    draw.rect(postDetailsSurface, (200,200,200), postLikeButtonRect)
                    postDetailsSurface.blit(likeFilled, postLikeButtonRect)

                    print(likesTextsRect)
                    draw.rect(postDetailsSurface, (200,200,200), likesTextsRect)
                    tex = minorFont.render("Likes: %i"%(parentInstance.likes), True, (128,128,128))
                    postDetailsSurface.blit(tex, likesTextsRect)

                    screen.blit(postDetailsSurface, postDetailsSurfaceRect)

                    parentInstance.uploadAsync()
                    likeClicked=True

                    
                 elif likeClicked==False:#if it wadnt liked
                    parentInstance.likes-=1#remove a like, reflect it in the instance, upload to database, blit right iumage
                    parentInstance.likeMembers.remove(currentPerson.username)
                    parentInstance.liked=True
                    draw.rect(postDetailsSurface, (200,200,200), postLikeButtonRect)
                    postDetailsSurface.blit(likeUnfilled, postLikeButtonRect)

                    draw.rect(postDetailsSurface, (200,200,200), likesTextsRect)
                    t = minorFont.render("Likes: %i"%(parentInstance.likes), True, (128,128,128))
                    postDetailsSurface.blit(t, likesTextsRect)

                    screen.blit(postDetailsSurface, postDetailsSurfaceRect)

                    parentInstance.uploadAsync()
                    likeClicked=True
                
        if leftArrowSurfaceRect.collidepoint(mx,my):
            hoverBool = True
            if leftClick==1:#go to the 7th screen
                to7=True
                hoverBool = False
        for rects in range(len(repliesRects)):#iterate through the replies
            if repliesTitleRectangle.collidepoint(mx-postRepliesSurfaceRect.x-repliesRects[rects].x, my-postRepliesSurfaceRect.y-repliesRects[rects].y):
                hoverBool=True
                print("REPLY TITLE COLLIDE")
                if leftClick==1:
                    startEleventhScreen(repliesObjects[rects])#go to the replies details screen if user presses on reply title
            if repliesLikeIconRect.collidepoint(mx-postRepliesSurfaceRect.x-repliesRects[rects].x, my-postRepliesSurfaceRect.y-repliesRects[rects].y):
                hoverBool=True
                #print("LIKECOLLIDE")
                if leftClick==1:
                    if str(repliesObjects[rects].liked)=="False" and likeClicked==False:#if the reply is not liked, then like it
                        likeClicked=True
                        print("like!")
                        repliesObjects[rects].liked="True"#it is liked and then add a like to the instance. Put in database and blit
                        repliesObjects[rects].likes = repliesObjects[rects].likes+1
                        repliesObjects[rects].likeMembers.append(currentPerson.username)
                        draw.rect(repliesSurfaces[rects], (128,128,128), repliesLikeIconRect)#check the make replies for logic relating to displaying filled/unfilled thumbs for likes
                        repliesSurfaces[rects].blit(likeFilled, repliesLikeIconRect)
                        draw.rect(repliesSurfaces[rects], (128,128,128), (repliesLikesTextsRects.x-10, repliesLikesTextsRects.y, repliesLikesTextsRects.width+20, repliesLikesTextsRects.height))
                        drawerText = minorFont.render("Likes: %i"%(repliesObjects[rects].likes), True, (200,200,200))
                        repliesSurfaces[rects].blit(drawerText, repliesLikesTextsRects)
                        postRepliesSurface.blit(repliesSurfaces[rects], repliesRects[rects])
                        screen.blit(postRepliesSurface, postRepliesSurfaceRect)
                        repliesObjects[rects].updateLikes()
                    elif likeClicked==False and str(repliesObjects[rects].liked)=="True" :##if liked
                        likeClicked=True
                        print("unliked!")
                        repliesObjects[rects].liked="False"#take off a like and reflect that in the instance. upload and then blit the iucon
                        repliesObjects[rects].likes = repliesObjects[rects].likes-1
                        print(repliesObjects[rects].likeMembers, repliesObjects[rects].liked, repliesObjects[rects].title)
                        repliesObjects[rects].likeMembers.remove(currentPerson.username)
                        draw.rect(repliesSurfaces[rects], (128,128,128), repliesLikeIconRect)#check the make replies for logic relating to displaying filled/unfilled thumbs for likes
                        repliesSurfaces[rects].blit(likeUnfilled, repliesLikeIconRect)
                        draw.rect(repliesSurfaces[rects], (128,128,128), (repliesLikesTextsRects.x-10, repliesLikesTextsRects.y, repliesLikesTextsRects.width+20, repliesLikesTextsRects.height))
                        drawerText = minorFont.render("Likes: %i"%(repliesObjects[rects].likes), True, (200,200,200))
                        repliesSurfaces[rects].blit(drawerText, repliesLikesTextsRects)
                        postRepliesSurface.blit(repliesSurfaces[rects], repliesRects[rects])
                        screen.blit(postRepliesSurface, postRepliesSurfaceRect)
                        repliesObjects[rects].updateLikes()


        
        if hoverBool:#change cursor if hovering over selectable object
            toSelectCursor()
        else:
            toArrowCursor()
    if screenNumber==10:
        if leftClick==1:
            if leftArrowSurfaceRect.collidepoint(mx,my):
                toNinth=True#go to 9th screen#control which text box is selected. if the body is selected, enable enter key. otherwise, ebnale the symbols and spaces
                
            if tenthReplyTextArray[0].collidepoint(mx,my):
                textIndex10=0
                keysActivate=True
                symbolsAllowed=True
                enterEnabled=False
                spaceEnabled=True
                selectedRect(textIndex10, tenthReplyTextArray, tenthReplyTextList)
            if tenthReplyTextArray[1].collidepoint(mx,my):
                textIndex10=1
                keysActivate=True
                symbolsAllowed=True
                enterEnabled=True
                spaceEnabled=True
                selectedRect(textIndex10, tenthReplyTextArray, tenthReplyTextList)

            if replyConfirm.collidepoint(mx,my):
                confirmedReply=True
                clickedButton(replyConfirm, replyText)

            if replyPhotoSelect1.collidepoint(mx,my):
                replyFirstPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#seelect a photo and upload it to firebase. blit to screen
                if replyFirstPhotoFile!="":
                    replyPhoto1=image.load(replyFirstPhotoFile)
                    replyFirstPhoto = transform.scale(replyPhoto1, (100, 100))
                    startTenthScreen(parentID)
                    for item in range(len(tenthReplyTextList)):
                        if item!=1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, True)
                        elif item==1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, False)
            if replyPhotoSelect2.collidepoint(mx,my):
                replySecondPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#photo select. blit and add to firebase
                if replySecondPhotoFile!="":
                    replyPhoto2=image.load(replySecondPhotoFile)
                    replySecondPhoto = transform.scale(replyPhoto2, (100, 100))
                    startTenthScreen(parentID)
                    for item in range(len(tenthReplyTextList)):
                        if item!=1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, True)
                        elif item==1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, False)
            if replyPhotoSelect3.collidepoint(mx,my):
                replyThirdPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#photo select.blit and add to firebase
                if replyThirdPhotoFile!="":
                    replyPhoto3=image.load(replyThirdPhotoFile)
                    replyThirdPhoto = transform.scale(replyPhoto3, (100, 100))
                    startTenthScreen(parentID)
                    for item in range(len(tenthReplyTextList)):
                        if item!=1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, True)
                        elif item==1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, False)
            if replyPhotoSelect4.collidepoint(mx,my):
                replyFourthPhotoFile = tkFileDialog.askopenfilename(filetypes=[("Images", "*.png; *.bmp; *.jpg; *.jpeg")])#photo select. blit and add to firebase
                if replySecondPhotoFile!="":
                    replyPhoto4=image.load(replyFourthPhotoFile)
                    replyFourthPhoto = transform.scale(replyPhoto4, (100, 100))
                    startTenthScreen(parentID)
                    for item in range(len(tenthReplyTextList)):
                        if item!=1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, True)
                        elif item==1:
                            drawText(tenthReplyTextArray[item], tenthReplyTextList[item], False, False)
                    
           

    if screenNumber==11:
        if leftArrowSurfaceRect.collidepoint(mx,my):
            if leftClick==1:#go to 9th screen
                to9 = True
                
        if reportButt.collidepoint(mx,my):
            if leftClick==1:
                replyReport = True#start the report process
                clickedButton(reportButt, reportButtText)
        for rect in range(len(pArrayRects)):
            if pArrayRects[rect].collidepoint(mx-imageDisplaySurfRect.x, my-imageDisplaySurfRect.y) and leftClick==1:
                url = parentReply.photos[rect]#check index
                f = open(str(parentReply.replyID)+"_"+str(item)+".jpg",'wb')#download images from url to harddrive\
                f.write(requests.get(url).content)
                f.close()
                makeError("Success", "File Downloaded")
                
                
            
                

    typedLetters=""#clear typedLetters
    myClock.tick(fps)#30fps
    display.flip()
    #everything we "draw" is actually copied
                #to a place in RAM
            #display.flip copies that to the actual screen
            
quit() #closing the pygame window







    
