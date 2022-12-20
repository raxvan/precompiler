
import precompiler
import sys
import os

def test_file(infile,outfile,options, msgcheck):
	lexer = precompiler.createLexer()
	fi = precompiler.createFileInterface(lexer)
	ctx = precompiler.createContext(fi,None)
	ctx.AddInputFile(infile)
	ctx.SetOutputFile(outfile,options)
	try:
		ctx.Run()
	except precompiler.SourceCodeError as e:
		msg = str(e).replace("\r\n","").replace("\n","")
		msgcheck = msgcheck.replace("\r\n","").replace("\n","")
		#print("--:" + msg + ":--")
		#print("--:" + msgcheck + ":--")
		if msg.find(msgcheck) == -1:
			raise Exception("FAILED - [" + infile + "]\n" + msg)
		else:
			print("OK - [" + infile + "]")





path = os.path.join(sys.argv[1],"conditions.txt")
err = """tests/data/error_tests/conditions.txt(1)-> .> Incomplete if/else/endif block!"""
test_file(path,path + ".pp",None,err)

path = os.path.join(sys.argv[1],"conditions_inc.txt")
err = """tests/data/error_tests/conditions_inc.txt(2)->['#include "conditions.txt"', '"conditions.txt"', 2]->> Incomplete if/else/endif block!"""
test_file(path,path + ".pp",None,err)
