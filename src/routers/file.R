 options(repos = c(CRAN = "https://cran.r-project.org"))


#  install.packages("magrittr")
#  install.packages("rmarkdown")
# install.packages("bupaR")
# install.packages("curl")
# install.packages("DiagrammeR")
# install.packages("plotly")
# install.packages("openssl")
#  install.packages("igraph")
# install.packages("plotly")
#  install.packages("DiagrammeR")
# install.packages("processmapR")
# install.packages("processanimateR")
#    install.packages("dplyr")
#  install.packages("igraph’")
#      install.packages("xesreadR")
#     install.packages("processanimateR")


require("curl")
require("bupaR")
require("xesreadR")
require("processanimateR")

library(dplyr)
library(bupaR)
library(xesreadR)
library(processanimateR)


animate_csv <- function(csv_path) {

    if (endsWith(csv_path, ".csv")) {
        log <- read.csv(csv_path, sep = ';')
    } else {
        stop("Wrong file format")
    }

#     log = read.csv('src/logs/Digital-Library-logs.csv',sep=';')
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

    htmlwidgets::saveWidget(animation, file = "animation_csv.html", selfcontained = FALSE)

#     options(browser = "kfmclient newTab")
     browseURL("animation_csv.html")
 }


# animating xes files ::

animate_xes <- function(xes_path) {

    if (endsWith(xes_path, ".xes")) {
        log <- read_xes(xes_path)
    } else {
        stop("Wrong file format")
    }

# log = read_xes('src/logs/running-example.xes')
#   log = read_xes(xes_path)
  animation <- animate_process(log,
                         mode = "relative", jitter = 10, legend = "color",
                         mapping = token_aes(color = token_scale("users",
                         scale = "ordinal",
                         range = RColorBrewer::brewer.pal(7, "Paired"))))

htmlwidgets::saveWidget(animation, file = "animation_xes.html", selfcontained = FALSE)
browseURL("animation_xes.html")

}


args <- commandArgs(trailingOnly = TRUE)
file_path <- args[1]

if (endsWith(file_path, ".csv")) {
        animate_csv(file_path)
    } else if (endsWith(file_path, ".xes"))  {
       animate_xes(file_path)
    }
    else {
        return "You provided the wrong file format"
    }

