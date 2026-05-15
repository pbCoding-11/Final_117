"""
Description: A Program that creates a widget where a user can search a local database for a book via its title,
            and see the 10 most common words inside the text. The URL is taken from Project Gutenberg
            and the database is ran using SQLite3
Author: Patrick Bowlus
Date: 5/4/2026
"""

import re, sqlite3, os, ssl
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from tkinter import *
from urllib.request import urlopen
from collections import Counter

#Prevents the counting of common words irrelevant to program
STOP_WORDS = {
    "x", "y", "your", "yours", "yourself", "yourselves", "you", "yond", "yonder",
    "yon", "ye", "yet", "z", "zillion", "j", "u", "umpteen", "usually", "us",
    "username", "uponed", "upons", "uponing", "upon", "ups", "upping", "upped",
    "up", "unto", "until", "unless", "unlike", "unliker", "unlikest", "under",
    "underneath", "use", "used", "usedest", "r", "rath", "rather", "rathest",
    "rathe", "re", "relate", "related", "relatively", "regarding", "really",
    "res", "respecting", "respectively", "q", "quite", "que", "qua", "n",
    "neither", "neaths", "neath", "nethe", "nethermost", "necessary",
    "necessariest", "necessarier", "never", "nevertheless", "nigh", "nighest",
    "nigher", "nine", "noone", "nobody", "nobodies", "nowhere", "nowheres",
    "no", "noes", "nor", "nos", "no-one", "none", "not", "notwithstanding",
    "nothings", "nothing", "nathless", "natheless", "t", "ten", "tills", "till",
    "tilled", "tilling", "to", "towards", "toward", "towardest", "towarder",
    "together", "too", "thy", "thyself", "thus", "than", "that", "those",
    "thou", "though", "thous", "thouses", "thoroughest", "thorougher",
    "thorough", "thoroughly", "thru", "thruer", "thruest", "thro", "through",
    "throughout", "throughest", "througher", "thine", "this", "thises", "they",
    "thee", "the", "then", "thence", "thenest", "thener", "them", "themselves",
    "these", "therer", "there", "thereby", "therest", "thereafter", "therein",
    "thereupon", "therefore", "their", "theirs", "thing", "things", "three",
    "two", "o", "oh", "owt", "owning", "owned", "own", "owns", "others",
    "other", "otherwise", "otherwisest", "otherwiser", "of", "often", "oftener",
    "oftenest", "off", "offs", "offest", "one", "ought", "oughts", "our",
    "ours", "ourselves", "ourself", "out", "outest", "outed", "outwith", "outs",
    "outside", "over", "overallest", "overaller", "overalls", "overall",
    "overs", "or", "orer", "orest", "on", "oneself", "onest", "ons", "onto",
    "a", "atween", "at", "athwart", "atop", "afore", "afterward", "afterwards",
    "after", "afterest", "afterer", "ain", "an", "any", "anything", "anybody",
    "anyone", "anyhow", "anywhere", "anent", "anear", "and", "andor",
    "another", "around", "ares", "are", "aest", "aer", "against", "again",
    "accordingly", "abaft", "abafter", "abaftest", "abovest", "above",
    "abover", "abouter", "aboutest", "about", "aid", "amidst", "amid",
    "among", "amongst", "apartest", "aparter", "apart", "appeared", "appears",
    "appear", "appearing", "appropriating", "appropriate", "appropriatest",
    "appropriates", "appropriater", "appropriated", "already", "always",
    "also", "along", "alongside", "although", "almost", "all", "allest",
    "aller", "allyou", "alls", "albeit", "awfully", "as", "aside", "asides",
    "aslant", "ases", "astrider", "astride", "astridest", "astraddlest",
    "astraddler", "astraddle", "availablest", "availabler", "available",
    "aughts", "aught", "vs", "v", "variousest", "variouser", "various", "via",
    "vis-a-vis", "vis-a-viser", "vis-a-visest", "viz", "very", "veriest",
    "verier", "versus", "k", "g", "go", "gone", "good", "got", "gotta",
    "gotten", "get", "gets", "getting", "b", "by", "byandby", "by-and-by",
    "bist", "both", "but", "buts", "be", "beyond", "because", "became",
    "becomes", "become", "becoming", "becomings", "becominger", "becomingest",
    "behind", "behinds", "before", "beforehand", "beforehandest",
    "beforehander", "bettered", "betters", "better", "bettering", "betwixt",
    "between", "beneath", "been", "below", "besides", "beside", "m", "my",
    "myself", "mucher", "muchest", "much", "must", "musts", "musths", "musth",
    "main", "make", "mayest", "many", "mauger", "maugre", "me", "meanwhiles",
    "meanwhile", "mostly", "most", "moreover", "more", "might", "mights",
    "midst", "midsts", "h", "huh", "humph", "he", "hers", "herself", "her",
    "hereby", "herein", "hereafters", "hereafter", "hereupon", "hence",
    "hadst", "had", "having", "haves", "have", "has", "hast", "hardly", "hae",
    "hath", "him", "himself", "hither", "hitherest", "hitherer", "his",
    "how-do-you-do", "however", "how", "howbeit", "howdoyoudo", "hoos", "hoo",
    "w", "woulded", "woulding", "would", "woulds", "was", "wast", "we",
    "wert", "were", "with", "withal", "without", "within", "why", "what",
    "whatever", "whateverer", "whateverest", "whatsoeverer", "whatsoeverest",
    "whatsoever", "whence", "whencesoever", "whenever", "whensoever", "when",
    "whenas", "whether", "wheen", "whereto", "whereupon", "wherever",
    "whereon", "whereof", "where", "whereby", "wherewithal", "wherewith",
    "whereinto", "wherein", "whereafter", "whereas", "wheresoever",
    "wherefrom", "which", "whichever", "whichsoever", "whilst", "while",
    "whiles", "whithersoever", "whither", "whoever", "whosoever", "whoso",
    "whose", "whomever", "s", "syne", "syn", "shalling", "shall", "shalled",
    "shalls", "shoulding", "should", "shoulded", "shoulds", "she", "sayyid",
    "sayid", "said", "saider", "saidest", "same", "samest", "sames", "samer",
    "saved", "sans", "sanses", "sanserifs", "sanserif", "so", "soer", "soest",
    "sobeit", "someone", "somebody", "somehow", "some", "somewhere",
    "somewhat", "something", "sometimest", "sometimes", "sometimer",
    "sometime", "several", "severaler", "severalest", "serious", "seriousest",
    "seriouser", "senza", "send", "sent", "seem", "seems", "seemed",
    "seemingest", "seeminger", "seemings", "seven", "summat", "sups", "sup",
    "supping", "supped", "such", "since", "sine", "sines", "sith", "six",
    "stop", "stopped", "p", "plaintiff", "plenty", "plenties", "please",
    "pleased", "pleases", "per", "perhaps", "particulars", "particularly",
    "particular", "particularest", "particularer", "pro", "providing",
    "provides", "provided", "provide", "probably", "l", "layabout",
    "layabouts", "latter", "latterest", "latterer", "latterly", "latters",
    "lots", "lotting", "lotted", "lot", "lest", "less", "ie", "ifs", "if",
    "i", "info", "information", "itself", "its", "it", "is", "idem",
    "idemer", "idemest", "immediate", "immediately", "immediatest",
    "immediater", "in", "inwards", "inwardest", "inwarder", "inward",
    "inasmuch", "into", "instead", "insofar", "indicates", "indicated",
    "indicate", "indicating", "indeed", "inc", "f", "fact", "facts", "fs",
    "figupon", "figupons", "figuponing", "figuponed", "few", "fewer",
    "fewest", "frae", "from", "failing", "failings", "five", "furthers",
    "furtherer", "furthered", "furtherest", "further", "furthering",
    "furthermore", "fourscore", "followthrough", "for", "forwhy", "fornenst",
    "formerly", "former", "formerer", "formerest", "formers", "forbye",
    "forby", "fore", "forever", "forer", "fores", "four", "d", "ddays",
    "dday", "do", "doing", "doings", "doe", "does", "doth", "downwarder",
    "downwardest", "downward", "downwards", "downs", "done", "doner",
    "dones", "donest", "dos", "dost", "did", "differentest", "differenter",
    "different", "describing", "describe", "describes", "described",
    "despiting", "despites", "despited", "despite", "during", "c", "cum",
    "circa", "chez", "cer", "certain", "certainest", "certainer", "cest",
    "canst", "cannot", "cant", "cants", "canting", "cantest", "canted", "co",
    "could", "couldst", "comeon", "comeons", "come-ons", "come-on",
    "concerning", "concerninger", "concerningest", "consequently",
    "considering", "e", "eg", "eight", "either", "even", "evens", "evenser",
    "evensest", "evened", "evenest", "ever", "everyone", "everything",
    "everybody", "everywhere", "every", "ere", "each", "et", "etc",
    "elsewhere", "else", "ex", "excepted", "excepts", "except", "excepting",
    "exes", "enough", "gutenberg", "pg",
}



