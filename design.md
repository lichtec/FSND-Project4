#Design Document
##What additional properties did you add to your models and why?
My game model has some additions to handle the differences between the guess a number game and hangman. 
I added a current view so that a player could track what they still had to guess. I also added a hint 
option to facilitate challenges. There was also the addition of a cancel Boolean field to handle the 
canceling of a game. Since the hangman game also needed a clear objective (the phrase or word to be 
guessed) I added an objective field. I also included a guesses field to keep track of a game's history. 
Finally the addition of a challenger and challenged field allows for the challenge aspect of the game. 
These fields are also important for the tasks processes. There are two tasks facilitated by these, the 
end game notification and the challenge notification. The challenged field also allows for the cron job 
to reminder users about their active games.

The user model was left mostly unchanged except for the total points. This was added to facilitate ranking.
I never found a clean way to sum each score entity for a user which is the way I would have preferred to 
handle it. I do not see too many issues with this addition since it’s such a small concession to simplify 
the problem. The final change was the setting the email field to required. Doing this keeps the cron and 
task job working properly.

The score model was also mostly unmodified except for the points field. The points field was added to track 
scoring but in the end was not used. It’s left there as an option to review in the future. The score model 
was also being used not only for the winner but also the loser. Keeping track of both allows for the option 
to expand the ranking to include a win-lose stat. 

##What were some of the trade-offs or struggles you faced when implementing the new game logic?
My biggest trade-off is the points duplication. The points data is available in different areas so there's a 
clear duplication of data. To get around issues I ran into this was necessary. The biggest struggle I faced 
was how to handle the each step without impacting the other work I had done. I regularly had to refactor code 
to deal with issues I introduced with new features. With this in mind I would like to implement a better process
for tracking features. If I'm not careful this will turn into a pitch for Agile backlogs. 

If I had to rank another issue it was probably the errors I ran into. In some situations errors produced by 
appengine were not clear and did not provide enough information to check the docs/google. That would normally 
force me to comment out code till I found the issue or rewrite entire sections trying to avoid whatever I was 
running into. 

The final thing that caused issues was testing. I would have liked some time spent on writing testing functions
to automate this process. I know this is very useful in the real world and would have sped that process up.

