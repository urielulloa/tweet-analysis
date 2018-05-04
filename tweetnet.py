from preprocesstweet import make_twittercorpus, get_username
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pandas as pd

class Tweet:    
    def __init__(self, message, time, date):
        self.message = message
        self.time = time
        self.date = date
        
    def get_weekday(self):
        year = int(self.date[:4])
        month = int(self.date[5:7])
        day = int(self.date[8:10])
        return datetime.date(year, month, day).weekday()

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
 
        
    def make_relationship_csv(self): 
        #produce CSV output that gephi can import
        for recipient, weight in self.relations.items():
            for i in range(0, weight):
                yield self.name + "," + recipient
                
    def relation_graph(self):
        
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
    
    def getTweets(self):
        return self.tweets
        
    def get_username(self):
        return self.name
 
        
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
        print("Extracting tweets and user data...")
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
                    tweet_date = tweet[1][:11]
                    tweet_time = tweet[1][11:]
                    new_tweet = Tweet(tweet_message, tweet_time, tweet_date)
                    user_name = tweet[0]
                        
                    #print("Following tweet contains mention: " + tweet[2])
                    if user_name in self.users:
                        #print("Old user found: " + user_name)
                        self.users[user_name].tweets.append(new_tweet)
                    else:
                       # print("New user found: " + user_name)
                        new_user = TwitterUser(user_name)
                        new_user.tweets.append(new_tweet)
                        self.users[user_name] = new_user
        print("Data extracted! Computing relations...")                    
        #Compute relations between users
        for user in self.users:
            #assert isinstance(user,TwitterUser)
            self.users[user].computerelations()
        print("Relations computed!")

    
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
    
def ActivityPerHour(twittergraph):
    print("Printing activity graph.")
    times = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    count = 0
    user_times = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for twitteruser in twittergraph:
        for tweet in twittergraph[twitteruser.name].getTweets():
            hour = tweet.time[:2]
            if hour is '':
                hour = 00
            #print(tweet.time)
            user_times[int(hour)] += 1
        for hour in range(len(times)):
            times[int(hour)] += user_times[int(hour)]
        count += 1
       # print(str(hour)+ ": "+ str(times[int(hour)]))
    hours = np.arange(24)
    plt.bar(hours,times, 0.75)
    #plt.plot(hours,times)
    plt.ylabel('Average Number of Tweets per Hour')
    plt.xticks(np.arange(24))
    plt.xlabel('Hour')
    plt.show()
    return times

def popularHourPerDay(twittergraph):
    print("Calculating most popular hours per day...")
    chart = np.zeros((7, 25))
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    total_num_tweets = 0
    
    for twitteruser in twittergraph:
        for tweet in twittergraph[twitteruser.name].getTweets():
            total_num_tweets += 1
            if tweet.date is '':
                day = 0
            else:
                day = tweet.get_weekday()
            hour = tweet.time[:2]
            if hour is '':
                hour = 0
            else:
                hour = int(hour)
            chart[day][hour] += 1
            chart[day][24] += 1
            
        week = [0 for x in range(7)] 
        averages = [0 for x in range(7)]
        for day in range(7):
            max_num_tweets = 0
            most_popular_hour = 0
            for hour in range(24):
                if chart[day][hour] > max_num_tweets:
                    max_num_tweets = chart[day][hour]
                    most_popular_hour = hour
                average_num_tweets = chart[day][most_popular_hour] / chart[day][24]
                week[day] = most_popular_hour
                averages[day] = average_num_tweets  
    print("\nMOST POPULAR HOURS PER DAY")
    for day in range(7):
        print(days[day]+": \t"+ str(week[day]).zfill(2) + ":00 "+"\t Average number of tweets per user: " + str(averages[day]))
    return week


def make_csv(twittergraph, filepath, filename = "tweets.csv"):
    print("Making CSV file...")
    csv = open(filepath + filename, 'w') 
    csv.write("username\tdate\tday\ttime\tmessage\n")
    for twitteruser in twittergraph:
        username = twitteruser.get_username()
        for tweet in twittergraph[username].getTweets():
            time = tweet.time
            if tweet.date is '':
                date = str("NaT")
                weekday = str("NaN")
            else:
                date = tweet.date
                weekday = str(tweet.get_weekday())
            message = tweet.message
            csv.write(username+"\t"+date+"\t"+weekday+"\t"+time+"\t"+message+"\n")
    csv.close()
    print(filename+ " created!")
    
def make_relationship_csv(twittergraph, filepath, filename = "user_relationship.csv"):
    print("Making CSV file for relationships...")
    csv = open(filepath + filename, 'w') 
    csv.write("username\tuser_mentioned\tnum_times_mentioned\n")
    for twitteruser in twittergraph:
        username = twitteruser.name
        for recipient, weight in twitteruser.relations.items():
            weight = str(weight)
            csv.write(username+"\t"+recipient+"\t"+weight+"\n")
    csv.close()
    print(filename+ " created!")
    
def read_csv(filepath, filename ="tweets.csv"):
    return pd.read_csv(filepath+filename, sep = "\t")

twittergraph = TwitterGraph("twitterdata/") 
make_csv(twittergraph, "data/")