#parses html page via BeautifulSoup
class htmlparser(HTMLParser):
    """HTMLParser parses through text pulled via URL using BeautifulSoup"""
    def __init__(self, db):
        HTMLParser.__init__(self)
        self.title = ""
        self.db = db

    def handle_data(self, url, fallback_title="unknown title"): #fallback title to still allow addition to db
        #cleans content of HTML page and parses via BeautifulSoup
        response = urlopen(url)
        content = response.read()
        soup = BeautifulSoup(content, "html.parser")
        self.title = soup.title.string

        #checks if both are true, then ensures proper titling
        if soup.title and soup.title.string:
             self.title = soup.title.string.strip()
        else:
             self.title = fallback_title

        self.title = self.title.split("|")[0].strip()
        print(soup.title)

        #main section which lowers and only grabs words which are not in STOP_WORDS
        main_content = soup.find("div", class_="body") or soup
        jarble = main_content.get_text()
        coherence = re.findall(r"\b\w+", jarble.lower())
        filtered = [word for word in coherence if word not in STOP_WORDS]
        numbers = Counter(filtered)

        #retrieves 10 most common words in the numbers list, then joins it as one big string
        TheTen = numbers.most_common(10)
        answer = "\n".join(f"{k}: {v}" for k, v in TheTen)
        self.db.add(answer, self.title)
        return self.title



