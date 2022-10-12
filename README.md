
# Welcome to my webpage!

This holds all the code to stand up my personal webpage as well as some other goodies.


### Mike Schur Dialog Generator

I'm a big fan of many of the shows Michael Schur has produced: The Office, Parks and Rec, Booklyn 99, The Good Place, etc. While I was working on my Masters I created a Jupyter notebook that used Natural Language Processing to read in all of the scripts from The Office and spit out new lines of dialog for a few selected characters.

After building out expertise in AWS I decided to have some fun and build something similar using AWS resources. As of right now there are many more characters you can get dialog for:

**The Office**
- Michael Scott
- Dwight Schrute
- Jim Halpert
- Pam Beesly

**Parks and Recreation**
- Leslie Knope
- Ron Swanson
- Tom Haverford
- Ann Perkins
- April Ludgate
- Andy Dwyer
- Ben Wyatt
- Chris Traeger
- Jerry/Garry/Larry Gergich
- Donna Meagle


The code in this repo includes a public API enpoint that you can access with a simple `get` request to the endpoint `https://whph7zzofa.execute-api.us-east-1.amazonaws.com/prod/` and include a `character` parameter. For example:

`curl https://whph7zzofa.execute-api.us-east-1.amazonaws.com/prod?character=dwight`

This yields the following JSON output:
`{"dwight line": "A couple of bad reviews there, you might as well try to be halfway accurate."}`

Many of the lines may be gibberish and that's okay! The point of this project was not to create *actual* human readable dialog. It was merely to have some fun and learn some new tools and services.

There is a pretty low throttling limit to the API so it will easily choke if you throw too much at it. It's also likely your first few calls will throw an Internal Server Error, since the underlying Lambda function may be cold. It just takes a minute to warm back up.

Enjoy!