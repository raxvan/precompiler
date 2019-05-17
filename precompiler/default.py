
import precompiler._impl.pc_vm as _impl_pc_vm
import precompiler._impl.pc_iterator as _impl_pc_iterator
import precompiler._impl.pc_define as _impl_pc_define
import precompiler._utils.pc_utils as _pc_utils
import time



#all functions exposed to the user
class context(_impl_pc_vm._precompiler_backend):

	#`options` are defined in __init__.py as `Features` function
	#`file_handler` should be result of createFileInterface() or implementation inherited from `DefaultFileManager`
	def __init__(self,file_handler,options):
		_impl_pc_vm._precompiler_backend.__init__(self,file_handler, options)

		self.run_iterations = 0
		self.run_time = 0

		self.Reset(False)

	#adds user functions to `eval` context
	def ResetEvalContext(self,user_ctx):
		self.eval_user_context = user_ctx
		self._invalidate_eval_ctx()

	#reset preprocessor to initial state. This is required if you don't want to rebuild the context for multiple Runs
	def Reset(self,reset_stats):
		if reset_stats:
			self.run_iterations = 0
			self.run_time = 0

		if self._dependency_list != None:
			self._dependency_list = []

		#reset file interface
		self.file_interface.ResetFileSystem(reset_stats)

		#rebuild internal structure
		self.input_state = _impl_pc_iterator.ParsingContextStack()

		self._invalidate_eval_ctx()

	#returns the file handler
	def AddInputFile(self,abs_file_path):
		self.init_default_macros()
		file_handle = self.file_interface.GetOrLoadFile(abs_file_path)
		file_token_iterator = _impl_pc_iterator.FileTokenInterator(file_handle.tokens(),abs_file_path,[])
		self.input_state.PushState(file_token_iterator,None)
		return file_handle

	#flags are defined in __init__.py
	def SetOutputFile(self,abs_file_path, flags):
		output_handle = self.file_interface.CreateAssembler(abs_file_path,flags);
		self.parser_state = _impl_pc_vm._pc_root_parser(self,output_handle)
		return output_handle

	#when you want to run the precompiler on a file without outputting anything.
	def SetOutputToBlank(self):
		output_handle = _pc_utils.EmptyAssembler()
		self.parser_state = _impl_pc_vm._pc_root_parser(self,output_handle)

	#define with value
	def AddUserDefineValue(self,define_name,string_value):
		tokens = _pc_utils.precompiler_tokens
		tok_def = (_pc_utils.precompiler_tokens.k_define, 0, (define_name,None,string_value), ["user", -1] )
		self.input_state.AddGlobalDefine(_impl_pc_define.VarDefine(define_name,string_value,None,tok_def,self))

	#without value
	def AddUserDefine(self,define_name):
		tokens = _pc_utils.precompiler_tokens
		tok_def = (_pc_utils.precompiler_tokens.k_define, 0, (define_name,None,""), ["user", -1] )
		self.input_state.AddGlobalDefine(_impl_pc_define.VarDefine(define_name,None,None,tok_def,self))

	#returns a bunch if debug info
	def GetStats(self):
		return {
			"io" : self.file_interface.GetStats(),
			"vm_seconds" : self.run_time,
			"iterations" : self.run_iterations,
		}

	#returns a list of dependencyes; each dependency is a tuple (source,dependency_abs_path,dependency_content_hash)
	def Run(self):
		_start_time = time.time()

		#eval loop
		_itr = 0

		while True:
			tok = self.input_state.GetNextToken()
			if tok == None:
				break #end of input
			#print(tok,"\n")
			self.parser_state = self.parser_state.Advance(tok)

			_itr += 1;

		self.parser_state.Finish()
		#end of processing

		_end_time = time.time()
		self.run_time += (_end_time - _start_time)
		self.run_iterations += _itr

		return self._dependency_list


##########################################################################################################


