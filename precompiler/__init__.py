__all__ = ["createLexer","createFileInterface","createContext","OutOptions","Features"]

def _getExceptionClass():
	import precompiler._utils.pc_utils
	return precompiler._utils.pc_utils.SourceCodeError

SourceCodeError = _getExceptionClass()

def createLexer():
	import precompiler._lexers.cpp_family_lexer
	return precompiler._lexers.cpp_family_lexer


def createFileInterface(_lexer_interface):
	import precompiler._impl.pc_file_manager
	return precompiler._impl.pc_file_manager.DefaultFileManager(_lexer_interface)


def createContext(file_interface,options):
	import precompiler.default
	result = precompiler.default.context(file_interface,options)
	return result

def version():
	import precompiler._version.pc_version
	return (precompiler._version.pc_version._PCVER_HIGH_, precompiler._version.pc_version._PCVER_LOW0_, precompiler._version.pc_version._PCVER_LOW1_)

class OutOptions:
	remove_comments = 1 << 0 #-> removes all comments
	collapse_endlines = 1 << 2 #-> collapses multiple endlines into one endline ("\n)
	collapse_whitespaces = 1 << 3 #-> collapses whitespaces to " " or to "\n"; this is a superset of `collapse_endlines`
	try_whitespace_removal = 1 << 4 #-> will try to remove whitespaces when it's possible
	#track_touched_files = 1 << 5 #-> keeps track of all loaded files for later use


def Features():
	return {
		"MakeDependencyTree" : False, #returns a list with tuples; values from tuple (A,B) indicate that file path A has file path B as a dependency
		"SourceOnceByDefault" : False,
		"EvalContext" : None
	}

