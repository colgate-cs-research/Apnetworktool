library(readr)
data <- read_csv("data.csv")
randomRows = sample(data, 10, replace = T)
i = 1
for (x in randomRows){
  png(names(randomRows)[i])
  plot(ecdf(x), main = names(randomRows)[i])
  dev.off()
  i <- i+1
}
