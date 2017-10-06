setwd("C:/Users/MillerAr/Documents/R Scripts")
library(reshape2)
library(dplyr)
library(extrafont)
library(ggplot2)
library(animation)
library(grid)

measles <- read.csv("MEASLES_Incidence_1928-2003_20170705142131.csv",skip=2)
View(measles)
measles <- melt(measles, id.var=c("YEAR", "WEEK"))
colnames(measles) <- c("year", "week", "state", "cases")
measles$cases <- ifelse(measles$cases=="\u002D",NA,measles$cases)
measles$cases <- as.numeric(measles$cases)

mdf <- measles %>% group_by(state, year) %>% 
  summarise(incidence=if(all(is.na(cases))) NA else
    sum(cases, na.rm=T))
mdf$state <- factor(mdf$state, levels=rev(levels(mdf$state)))

cols<- c("#e7f0fa", #lighter than light blue
         "#c9e2f6", #light blue
         "#95cbee", #blue
         "#0099dc", #darker blue
         "#4ab04a", #green
         "#ffd73e", #yellow
         "#eec73a", #mustard
         "#e29421", #dark khaki (?)
         "#f05336", #orange red
         "#ce472e") #red
extrafont::loadfonts()

gg <- ggplot(mdf, aes(y=state, x=year, fill=incidence)) + 
  geom_tile(colour="white",
            width=.9, height=.9) + theme_minimal() +
  scale_fill_gradientn(colours=cols, limits=c(0, 4000),
                       values=c(0, 0.01, 0.02, 0.03, 0.09, 0.1, .15, .25, .4, .5, 1), 
                       na.value=rgb(246, 246, 246, max=255),
                       labels=c("0k", "1k", "2k", "3k", "4k"),
                       guide=guide_colourbar(ticks=T, nbin=50,
                                             barheight=.5, label=T, 
                                             barwidth=10))

gg <- gg +
  scale_x_continuous(expand=c(0,0), 
                     breaks=seq(1930, 2010, by=10)) +
  geom_segment(x=1963, xend=1963, y=0, yend=51.5, size=.9) +
  labs(x="", y="", fill="") +
  ggtitle("Measles")

gg <- gg +
  theme(legend.position=c(.5, -.13),
        legend.direction="horizontal",
        legend.text=element_text(colour="grey20"),
        plot.margin=grid::unit(c(.5,.5,1.5,.5), "cm"),
        axis.text.y=element_text(size=6, family="Open Sans Regular", 
                                 hjust=1),
        axis.text.x=element_text(size=8, family="Open Sans Regular"),
        axis.ticks.y=element_blank(),
        panel.grid=element_blank(),
        title=element_text(hjust=-.07, vjust=1, 
                           family="Open Sans Semibold"),
        text=element_text(family="Open Sans")) +
  annotate("text", label="Vaccine introduced in 1963", x=1963, y=53, 
           vjust=1, hjust=0, size=I(3), family="Open Sans")

gg