#activates and runs the main database used for program
class CompDB():
    """Creates and maintains database while also holding actions regarding pulling information from the database"""
    def __init__(self):
        #initializes db incase it doesn't exist (it does)
        dir_base = os.path.dirname(os.path.abspath(__file__))
        path_db = os.path.join(dir_base, "feelinggood.db")

        self.con = sqlite3.connect(path_db)
        self.cur = self.con.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS feelinggood (
            title TEXT PRIMARY KEY,
            words TEXT
            )
        """)

        self.con.commit()
    
    #function to add books to the library using its title and the string "answer" retrieved from HTMLParser
    def add(self, answer, title):
        self.cur.execute("""
            INSERT OR REPLACE INTO feelinggood (title, words)
            VALUES (?, ?)
        """, (title, answer))

        self.con.commit()

    #checks if a book is already inside the database
    def check(self, title):
        similarity = f"%{title}%"
        self.cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM feelinggood
                WHERE title LIKE ?
                LIMIT 1
            )
        """, (similarity,))

        facts = self.cur.fetchone()[0] == 1

        return facts
    
    #grabs the book title and most common 10 words
    def grab(self, title):
        similarity = f"%{title}%"
        self.cur.execute("""
        SELECT words FROM feelinggood WHERE title LIKE ?
        """, (similarity,))

        success = self.cur.fetchone()

        if success:
            return success[0]
        
        return None

    
