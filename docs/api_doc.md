
Python Api Documentation
------------------------

Running the precompiler the easiet way:
```
import precompiler
def run_precompiler(input_file_path,out_file_path):
	lexer = precompiler.createLexer()
	fi = precompiler.createFileInterface(lexer)
	ctx = precompiler.createContext(fi,None)
	ctx.AddInputFile(input_file_path)
	ctx.SetOutputFile(out_file_path,None)
	ctx.Run()
	
run_precompiler("path/to/file.txt","path/to/output_file.txt")
```

