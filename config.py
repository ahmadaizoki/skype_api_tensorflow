# -*- coding: utf-8 -*-
db_url="postgres://xpmqhxcaiquvwy:7b300499f98a11666ffc1d3a14f2bba8d17859bed31e3f9f37451e2c57ba00ec@ec2-79-125-125-97.eu-west-1.compute.amazonaws.com:5432/db63uu5csa2t5l" #connexion avec la base de données
message_noIntent="je comprends pas ce que vous voulez me dire!" #message de pas detecter les intentions
data_set="intents.json" #le data sets
data="hod_1022.json" #les données
id_Micosoft="f6a6d0ee-1856-4c36-a545-a427aef5a001" # Microsoft ID
password_Microsoft="MS3JDeGrSLmeHaHpqTtgvsS" # Microsoft password
message_data_null="Désolé, j'ai pas les informations demandées. Veillez conntacter :" #s'il y a pas de data
fb_access_token="EAAT60LMwcGABAP3WMtxBc1fZAWMlmP4TqtSRKKDRn6AnN1naZA4MgNyXGZB3JCfn8u6DFfMGwl8da9W4ZCHBeFI0opQvqanr57jZC7KWitxOJteRDfT4OzbYgVJT9qRL6xOx0ZAXCoLCdK2xk7yZAlOe3IZCzTOoaAn5XFMRvkZAS3gZDZD" #facebook access token
fb_verifing_token="Accorhotels" #facebook verifing token
import gif
deRien=gif/deRien.gif
################################################################################
import json

with open(data) as horaires_data:
    horaires=json.load(horaires_data)
##################################################################################
breakfasts_period_from=horaires["hotels"]["breakfasts"]["schedules"][0]["days"][0]["time_slots"][0]["time_from"]
breakfasts_period_to=horaires["hotels"]["breakfasts"]["schedules"][0]["days"][0]["time_slots"][0]["time_to"]
breakfasts_date_from=horaires["hotels"]["breakfasts"]["schedules"][0]["date_from"]
breakfasts_date_to=horaires["hotels"]["breakfasts"]["schedules"][0]["date_to"]
###################################################################################
fitness_period_from=horaires["hotels"]["wellness_fitness"]["fitness_centers"][0]["fitness_center_schedules"][0]["days"][0]["time_slots"][0]["time_from"]
fitness_period_to=horaires["hotels"]["wellness_fitness"]["fitness_centers"][0]["fitness_center_schedules"][0]["days"][0]["time_slots"][0]["time_to"]
fitness_date_from=horaires["hotels"]["wellness_fitness"]["fitness_centers"][0]["fitness_center_schedules"][0]["date_from"]
fitness_date_to=horaires["hotels"]["wellness_fitness"]["fitness_centers"][0]["fitness_center_schedules"][0]["date_to"]
###################################################################################