#User Interface seen when running the program
class UserInterface():
    """The GUI of the Program, creating a widget with 2 buttons, 2 texts field, and an output.
        additionally checks Gutenberg website directly if the title is not in database and 
        there is no URL given"""
    def __init__(self, window):
        self.window = window

        self.db = CompDB()
        self.parser = htmlparser(self.db)

        self.create_widget()
    
    #creates the widget and specific features that run when an action is taken
    def create_widget(self):
        self.title_label = Label(self.window, text="Enter Title: ")
        self.title_label.grid(row=1, column=0, sticky='w')

        self.title_entry = Entry(self.window)
        self.title_entry.grid(row=1, column=1)

        self.title_button = Button(self.window, text="Search", command=self.title_click)
        self.title_button.grid(row=2, column=0, columnspan=2)

        self.url_label = Label(self.window, text="Enter URL: ")
        self.url_label.grid(row=3, column=0, sticky='w')

        self.url_entry = Entry(self.window)
        self.url_entry.grid(row=3, column=1)

        self.url_button = Button(self.window, text="Search", command=self.url_click)
        self.url_button.grid(row=4, column=0, columnspan=2)

        self.output = Text(self.window, width=40, height=15)
        self.output.grid(row=5, column=0, columnspan=2)

    #action for when program receives a url of an .HTML
    def url_click(self):
            self.output.delete(1.0, END) #alway clears output before running

            #opens URL and checks title in database to see if it already exists
            query = self.url_entry.get()
            response = urlopen(query)
            content = response.read()
            soup = BeautifulSoup(content, "html.parser")
            questionTitle = soup.title.string
            self.db.check(questionTitle)
            if self.db.check(questionTitle): #if in the database, pull it and put in output for user
                glory = self.db.grab(questionTitle)
                self.output.insert(END, questionTitle + "\n" + glory)
            else:
                #runs query as a new URL, and feeds into HTMLParser before grabbing new dataset
                happiness = self.parser.handle_data(query, fallback_title=query)
                pleasework = self.db.grab(happiness)
                self.output.insert(END, questionTitle + "\n" + pleasework)

    #action for when program receives a title of a book
    def title_click(self):
            self.output.delete(1.0, END)

            #receives name and checks db for title LIKE user input
            name = self.title_entry.get()
            self.db.check(name)
            if self.db.check(name): #if there, pulls and puts into output
                glory = self.db.grab(name)
                self.output.insert(END, glory)
            else:
                #searches using Project Gutenberg itself
                self.tryguten(name)
        
    #Searches Project Gutenberg using title, before sending to HTMLParser
    def tryguten(self, name):
            try:
                searchReady = name.replace(" ", "+") #makes user input URL friendly

                searching = (f"https://www.gutenberg.org/ebooks/search/?query={searchReady}")

                #checks if URL has a booklink for designated title
                response = urlopen(searching)
                content = response.read()
                soup = BeautifulSoup(content, "html.parser")

                theLink = soup.find("li", class_="booklink")

                if not theLink: #if no link, bummer
                    self.output.insert(END, "Book not found :(")
                    return
                
                #if a link is found, search ebooks
                ref = theLink.find("a")["href"]
                yay = re.search(r'/ebooks/(\d+)', ref)

                if not yay:
                    self.output.insert(END, "Book not found :(")
                
                id = yay.group(1)

                #creates another URL to try and open for parsing
                textURL = (f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt")

                #parses and joy
                secondtry = self.parser.handle_data(textURL, fallback_title=name)

                glory = self.db.grab(secondtry)

                self.output.insert(END, glory)
                
            except:
                #if nothing can be done, bummer
                self.output.insert(END, "Book not found :(")

#runs the instance
if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context

    window = Tk()

    window.title("Common Words")

    app = UserInterface(window)

    window.mainloop()
