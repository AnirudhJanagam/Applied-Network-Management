#! /bin/sh

SLEEP=5
MAX_CONN=5
ban_time=60

   while true; do
        (

                echo "create table ips (ip string);"
                
                echo 'begin transaction;'

sudo capshow  --count=5000 -i ens4 --ip.proto=tcp --tp.dport=22[/MASK] --tp.sport=22 --filter-mode=OR 01::71 01::72 | grep 'TCP: \[S\]' | sed  's/\[[ ]*[0-9]\+\]://' | sed 's/ID([ ]*[0-9]\+)://'  | sed 's/LINK([ ]*[0-9]\+)://'  | sed 's/CAPLEN([ ]*[0-9]\+)://'  | awk '{print $8," to ",$10}'  | awk 'BEGIN{FS="[ :]"}{print $1}' | tr -d ' '|sort |

while read IP;do

echo "insert into ips values ('$IP');"
                
                done

                echo 'commit;'
                
                echo "select ip from (select ip, count(ip) c from ips where ip != '' group by ip having c > $MAX_CONN order by c asc);"
        ) | sqlite3 |\
        
        while read BLOCK; do
#echo "select ip from (select ip, count(ip) c from ips.txt where ip != '' group by ip having c > $MAX_CONN order by c asc);"

echo "use fail2ban; 
INSERT INTO hosts_ban (ip,  ban_time, expiry, last_access) VALUES('$BLOCK', '$ban_time', NOW() + INTERVAL '$ban_time' SECOND, NOW()) ON DUPLICATE KEY UPDATE power = power + 1, expiry = NOW() + INTERVAL ((power)*ban_time) SECOND, last_access = NOW();" | mysql -u root &
 
 done

sleep $SLEEP

done