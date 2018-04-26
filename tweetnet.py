from preprocesstweet import make_twittercorpus, get_username
import numpy as np
import matplotlib.pyplot as plt


class Tweet:    
    def __init__(self, message, time):
        self.message = message
        self.time = time
        

class TwitterUser:
    def __init__(self, name):
        self.name = name
        self.tweets = [] #This will be a list of all tweets 
        self.relations = {} #This will be a dictionary in which the keys are TwitterUser objects and the values are the weight of the relation (an integer) 
    
    def append(self, tweet):
        assert isinstance(tweet, Tweet) #this is a test, if tweet is not an instance
                                        #of Tweet, it will raise an Exception.
        self.tweets.append(tweet)
        
    def __iter__(self):
        #This function, a generator, should iterate over all tweets
       for tweet in self.tweets:
           yield tweet
        
    
    def __hash__(self):    
        #For an object to be usable as a dictionary key, it must have a hash method. Call the hash() function over something that uniquely defined this object
        #and thus can act as a key in a dictionary. In our case, the user name is good, as no two users will have the same name:          
        return hash(self.name)
    
    
    def addrelation(self, user):
        if user and user != self.name: #user must not be empty, and must not be the user itself
            if user in self.relations:
                #the user is already in our relations, strengthen the bond:
                self.relations[user] += 1
            elif user not in self.relations:
                self.relations[user ] = 1
        
    def computerelations(self):
        for tweet in self.tweets:
            #tokenise the actual tweet content (use the tokeniser in preprocess!):
            words = tweet.message.split()
            #Search for @username tokens, extract the username, and call self.addrelation()
            for word in words:
                if word[0] is '@':
                    self.addrelation(get_username(word[1:]))
        
    def printrelations(self):
        #print the relations, include both users and the weight
        for relation in self.relations:
            print(relation)
 
        
    def gephioutput(self): 
        #produce CSV output that gephi can import
        for recipient, weight in self.relations.items():
            for i in range(0, weight):
                yield self.name + "," + recipient
                
    def RelationGraph(self):
        
        if len(self.relations) < 10:
            return
        
        num_interactions = ()
        names = ()
        
        fig, ax = plt.subplots()
        ax.set_xlabel('User Mentioned')
        ax.set_ylabel('Number of mentions')
        ax.set_title('Users most mentioned by ' + self.name)
        index = np.arange(10)
        
       # print(max(self.relations.items(), key=operator.itemgetter(1)))
        
        for relation in sorted(self.relations, key=self.relations.get)[-10:]:
            num_interactions += (self.relations[relation], )
            names += (relation, )
        ax.bar(index, num_interactions, 0.8, 0,
                alpha=0.4, color='b', tick_label= names)
        plt.xticks(rotation=90)
        plt.show()
        
 
        
class TwitterGraph:
    def __init__(self, corpusdirectory):        
        self.users = {} #initialisation of dictionary that will store all twitter users. They keys are the names, the values are TwitterUser objects.
                        #the keys are the usernames (strings), and the values are
                        # TweetUser instances
                
        #Load the twitter corpus 
        #tip: use preprocess.find_corpusfiles and preprocess.read_corpus_file,
        #do not use preproces.readcorpus as that will include sentence segmentation
        #which we do not want
        print("Extracting corpus from " + corpusdirectory +" ...")
        corpus = make_twittercorpus(corpusdirectory)
        print("Corpus extracted!")
        print("Creating twitter graph...")
        #Each txt file contains the tweets of one user.
        #all files contain three columns, separated by a TAB (\t). The first column
        #is the user, the second the time, and the third is the tweetmessage itself.
        #Create Tweet instances for every line that contains a @ (ignore other lines 
        #to conserve memory). Add those tweet instances to the right TweetUser. Create
        #TweetUser instances as new users are encountered.
        
        #self.users[user], which user being the username (string), should be an instance of the
        #of TweetUser
        
        for tweet in corpus:
            for word in tweet[2]:
                if word[0] is '@':
                    tweet_message = tweet[2]
                    tweet_time = tweet[1]
                    new_tweet = Tweet(tweet_message, tweet_time)
                    user_name = tweet[0]
                        
                    #print("Following tweet contains mention: " + tweet[2])
                    if user_name in self.users:
                        #print("Old user found: " + user_name)
                        self.users[user_name].tweets.append(new_tweet)
                    else:
                        print("New user found: " + user_name)
                        new_user = TwitterUser(user_name)
                        new_user.tweets.append(new_tweet)
                        self.users[user_name] = new_user
        print("Valid tweets extracted! Computing relations...")                    
        #Compute relations between users
        for user in self.users:
            #assert isinstance(user,TwitterUser)
            self.users[user].computerelations()
        print("Relations computed! Printing relation charts.")

    
    def __contains__(self, user):
        #Does this user exist?
        return user in self.users
    
    def __iter__(self):
        #Iterate over all users
        for user in self.users.values():
            yield user

    def __getitem__(self, user):    
        #Retrieve the specified user
        return self.users[user]
            

#this is the actual main body of the program. The program should be passed one parameter
#on the command line: the directory that contains the *.txt files from twitterdata.zip.

#We instantiate the graph, which will load and compute all relations
twittergraph = TwitterGraph("data/twitterdata/")
#We output all relations:
for twitteruser in twittergraph:
    twittergraph[twitteruser.name].RelationGraph()
