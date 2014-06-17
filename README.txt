EvoForest
=========
Evolutionary Forest framework with a small demo by team HedgeHo.

==========================================================
=====================What is it===========================
==========================================================

The evolutionary forest is a product of two somewhat refreshed
classic methods of data mining:
- Random forest of decision trees w/ search graphs: 
    original random forest:
    http://en.wikipedia.org/wiki/Random_forest
    that uses an otherwise clumsy search graphs to render
    complex numeric parameters (like y1^2 - 2*sin(y2) etc)
- Active learning genetic algorithm:
    original genetic algorithm:
    http://en.wikipedia.org/wiki/Genetic_algorithm
    The difference is that instead of fitness function you now
    have a fitness value of every chromosome(i.e. decision tree)
    that increases or decreases during the system runtime based
    on successes and failures of the chromosome.
    /*
    i actually had to reinvent ACTIVE GA because i found no good
    free papers about this method
    */

The IS maintains a pool of decision agents, each of them
has it's own subset of samples, attributes and a tree itself.

The decisions are made by polling the agents and picking the
most popular vote. 

/*
Practically because of unevenness in fitness
distribution, it only takes to poll some fraction of the most
fit trees to make a swift decision w/o a huge of accuracy as
it is in classic random forests
*/

Every agent has a fitness function associated to it, that
gets increased every time this agent was correct on a test
sample and decreased every failure.
In proportion to this function, the following resources are
distributed:
- amount of nodes a tree can have
- amount of samples per tree
- amount of attributes a tree can use
- agent's weight in the classification poll
- agent's probability to participate in recombination

=========================================================
====================How it works=========================
=========================================================
todo
=========================================================
===============Advantages and drawbacks==================
=========================================================
todo
=========================================================
========================Prospects========================
=========================================================
todo


=========================================================
==================Technical details======================
=========================================================

Current version is a working IronPython 2.7.3 framework, that
you can embed into any system, or use independently. However,
it was primarily designed for the scientific/demonstrational
causes and for sake of own curiosity.

Theoreticaly, it does not use any ironPython-specific mechanics
that are absent in cPython 2.7.5 (the basic one you can find on
python.org) or any other python you wish to use. The IDE used is
(surprisingly) Visual Studio '10 with Python Tools for VS plugin.

/*
Why? well, it was originally used in an IS, written in C#, that's
why IronPython. VS was used for cross-language developement ease.
In addition to this, i was surprised to find that VS debug capa-
bilities are great even in a plugged-in env.
*/

Practicaly, translating this code into, for example, cPython 3.*
would only take you to replace some 2.7.* syntax no more availa-
ble in 3.*, like console prints and those alike.

======================Feedback===========================
In case of any questions, notes, comments, ideas, or if you just
need someone to talk to, you can find me at sasha_panin@mail.ru.
