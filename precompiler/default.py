
import precompiler._impl.pc_vm as _impl_pc_vm
import precompiler._impl.pc_iterator as _impl_pc_iterator
import precompiler._impl.pc_define as _impl_pc_define
import precompiler._utils.pc_utils as _pc_utils
import time

#all functions exposed to the user
class context(_impl_pc_vm._precompiler_backend):
	def __init__(self,file_handler,options):
		_impl_pc_vm._precompiler_backend.__init__(self,file_handler, options)

		self.run_iterations = 0
		self.run_time = 0

		self.Reset()

	#adds user functions to `eval` context
	def ResetEvalContext(self,user_ctx):
		self.eval_user_context = user_ctx
		self._invalidate_eval_ctx()

	#reset preprocessor to zero
	def Reset(self):
		self.run_iterations = 0
		self.run_time = 0

		#reset file interface
		self.file_interface.ResetFileSystem()

		#rebuild internal structure
		self.input_state = _impl_pc_iterator.ParsingContextStack()

		self._invalidate_eval_ctx()

	#reset parsing and
	def AddInputFile(self,abs_file_path):
		file_token_iterator = _impl_pc_iterator.FileTokenInterator(self.file_interface.GetFileTokens(abs_file_path),abs_file_path,[])
		self.input_state.PushState(file_token_iterator,None)

	def SetOutputFile(self,abs_file_path, flags):
		output_handle = self.file_interface.CreateAssembler(abs_file_path,flags);
		self.parser_state = _impl_pc_vm._pc_root_parser(self,output_handle)

	def SetOutputToBlank(self):
		output_handle = _pc_utils.EmptyAssembler()
		self.parser_state = _impl_pc_vm._pc_root_parser(self,output_handle)

	def AddUserDefineValue(self,define_name,string_value):
		tokens = _pc_utils.precompiler_tokens
		tok_def = (_pc_utils.precompiler_tokens.k_define, 0, (define_name,None,string_value), ["user", -1] )
		self.input_state.AddGlobalDefine(_impl_pc_define.VarDefine(define_name,string_value,None,tok_def,self))

	def AddUserDefine(self,define_name):
		tokens = _pc_utils.precompiler_tokens
		tok_def = (_pc_utils.precompiler_tokens.k_define, 0, (define_name,None,""), ["user", -1] )
		self.input_state.AddGlobalDefine(_impl_pc_define.VarDefine(define_name,[],None,tok_def,self))

	def GetStats(self):
		return {
			"io" : self.file_interface.GetStats(),
			"vm_seconds" : self.run_time,
			"iterations" : self.run_iterations,
		}

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


##########################################################################################################


