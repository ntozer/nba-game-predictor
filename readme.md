## NBA Game Predictor
As a Toronto Raptors fan I really wanted to somehow give myself realistic expectations for the 2018 playoffs after the dissapointment
of the series against the Cavs last year. This desire to give me some sort of reasonable expectations combined with my intersest in data 
and machine learning spawned the idea of making an NBA Game Predictor.

## Project Screenshots
ELO values for home and visiting teams vs. the outcome of the game in the 2016-2017 NBA season
![elo_viz](https://i.imgur.com/Z4XcGy6.png)

Change of logloss vs. the number of data points(predictions made using a 2 layer 46 node neural network on the test set)
![logloss_test_viz](https://i.imgur.com/ZIaiBvW.png)



## Project Status

#### Completed:
 - write scraper to collect raw datasets from www.basketball-reference.com
 - write script to clean raw data and get it ready to for feature addition
 - write script to add features to cleaned data
 - implement a multi layer neural network and start predicting games
 - write a script to calculate evaluation metrics for ML algos
 - clean up/modularize data_preparer.py
 - implement Nate Silvers ELO algorithm for NBA teams
 
#### In Progress:
 - create seperate script for all data viz methods

#### To Do:
 - write and apply mean normalization func to all features
 - implement multivariate logistic regression to predict games
 - implement decision tree to predict games
 - create GUI to easily see predictions for a specific day

## Installation and Setup Instructions
Still have to update this :)

## Reflections
I'll update this when I'm done :)

## Technologies Used
![tech_used](https://i.imgur.com/eGUeX2d.png)

