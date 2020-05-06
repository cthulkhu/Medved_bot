#!/bin/bash
if [ -z "$1" ]
then
	echo Using your IP
else
	t_ip=`ping $1 -c 1 | head -n 1`
	t_from=`expr index "$t_ip" '\('`
	if [ $t_from \> 0 ]
	then
		t_to=`expr index "$t_ip" '\)'`
		t_len=$[$t_to-$t_from-1]
		e_ip=${t_ip:$t_from:$t_len}
	else
		echo Using your IP instead
	fi
fi
curl --no-progress-meter https://ipvigilante.com/$e_ip | jq '"IP: "+.data.ipv4, "Continent: "+.data.continent_name, "Country: "+.data.country_name, "Subdivision 1: "+.data.subdivision_1_name, "Subdivision 2: "+.data.subdivision_2_name, "City: "+.data.city_name, "Lat.: "+.data.latitude, "Long.: "+.data.longitude'
