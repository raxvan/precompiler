
import precompiler._impl.pc_define as _impl_pc_define

class TokenInterator():
	def __init__(self,tok_list):
		self.tok_iterator = iter(tok_list)
		self.input_tokens = tok_list

		self.next = None
		self.scope = None

	def AdvanceToNextToken(self):
		try:
			return self.tok_iterator.__next__()
		except StopIteration:
			return None

	def Stop(self):
		pass

###########################################################################################################

class GeneratedTokenInterator(TokenInterator):
	def __init__(self,tok_list):
		TokenInterator.__init__(self,tok_list)

	def GetFileUnit(self):
		if self.next != None:
			return self.next.GetFileUnit()
		return None

	def GetRootFileUnit(self):
		if self.next != None:
			return self.next.GetRootFileUnit()
		return None

	def IsFileUnit(self):
		return False

###########################################################################################################

class FileTokenInterator(TokenInterator):
	def __init__(self,tok_list,abs_file_path,_unit_state):
		TokenInterator.__init__(self,tok_list)
		self.abs_file_path = abs_file_path
		self.unit_state = _unit_state

	def GetFileUnit(self):
		return self.abs_file_path

	def GetRootFileUnit(self):
		if self.next != None:
			result = self.next.GetRootFileUnit()
			if result != None:
				return result
		return self.abs_file_path

	def IsFileUnit(self):
		return True

	def GetUnitState(self):
		return self.unit_state

###########################################################################################################

class ColapsedTokenInterator(TokenInterator):
	def __init__(self,collapse_tok,tok_list,precompiler):
		TokenInterator.__init__(self,tok_list)
		self.precompiler = precompiler
		self.tok = collapse_tok

	def GetFileUnit(self):
		if self.next != None:
			return self.next.GetFileUnit()
		return None

	def GetRootFileUnit(self):
		if self.next != None:
			return self.next.GetRootFileUnit()
		return None

	def IsFileUnit(self):
		return False

	def Stop(self):
		self.precompiler.close_collapse(self.tok)

###########################################################################################################

class ParsingContextStack(object):
	def __init__(self):

		self.current_iterator = None

		self.stack_depth = 0

		self.root_define_map = _impl_pc_define.VarDefineMap()

	def PushState(self,next_iterator,local_defines_map):
		#check for stack overflow
		self.stack_depth += 1
		if self.stack_depth > 1024:
			return False;


		next_iterator.next = self.current_iterator

		if local_defines_map != None:
			next_iterator.scope = local_defines_map;
			local_defines_map.SetParentMap(self.current_iterator.scope)
		elif self.current_iterator != None:
			next_iterator.scope = self.current_iterator.scope
		else:
			next_iterator.scope = self.root_define_map

		self.current_iterator = next_iterator

		return True

	def GetNextToken(self):
		itr = self.current_iterator;
		while itr != None:
			t = itr.AdvanceToNextToken()
			if t != None:
				self.current_iterator = itr
				return t
			itr.Stop()
			itr = itr.next

		return None

	def BreakFileUnit(self):
		itr = self.current_iterator;
		while itr != None:
			if itr.IsFileUnit() == True:
				break;
			itr = itr.next

		state = itr.GetUnitState();
		self.current_iterator = itr.next

		return state

	def FindVarDefineWithName(self,name):
		return self.current_iterator.scope.FindVarDefineWithName(name)

	def AddGlobalDefine(self,define_instance):
		self.root_define_map.TryAddLocalDefine(define_instance)

	def AddLocalDefine(self,define_instance):
		self.current_iterator.scope.TryAddLocalDefine(define_instance)

	def RemoveDefineRecursive(self,define_name):
		if self.current_iterator.scope.TryUndefineRecursive(define_name) == False:
			return False
		return True

	def GetActiveSourceFile(self):
		return self.current_iterator.GetFileUnit();

	def GetRootSourceFile(self):
		return self.current_iterator.GetRootFileUnit();

###########################################################################################################

class PrecompilerExecController(object):
	def __init__(self,vm):
		self.precompiler = vm

	def Advance(self,tok):
		pass

	def Finish(self):
		pass
