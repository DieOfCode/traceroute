Traceroute
===

Installing
-------

    git clone https://github.com/DieOfCode/traceroute.git

    pip install -r requirements.txt
    
Start
----
    sudo python3 main.py --host <host> --port <port> 
  
Example
----
    sudo python3 main.py --host yandex.ru 

    1:router.asus.com (192.169.0.1) 8ms router.asus.com (192.169.0.1) 5ms router.asus.com (192.169.0.1) 6ms , TYPE:11, CODE:0
    2: (172.23.27.1) 6ms  (172.23.27.1) 6ms  (172.23.27.1) 5ms , TYPE:11, CODE:0
    3:Algai-bb-ov122.ural.net (195.64.219.81) 6ms Algai-bb-ov122.ural.net (195.64.219.81) 6ms Algai-bb-ov122.ural.net (195.64.219.81) 5ms , TYPE:11, CODE:0
    4:BlackBox-ov306.ural.net (195.64.220.243) 5ms BlackBox-ov306.ural.net (195.64.220.243) 6ms BlackBox-ov306.ural.net (195.64.220.243) 6ms , TYPE:11, CODE:0
    5:OnePower-bb2-ov9.ural.net (87.251.181.7) 6ms OnePower-bb2-ov9.ural.net (87.251.181.7) 6ms OnePower-bb2-ov9.ural.net (87.251.181.7) 6ms , TYPE:11, CODE:0
    6:TwoPower-v120.Ural.Net (87.251.181.51) 70ms TwoPower-v120.Ural.Net (87.251.181.51) 59ms TwoPower-v120.Ural.Net (87.251.181.51) 7ms , TYPE:11, CODE:0
    7: (185.1.160.87) 44ms  (185.1.160.87) 43ms  (185.1.160.87) 43ms , TYPE:11, CODE:0
    8: (*) 10014ms  (10.1.3.1) 50ms yandex.ru (77.88.55.50) 50ms , TYPE:3, CODE:3


    
Command
----

    
| Command       | info                | 
| :------------- |:------------------:|
| -p --port     | Specify the port   | 
|  --host     | Specify the host|   
| -f --first_ttl|number of ttl at first start|
| -m --max_hops|number of maximum ttl |
 