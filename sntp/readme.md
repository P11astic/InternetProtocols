## Liar SNTP
This is __SNTP__ server that "lies" for `${N}` seconds.<br>
Variable `${N}` ___must___ be the only line in file "config.txt"
********
### How to use
To run the script type at comand prompt<br>
`cd ${PATH}`<br>
where `${PATH}` is path to the scipt on your computer<br>
And then type<br>
`python3 liarSNTP.py`<br>
add extra options for launch by using keys if needed.<br>
List of keys is shown by typing<br>
`python3 liarSNTP.py -h`<br>
in comand prompt
*******
### Examples of use
#### Raw usage without keys
![Raw usage without keys](screens/raw.png)
#### Cases with keys
![With key "-r"](screens/rKey.png)<br>
![With key "-s"](screens/sKey.png)<br>
![With both](screens/both.png)

### Main modules
* `main` - cerates socket with imported library `socket`, binds it to port 123
* after receiving an SNTP packet it calls `unpack`
* `unpack` - unpacks SNTP packet
* then `main` calls `make_packet`
* pretty obvious what does `make_packet` method ;) (it makes SNTP packet and changes _only_ one field "Reference")
* and last but not least, `get_shift` - reads "config.txt" and returns current time with shift from config divided into two numbers - integer and fractional part
* the freshly made packet is sent to port 123