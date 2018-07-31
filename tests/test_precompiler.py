
import precompiler
import sys


def test_file(infile,outfile,options):
	lexer = precompiler.createLexer()
	fi = precompiler.createFileInterface(lexer)
	ctx = precompiler.createContext(fi,None)
	ctx.AddInputFile(infile)
	ctx.SetOutputFile(outfile,options)
	ctx.Run()


test_file(sys.argv[1],sys.argv[1] + ".pp",None)
