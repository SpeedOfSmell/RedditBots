import praw, time
from wordnik import *

def formatPost(defins, comment):
    if defins == None:
        post = "---\n> [**%s**](http://www.wordnik.com/words/%s)\n\n> *No definitions found.*\n\n ^Scrabble ^score: ^N/A\n\n---\n\n" % (searchword, searchword) + \
        "[^Report ^a ^problem](http://www.np.reddit.com/message/compose?to=djmanex&subject=DictBot Problem&message=Problem: %s)" % comment
    else:
        pro = wordApi.getTextPronunciations(searchword, limit = 1)
        sScore = wordApi.getScrabbleScore(searchword)
        post = "---\n> [**%s**](http://www.wordnik.com/words/%s) %s" % (searchword, searchword, pro[0].raw)
        for defin in defins:
            post = '\n\n> * '.join([post, defin.text])
        post = '\n'.join([post, "\n\n ^Scrabble ^score: ^%s\n\n---\n [^Report ^a ^problem](http://www.np.reddit.com/message/compose?to=djmanex&subject=DictBot Problem&message=Problem: %s)"
            % (sScore.value, comment)])
    return post

r = praw.Reddit("Dictionary bot by /u/DjManEX")
r.login(username = "Username", password = "Password")
print "Logged in to Reddit."

apiUrl = 'http://api.wordnik.com/v4'
apiKey = 'Key'
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)
print "Logged in to Wordnik API.\n"

already_done = []

while True:
    try:
        commentList = r.get_comments('all', limit = 1000)
    except praw.requests.HTTPError:
        print "No connection to Reddit.\n"
        time.sleep(20)
        continue
    except Exception:
        error = traceback.format_exc()
        print "Unknown error occured while attempting to retrieve comments.\n" + error
        continue
    
    for comment in commentList:
        if (comment.body.lower()[0:15] == "dictbot define ") and (comment.id not in already_done):
            searchword = comment.body.lower()[15:]
            print "\"%s\" requested in /r/%s by /u/%s" % (searchword, comment.subreddit.display_name, comment.author.name)
            definitions = wordApi.getDefinitions(searchword)
            formatted = formatPost(definitions, comment.id)
            try:
                comment.reply(formatted)
            except praw.errors.RateLimitExceeded as error:
                print "Bot posting too much. Sleeping for %s seconds." % error.sleep_time
                time.sleep(error.sleep_time)
                print "Done sleeping."
            except praw.requests.HTTPError:
                print "Bot attempted to post in a banned subreddit.\n"
            except Exception:
                error = traceback.format_exc()
                print "Unknown error occured.\n" + error
            else:
                print "Replied."
            already_done.append(comment.id)
            
    
