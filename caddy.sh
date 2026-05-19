  1 # 1. Define the block                                                                                                                                                       
    2 CADDY_BLOCK="phc.alshifalab.pk {                                                                                                                                            
    3     encode zstd gzip                                                                                                                                                        
    4     reverse_proxy 127.0.0.1:8018                                                                                                                                            
    5 }"                                                                                                                                                                          
    6                                                                                                                                                                             
    7 CADDY_FILE="/home/munaim/srv/proxy/caddy/Caddyfile"                                                                                                                         
    8                                                                                                                                                                             
    9 # 2. Check if the block already exists                                                                                                                                      
   10 if grep -q "phc.alshifalab.pk" "$CADDY_FILE"; then                                                                                                                          
   11     echo "Configuration for phc.alshifalab.pk already exists in $CADDY_FILE."                                                                                               
   12     echo "Please verify the port is set to 8018 manually if needed."                                                                                                        
   13 else                                                                                                                                                                        
   14     # 3. Append the block if missing                                                                                                                                        
   15     echo -e "\n$CADDY_BLOCK" >> "$CADDY_FILE"                                                                                                                               
   16     echo "Added phc.alshifalab.pk block to $CADDY_FILE."                                                                                                                    
   17 fi                                                                                                                                                                          
   18                                                                                                                                                                             
   19 # 4. Reload Caddy (Try docker reload first, fallback to systemctl)                                                                                                          
   20 if [ -f "/home/munaim/srv/proxy/caddy/docker-compose.yml" ]; then                                                                                                           
   21     echo "Attempting to reload Caddy via Docker..."                                                                                                                         
   22     cd /home/munaim/srv/proxy/caddy && docker compose exec -t caddy caddy reload --config /etc/caddy/Caddyfile                                                              
   23 else                                                                                                                                                                        
   24     echo "Attempting to reload system Caddy..."                                                                                                                             
   25     sudo systemctl reload caddy                                                                                                                                             
   26 fi                                                                                                                                                                          
                                                                                         
