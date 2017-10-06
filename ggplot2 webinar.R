setwd("C:/Users/MillerAr")
library(ggplot2)
library(readr)
train <- read_csv("~/train.csv")
View(train)




train$Pclass <- as.factor(train$Pclass)
train$Survived <- as.factor(train$Survived)
train$Sex <- as.factor(train$Sex)
train$Embarked <- as.factor(train$Embarked)

prop.table(table(train$survived))

ggplot(train, aes(x = Survived)) + 
  theme_bw() +
  geom_bar() +
  labs(y= "Passenger Count",
    title = "Titanic Survival Rates by Sex")

ggplot(train, aes(x = Sex, fill = Survived)) + 
  theme_bw() +
  geom_bar() +
  labs(y= "Passenger Count",
       title = "Titanic Survival Rates by Sex")

ggplot(train, aes(x = Pclass, fill = Survived)) + 
  theme_bw() +
  geom_bar() +
  labs(y= "Passenger Count",
       title = "Titanic Survival Rates by PClass")

ggplot(train, aes(x = Pclass, fill = Survived)) + 
  theme_bw() +
  facet_wrap(~Pclass)
  geom_bar() +
  labs(y= "Passenger Count",
       title = "Titanic Survival Rates by PClass")
  
  ggplot(train, aes(x = Age)) + 
    theme_bw() +
    geom_histogram(binwidth = 5) +
    labs(y = "Passenger Count",
         x = "Age (binwidth = 5)",
         title = "Titanic Age Distribution")
  
  ggplot(train, aes(x = Age, fill = Survived)) + 
    theme_bw() +
    geom_histogram(binwidth = 5) +
    labs(y = "Passenger Count",
         x = "Age (binwidth = 5)",
         title = "Titanic Age Distribution")
  
  ggplot(train, aes(x = Survived, y = Age)) +
    theme_bw() +
    geom_boxplot() +
    labs(y = "Age",
         x = "Survived",
         title = "Titanic Survival Rates by Age")
  
  ggplot(train, aes(x = Age, fill = Survived)) +
    theme_bw() +
    facet_wrap(Sex ~ Pclass) +
    geom_density(alpha = 0.5) +
    labs(y = "Survived",
         x = "Age",
         title = "Titanic Survival Rates by Age, PClass and Sex")
  
  ggplot(train, aes(x = Age, fill = Survived)) +
    theme_bw() +
    facet_wrap(Sex ~ Pclass) +
    geom_histogram(binwidth = 5) +
    labs(y = "Survived",
         x = "Age",
         title = "Titanic Survival Rates by Age, PClass and Sex")
  
