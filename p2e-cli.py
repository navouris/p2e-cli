# NMA June 2020 v 0.3 windows enabled
import os
import json
import checkExams
import sys

# https://stackoverflow.com/questions/60937345/how-to-set-up-relative-paths-to-make-a-portable-exe-build-in-pyinstaller-with-p
def resource_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path

# print("the home dir is ...", resource_path("."))

class MyApp:
    def __init__(self):
        self.load(setCourse=False)
        self.buildMenu()
    
    def load(self, setCourse):
        self.activeCourse = Course.loadCourses(setCourse)
        if self.activeCourse:
            print("loaded...", self.activeCourse.dir, self.activeCourse.progressFile)
        loadingResult =""
        if self.activeCourse and not checkExams.Enrolled.courseDir == self.activeCourse.dir:
            print("loading progress data .....")
            loadingResult = checkExams.Enrolled.load(self.activeCourse.dir, self.activeCourse.progressFile) # load course data
            # print("result=", loadingResult, "dir, progressFile ==", self.activeCourse.dir, self.activeCourse.progressFile)
        else: loadingResult = False
        if self.activeCourse: print(self.activeCourse.name)
        if loadingResult != "ok":
            if not loadingResult: loadingResult = ""
            print("Προσοχή δεν δημιουργήθηκε νέο μάθημα, πρέπει να ξαναπροσπαθήσετε ..."+loadingResult)
    
    def error(self, text):
        print("ERROR: "+  text)

    def buildMenu(self): # build the main menu card
        while True:
            if self.activeCourse: course = self.activeCourse.name
            else: course = "......"
            print("\n\nΜάθημα: {}\nΕΠΙΛΟΓΕΣ:\n1. Φοιτητές χωρίς δικαίωμα συμμετοχής στην εξέταση [1h με το ιστορικό τους]".format(course) +
            "\n2. Φοιτητές με δικαίωμα συμμετοχής [2h με το ιστορικό τους]\n3. Αλλαγή μαθήματος\n4.Έξοδος")
            reply = input("επιλογή:")
            if reply == "1":
                print(checkExams.Enrolled.showStudents(kind = "not eligible", exams=False))
            elif reply == "1h":
                print(checkExams.Enrolled.showStudents(kind = "not eligible", exams=True))
            elif reply == "2h":
                print(checkExams.Enrolled.showStudents(kind = "eligible", exams=True))
            elif reply == "2":
                print(checkExams.Enrolled.showStudents(kind = "eligible", exams=False))
            elif reply == "3": 
                self.load(setCourse=True)
            elif reply == "4":
                break
        return False

class Course:
    theCourses = []
    activeCourse = None
    @staticmethod
    def loadCourses(setCourse=False):
        loaded = False
        if os.path.isfile('mycourses.json'):
            try:
                with open('mycourses.json') as jsonFile:
                    theCourses = json.load(jsonFile)
                    for course in theCourses:
                        Course(**course)
                    loaded = True
            except: 
                loaded = False 
        if not loaded or setCourse:
            name, dir, filename = "","",""
            while (not name or not dir or not filename):
                if not name:
                    name = input( \
'''ΟΡΙΣΜΟΣ Ή ΑΛΛΑΓΗ ΤΟΥ ΜΑΘΗΜΑΤΟΣ ΕΞΕΤΑΣΗΣ ...
Δώστε το Όνομα του Μαθήματος που θα εξεταστεί (πχ. Μαθηματικά),
στη συνέχεια θα σάς ζητηθεί να ορίσετε τον φάκελο που έχετε αποθηκεύσει  
τα αρχεία βαθμολογιών, και τέλος στον φάκελο αυτό να δείξετε ποιο είναι
το αρχείο που περιέχει τις δηλώσεις της τρέχουσας εξέτασης.
Αν κάποιο από τα στοιχεία αυτά δεν οριστεί δεν μπορείτε να ορίσετε το
μάθημα της εξέτασης (x για έξοδο)...
\nΑρχίζουμε με το όνομα του μαθήματος:''')
                    if name == "x": break
                if not dir:
                    reply = input('''\nΟ φάκελος που έχετε αποθηκεύσει τα αρχεία βαθμολογιών (progress) του μαθήματος "{}" (enter αν είναι ο τρέχων φάκελος)... '''.format(name) )
                    if reply == "x":break
                    if not reply: reply = os.getcwd()
                    if os.path.isdir(reply): dir = reply

                if not filename:
                    reply = input('''\nΤο αρχείο με το βαθμολόγιο της τρέχουσας εξεταστικής του μαθήματος "{}" :'''.format(name) )
                    if reply == "x":break
                    if os.path.isfile(reply): filename = reply
                    elif dir and os.path.isfile(os.path.join(dir, reply )): filename = os.path.join(dir, reply )
                print('so far ...', name, dir, filename)
            else: 
                Course(name, dir, filename, True)
                Course.saveCourses()
                return Course.activeCourse
        return Course.activeCourse

    @staticmethod
    def saveCourses():
        theCourses = []
        for c in Course.theCourses:
            if c == Course.activeCourse: activeCourse = 1
            else: activeCourse = 0
            theCourses.append({"name": c.name, "dir": c.dir, "progressFile": c.progressFile, "active":activeCourse})
        with open('mycourses.json', "w") as outJson:
            json.dump(theCourses, outJson, ensure_ascii=False)
    
    def __init__(self, name, dir, progressFile, active):
        self.name = name
        self.dir = dir
        self.progressFile = progressFile
        self.active = active
        Course.theCourses.append(self)
        if self.active: Course.activeCourse = self

def main():
    MyApp()

if __name__ == "__main__":
    main()

