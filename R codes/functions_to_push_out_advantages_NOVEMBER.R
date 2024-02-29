#This was updated on 25 July 2023
library(readxl)
library(openxlsx)
#first_inland_data = read_xlsx("/home/abed/Documents/begin_analysis/trial_balloon/inland.xlsx")
#first_offshore_data = read_xlsx("/home/abed/Documents/begin_analysis/trial_balloon/offshore.xlsx")

create_advantages_data_NOVEMBER <- function(inland_data, offshore_data, name_of_site)
{
  #We will need this for those sites which do not have "T2M" in their column headings, etc
  '%notin%' <- Negate('%in%')
  
  if("T2M" %notin% colnames(inland_data))
  {
    inland_data$T2M = inland_data$additional_columns
  }
  
  else if("WS2M" %notin% colnames(inland_data))
  {
    inland_data$WS2M = inland_data$additional_columns
  }
  
  
  G_stc = 1000
  colnames(offshore_data) = trimws(colnames(offshore_data))
  colnames(inland_data) = trimws(colnames(inland_data))
  
  #Note the use of G_STC 
  
  apparent_yields_inland = inland_data$module_eta_method2*(inland_data$poa_calculated/G_stc)
  yields_inland_new_method = inland_data$module_eta_method1*(inland_data$poa_calculated/G_stc)
  
  

  
  apparent_yields_offshore = offshore_data$module_eta_RM*(offshore_data$poa_for_offshore/G_stc)
  #Note that we did not use the apparent temperature/heat index in the calculations for the offshore sites
  #We will keep this one here for clarity 
  second_yields_offshore = apparent_yields_offshore
  yields_advantage_new_method = second_yields_offshore - yields_inland_new_method
  
  
  apparent_yield_advantages = apparent_yields_offshore - apparent_yields_inland
  
  
  removerow = offshore_data$poa_for_offshore
  for(i in 1:length(removerow))
  {
    if(offshore_data$poa_for_offshore[i] < 50 | inland_data$poa_calculated[i] < 50)
    {
      removerow[i] = 1
    }
    
    else
    {
      removerow[i] = 0 
    }
  }
  
  
  
  print("App Y inland")
  print(length(apparent_yields_inland))
  print("App Y offshore")
  print(length(apparent_yields_offshore))
  print("Diff in Y")
  print(length(apparent_yield_advantages))
  
  efficiency_advantage = offshore_data$module_eta_RM - inland_data$module_eta_method2
  
  inland_poa = inland_data$poa_calculated
  offshore_poa = offshore_data$poa_for_offshore
  
  delta_vw = rep(0, nrow(offshore_data))
  delta_prec = rep(0, nrow(offshore_data))
  delta_G = rep(0, nrow(offshore_data))
  for(i in 1:length(delta_vw))
  {
    delta_vw[i] = (offshore_data$WS2M[i] - inland_data$WS2M[i])/(mean(c(offshore_data$WS2M[i], inland_data$WS2M[i])))
    delta_prec[i] = (offshore_data$PRECTOTCORR[i] - inland_data$PRECTOTCORR[i])/(mean(c(offshore_data$PRECTOTCORR[i], inland_data$PRECTOTCORR[i])))
    delta_G[i] = (offshore_data$poa_for_offshore[i] - inland_data$poa_calculated[i])/mean(c(offshore_data$poa_for_offshore[i], inland_data$poa_for_inland[i]))
  }
  
  
  
  #print("offshore poa")
  #print(offshore_poa)
  
  ambient_temperature_inland = inland_data$T2M
  #Come back here so that we can print out the actual heat index temperatures 
  #heat_index_temperature = inland_data$HI_temp
  water_temperature = offshore_data$TS
  
  
  print("Ambient temp")
  print("Water temp")
  Tcell_inland = inland_data$cell_temp_method2
  Tcell_inland_B = inland_data$cell_temp_method1
  Tcell_offshore = offshore_data$TempC_RM
  print("T cell on land")
  print("T cell on water")

  
  df_of_results = data.frame(cbind(apparent_yield_advantages, apparent_yields_offshore, apparent_yields_inland, 
                                   second_yields_offshore,
                                   yields_inland_new_method,
                                   yields_advantage_new_method,
                                   offshore_poa, inland_poa, delta_G, ambient_temperature_inland, water_temperature, 
                                   Tcell_inland, Tcell_inland_B, Tcell_offshore, delta_vw, delta_prec,removerow), stringsAsFactors = FALSE)
  
  print("Rows of data")
  print(nrow(df_of_results))
  
  colnames(df_of_results) = c("Y_adv", "Y_offshore", "Y_inland", "Y_offshore_B", "Y_inland_B", "Y_adv_B","G_offshorePOA", "G_inland_POA", "delta_G_POA",
                              "T2M", "TS", "Tcell_inland", "Tcell_inland_B", "Tcell_offshore", "delta_windspeed", "Delt_PREC","removerow")
  print(mean(apparent_yields_inland))
  
  #filename = paste0("/home/abed/Documents/begin_analysis/trial_balloon/", name_of_site, ".xlsx")
  #openxlsx::write.xlsx(df_of_results, filename, overwrite = TRUE)
  return(df_of_results)
}

#November function to re-write the normalization of the advantages for yields
##See the separate file, make_yields_advantages_normalized.R



#Here's a new function to do a quick summary of what we are looking for
november_summary_advantages <- function(reading_data)
{
  #Exclude the funny stuff
  reading_data = reading_data[which(reading_data$removerow == 0),]
  #The weird thing R does with averages
  average_yield_adv_B = sum(reading_data$Y_adv_B)/nrow(reading_data)
  return(average_yield_adv_B)
}

# summarize_advantage_data <- function(advantages_data)
# {
#   #Only keep the data we want
#   advantages_data = advantages_data[which(advantages_data$removerow == 0),]
#   
#   averaged_out = sum(advantages_data$Y_adv_normal)/nrow(advantages_data)
#   return(averaged_out)
# }
