# PyTop

This is a solution similar to UNIX "top" command, developed as a project for the Operating Systems course @UFRJ (Fed. University of Rio de Janeiro / Brazil). For further information on the course instructions for this project please check https://www.gta.ufrj.br/~cruz/courses/eel770/ on "Trabalho" section.

# Inspiration

**We are friendly!**
We know that the "top" command might not be as easy to parse as some of us would want, so we built PyTop to be as friendly as it should be.

**Easy to understand and open code**
We're under MIT license, in other words, you can do *whatever you want* with our code! Beside that, it's been developed in Python, a very simple programming language.

**Multi-platform**
A-ha! We didn't forget you! Come on aboard Linux, Windows, OSX, FreeBSD, OpenBSD, NetBSD, Sun Solaris and AIX users, we've got you all covered.

# Features
As we're not trying to clone the "top" command (it would be meaningless), we shall now define the scope of this solution:
1. Show a list of all processes with the following information:
	* Unique ID
	* Owner
	* Priority
	* Memory usage
	* CPU usage
	* Description
2. Split processes according to their status:
	* Running
	* Sleeping
	* Stopped
	* Zombie
3. Inform CPU usage on user processes and system processes
4. Show general RAM and SWAP memory usage
5. Provide the possibility to change a process priority
6. Average CPU usage on the last 5, 10 and 15 minutes
7. Highlight the most CPU consumer process

# Strategy

As our main goal is to democratize the access to a similar solution to the "top" command, we intended to choose a very easy-to-learn, still powerful, programming language. This way, we've chosen Python for this solution. Since Python is *the one*, any healthy person would have imagined that there's already a library for something like that. Guest what? Of course there *are*! Plenty of those! And why should we reinvent the wheel?

After carefully comparing libraries, running example codes and some coffee, we decided that **psutil** is *a simple but tough-to-beat* (didn't get the reference? Please check https://github.com/PrincetonML/SIF) solution for our initial purpose, which is to develop the whole mechanism behind the process monitoring interface.

For later mechanisms, as changing processes priorities and more advanced statistics, we're still on the "some coffee" part.

# Troubles

**Every developer knows** that every developer makes stupid mistakes that can be solved with more stupid solutions but, unfortunately, **no developer knows** how to solve them, unless they have some coffee (and by "some" I mean "a lot of").

Our first troubles were all about the library: we had many "0%" usage on CPU *every time* we ran the code, issues with the unique IDs. **It was a mess**. After we *truly* learned how to use the library properly, started advancing on this project.

**Right now** we're working on improving the graphical part of our monitoring mechanisms and our statistics (it still seems not realistic).

# The team

The team related to this project is composed by two members:
 * Gabriel Gazola Milan
	 * Electronic and Computer Engineering Student @ UFRJ
	 * gabriel.gazola@poli.ufrj.br
 * Victor Rafael Breves Santos Ferreira
	 * Computer and Information Engineering Student @ UFRJ
	 * victor.breves@poli.ufrj.br

# Checkpoints

As required on the instructions of this project, there are two checkpoints:

 * May 16th, 2018:
	 * First presentation of the project.
* June 20th, 2018:
	* Final presentation of the project.

In the remote case where there is interest from the community in continuing this project, people should get in touch with any member of the team so we could, together, check this possibility.
