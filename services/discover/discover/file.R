# options(repos = c(CRAN = "https://cran.r-project.org"))
#


#  install.packages("magrittr")
#  install.packages("rmarkdown")
#  install.packages("dplyr")

#  install.packages("curl")
#  install.packages("igraph’")
#  install.packages("xesreadR")
#  install.packages("processanimateR")
#
#
require("bupaR")
require("xesreadR")
require("processanimateR")
#
library(dplyr)
library(bupaR)
library(processanimateR)

log = read.csv('/home/ania/Desktop/trace_clustering/discover/test/Digital-Library-logs.csv',sep=';')


log$X.timestamp <- as.POSIXct(log$X.timestamp, format = "%Y-%m-%d %H:%M:%OS")

log <- log %>%
  mutate(activity_instance_id = row_number())

log <- log %>%
  group_by(session_id) %>%
  mutate(lifecycle_id = row_number())

# Generate a resource_id based on the 'action' column
log <- log %>%
  mutate(resource_id = as.factor(action))


log <- eventlog(log, case_id = "session_id", activity_id = "action",
                activity_instance_id = "activity_instance_id", lifecycle_id= "lifecycle_id",
                 resource_id= "resource_id", timestamp = "X.timestamp")

animation <- animate_process(log,mode = "relative", jitter = 10, legend = "color",
     mapping = token_aes(color = token_scale("users",
     scale = "ordinal",
     range = RColorBrewer::brewer.pal(7, "Paired"))))

htmlwidgets::saveWidget(animation, file = "animation_output.html")


# animating xes files ::

# log = read_xes('/home/ania/Desktop/trace_clustering/discover/test/running-example')
#
# animation <- animate_process(log,
#                          mode = "relative", jitter = 10, legend = "color",
#                          mapping = token_aes(color = token_scale("users",
#                          scale = "ordinal",
#                          range = RColorBrewer::brewer.pal(7, "Paired"))))
#
# htmlwidgets::saveWidget(animation, file = "animation_xes.html")
