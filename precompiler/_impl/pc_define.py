
import precompiler._utils.pc_utils as _pc_utils

class MacroBase(object):
	def __init__(self,name, source_token,preprocessor):
		self.name = name

		self.source_token = source_token #token that created this
		self.preprocessor = preprocessor

	def GetDefinitionToken(self):
		return self.source_token

	def GetValueAsTokens(self,tok):
		assert False, "Internal error!"
		pass

	def GetRequiredArguments(self):
		return None

	def IsBuiltin(self):
		return False

	def GetValueAsString(self,tok):
		return _pc_utils.TokListJoinValue(self.GetValueAsTokens(tok));

#	def TokenCount(self,tok):
#		tokens = self.GetValueAsTokens(tok)
#		return len(tokens)
#
#	def TokenCountNoCW(self,tok):
#		tokens = self.GetValueAsTokens(tok)
#		sz = 0
#		for t in tokens:
#			if t[1] != _pc_utils.primitive_tokens.kComment and t[1] != _pc_utils.primitive_tokens.kWhitespace:
#				sz += 1
#		return sz

class VarDefineStatic(MacroBase):
	def __init__(self,name, value_str_or_tokens,source_token,preprocessor):
		MacroBase.__init__(self,name,source_token,preprocessor)

		if value_str_or_tokens == None:
			#empty define
			self.value_tok_list = []
		elif isinstance(value_str_or_tokens, str):
			self.value_tok_list = self.preprocessor.file_interface.RetokenizeContent(value_str_or_tokens,self.source_token)
		elif isinstance(value_str_or_tokens, list):
			self.value_tok_list = value_str_or_tokens

	def GetValueAsTokens(self,tok):
		#remap tokens ?
		return [_pc_utils.RelocateTokenAtExpandedToken(t,tok) for t in self.value_tok_list]

	def ClearValue(self):
		self.value_tok_list = []

	def ApeendTokenToValue(self,tok_tuple):
		self.value_tok_list.append(tok_tuple);

	def CwStrip(self):
		tokens = self.value_tok_list
		new_tokens = [t for t in tokens if t[1] != _pc_utils.primitive_tokens.kComment and t[1] != _pc_utils.primitive_tokens.kWhitespace]
		self.value_tok_list = new_tokens

class VarDefineDynamic(VarDefineStatic):
	def __init__(self,name,arg_tokens, value_str_or_tokens,source_token,preprocessor):
		VarDefineStatic.__init__(self,name,value_str_or_tokens, source_token,preprocessor)
		self.arguments_list = arg_tokens #if null then define has no arguments

	def GetRequiredArguments(self):
		return self.arguments_list

###########################################################################################################

def VarDefine(name,arg_tokens, value_str_or_tokens,source_token,preprocessor):
	if arg_tokens == None:
		return VarDefineStatic(name,value_str_or_tokens,source_token,preprocessor)
	else:
		return VarDefineDynamic(name,arg_tokens, value_str_or_tokens,source_token,preprocessor)


###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################

class VarDefineMap(object):
	def __init__(self):
		self.parent = None

		self.local_defines = {}

	def SetParentMap(self,pm):
		self.parent = pm

	def GetParent(self):
		return self.parent

	def FindVarDefineWithName(self,name):
		ad = self.local_defines.get(name,None)
		if ad != None:
			return ad

		if self.parent != None:
			return self.parent.FindVarDefineWithName(name)

		return None

	def TryAddLocalDefine(self,define_instance):
		ad = self.local_defines.get(define_instance.name,None)
		if ad != None:
			return False
		self.local_defines[define_instance.name] = define_instance
		return True

	def TryUndefineLocal(self,name):
		ad = self.local_defines.get(name,None)
		if ad != None:
			del self.local_defines[name]
			return True
		return False

	def TryUndefineRecursive(self,name):
		if (self.TryUndefineLocal(name) == True):
			return True
		elif self.parent != None:
			return self.parent.TryUndefineRecursive(name)
		return False

###########################################################################################################