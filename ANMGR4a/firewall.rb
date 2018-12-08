#!/usr/bin/env ruby


require 'rubygems'
require 'mysql'

# -- Configuration -- #

# MySQL database:
@db_host = "192.168.185.52"
@db_name = "anm"
@db_user = "root"
@db_password = "root"



# Your iptables firewall startup script:
firewall_script = "/etc/init.d/firewall.sh"

# Location of touchfile that gets notified when the database changes:
ban_touchfile = "/tmp/blockit"

# Check touchfile every n seconds:
loop_time = 1

# -- Don't change below this line unless you know what you are doing -- #

# Initial values
last_ban = 0
@current_chain = 0
@next_expiry = nil

# Restart Firewall to clean up the mess me may have made
system(firewall_script) if firewall_script



# The IP blocking method
def ipblock
  # Alternate chains
  @old_chain = @current_chain
  @current_chain = (@current_chain == 1) ? 0 : 1
  # Flush chain
  system("iptables -N banned_ips#{@current_chain} 2>/dev/null")
  system("iptables -F banned_ips#{@current_chain}")
  dbh = Mysql.real_connect(@db_host, @db_user, @db_password, @db_name)
  # Get all banned IPs
  result = dbh.query("SELECT ip, expiry FROM hosts_ban WHERE expiry > NOW()")
  while row = result.fetch_hash do
    # Add IP to chain
    system("iptables -A banned_ips#{@current_chain} -s #{row["ip"]} -j DROP")
  end
  result.free if result
  # Get next expiry date
  result = dbh.query("SELECT MIN(expiry) AS next_expiry FROM hosts_ban WHERE expiry > NOW()")
  if row = result.fetch_hash and row["next_expiry"]
    t = row["next_expiry"].split(/-|:|\s/)
    @next_expiry = Time.mktime(t[0], t[1], t[2], t[3], t[4], t[5])
  else
    @next_expiry = nil
  end
  dbh.close if dbh
  # Insert chain in INPUT
  system("iptables -I INPUT -j banned_ips#{@current_chain}")
  # Delete old chain
  system("iptables -D INPUT -j banned_ips#{@old_chain} 2>/dev/null")
  system("iptables -F banned_ips#{@old_chain}")
  system("iptables -X banned_ips#{@old_chain}")
end

# Main loop
loop do
  # IP block
  if File.mtime(ban_touchfile) != last_ban or (@next_expiry and Time.now > @next_expiry)
    ipblock
    last_ban = File.mtime(ban_touchfile)
  end
  # Wait loop_time seconds
  sleep(loop_time)
end