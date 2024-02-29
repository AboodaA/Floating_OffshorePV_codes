##Just add the normalized yields advantages to all files

list_of_advantages_files = list.files("/home/abed/Documents/begin_analysis/november/advantages_data_november/")
setwd("/home/abed/Documents/begin_analysis/november/advantages_data_november/")
for(i in 1:length(list_of_advantages_files))
{
  opened_advantages_file = openxlsx::read.xlsx(list_of_advantages_files[i])
  opened_advantages_file$Y_adv_B_normal = 0 
  for(i in 1:nrow(opened_advantages_file))
  {
    oaoy = opened_advantages_file$Y_offshore_B[i]
    oaiy = opened_advantages_file$Y_inland_B[i]
    oaya = opened_advantages_file$Y_adv_B[i]
    if(oaoy >= 0 & oaiy >= 0 & oaya > 0)
    {
      opened_advantages_file$Y_adv_B_normal[i] = (oaoy - oaiy)/mean(c(oaoy, oaiy))
    }
    
  }
  print(paste("We have done the file at index", i, sep = " "))
  Sys.sleep(3)
}


##In an earlier version, this is what it looked like 

#november_normalize_advantages <- function(advantgaes_data, file_name)
#{
#  #We will do this for all rows, and then for the summary data use
#  # only the 
#  advantgaes_data$Y_adv_B_normal = 0
#  for(i in 1:nrow(advantgaes_data))
#  {
#    
#    if(advantgaes_data$removerow == 0)
#    {
#      #Create the normalized advantage in yield 
#      #For readibility, I will break it up like this 
#      mean_of_yields = mean(c(advantgaes_data$Y_inland_B[i], advantgaes_data$Y_offshore_B[i]))      
#      advantgaes_data$Y_adv_B_normal[i] = advantgaes_data$Y_adv_B[i]/mean_of_yields
#    }
#    
#    else
#    {
#      advantgaes_data$Y_adv_B_normal[i] = 0 
#    }
#    
#  }
#  
#  openxlsx::write.xlsx(advantgaes_data, file = file_name, overwrite = TRUE)
#  length_of_colnames = length(colnames(advantgaes_data))
#  print(colnames(advantgaes_data)[length_of_colnames])
#  #return(advantgaes_data)
#}
