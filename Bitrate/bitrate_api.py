import os, sys
import subprocess
from subprocess import Popen
from bitrate_db import influx
from flask import Flask
from flask import request, Response, make_response
from functools import wraps
import threading
from threading import Thread

dpmi = Flask(__name__)

interface="ens4"

directory="/home/ajheartnett/consumer-bitrate"

password="aj_heartnett001"

global mainstream
mainstream=[]
global streams
streams=[]

def auth(w):
	@wraps(w)
	def q(*args, **kwargs):
		r = request.authorization
		if r and r.username == 'dpmi' and r.password == 'dpmi':
			return w(*args, **kwargs)
		return make_response('\n...Could not verify...\nPlease check the credentials\n', 401, {'WWW-Authenticate' : 'Basic realm = "login required"'})
	return q

def pkill():
	sudo_Password = password
	stop_command = 'sudo pkill bitrate'
	kill = os.system('echo %s|sudo -S %s' % (sudo_Password, stop_command))
	return


def bitrate(str):
	os.chdir(directory)
	bitrate=subprocess.Popen(["unbuffer","./bitrate","-i",interface,str],stdout=subprocess.PIPE)  
	influx_thread=threading.Thread(target=influx,args=(bitrate.stdout,str,)) 
	influx_thread.start()


@dpmi.route('/startstream/<stream>', methods=['GET'])
@auth
def main(stream):
	global mainstream
	mul=stream.split(',')
	if len(mul)>1:
		return '\n...start with only one stream, use "addstream" for adding multiple streams...\n\n'
	else:
		if not streams:
			if stream in mainstream:
				return '\n... bitrate stream %s is already running...\n\n' %stream
			else:
				streams.append(stream) 
				mainstream=mainstream+streams
				bitrate_thread=threading.Thread(target=bitrate,args=(stream,))
				bitrate_thread.deamon=True	
				bitrate_thread.start()
				return '\n...bitrate stream  %s started...\n\n' %stream
		elif stream in mainstream:
			return '\n... bitrate stream %s is already running...\n\n' %stream
		else:
			return '\n...a stream has already been started, use "addstream" to add the streams...\n\n'


@dpmi.route('/showstream', methods=['GET'])
@auth
def show():
	if not mainstream: 
		return '\n...No streams available...\n\n'
	else:
		show=" ".join(str(S) for S in mainstream)
		return '\n...running bitrate streams %s...\n\n' %show


@dpmi.route('/addstream/<add>', methods=['GET'])
@auth
def add(add):
	global mainstream
	
	addstream=add.split(',')
	b=",".join(addstream)	

	already=[]
	already=list(set(addstream).intersection(mainstream)) 
	stralready=" ".join(str(j) for j in already) 

	new=[]
	new=list(set(addstream)-set(already)) 
	strnew=" ".join(str(i) for i in new) 

	mainstream=mainstream+new	
		
	for s in new:
		bitrate_add_thread=threading.Thread(target=bitrate,args=(s,)) 
		bitrate_add_thread.deamon=True	
		bitrate_add_thread.start()

	if not already:
		return '\n...adding bitrate streams %s...\n\n' %strnew
	else:
		return '\n...stream %s already running...\n...streams %s added...\n\n' %(stralready,strnew) 


@dpmi.route('/deletestream/<delet>', methods=['GET'])
@auth
def delete(delet):
	global mainstream
	
	delet=delet.split(',')

	suredel=[]
	suredel=list(set(delet).intersection(mainstream))
	strsuredel=",".join(str(l) for l in suredel) 

	cantdel=[]
	cantdel=list(set(delet)-set(suredel))
	strcantdel=" ".join(str(m) for m in cantdel) 

	mainstream=list(set(mainstream)-set(suredel))
	strmainstream=",".join(str(k) for k in mainstream)


	if not suredel:
		return '\n...stream(s) not available to delete...\n\n'
	else:
		pkill()
		for h in mainstream:
			bitrate_add_thread=threading.Thread(target=bitrate,args=(h,)) 
			bitrate_add_thread.deamon=True	
			bitrate_add_thread.start()
		
		if set(suredel).intersection(streams)!=0 :
			del streams[:]

		if not cantdel:		
			return "\n...bitrate stream %s deleted...\n\n" %(strsuredel)
		else:
			return "\n...bitrate stream %s deleted...\n...bitrate stream %s not available to delete...\n\n" %(strsuredel,strcantdel)		


@dpmi.route('/changestream/<stream>', methods=['GET'])
@auth
def change(stream):

	global ch
	global mainstream

	ch=stream
	if ch in mainstream: 
		return '\n...bitrate stream %s already running, change to another stream...\n\n' %ch		
	else:
		stop()
		del streams[:]
		mainstream=list(set(mainstream)-set(streams))

		main(ch)
		return '\n...bitrate stream changed to %s...\n\n' %ch
	

@dpmi.route('/stop', methods=['GET'])
@auth
def stop():
	pkill()
	del (mainstream[:],streams[:])	
	return "\n...bitrate stream killed...\n\n"	


if __name__ == "__main__":
	dpmi.run(host='localhost', port=5000, debug=True)    
