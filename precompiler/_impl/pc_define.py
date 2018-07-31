
import precompiler._utils.pc_utils as _pc_utils


class VarDefine(object):
	def __init__(self,name,arg_tokens, value_str_or_tokens,source_token,preprocessor):
		self.name = name
		self.arguments_list = arg_tokens #if null then define has no arguments

		self.source_token = source_token #token that created this
		self.preprocessor = preprocessor


		if value_str_or_tokens == None:
			#empty define
			self.value_str = ""
			self.value_tok_list = []
		elif isinstance(value_str_or_tokens, str):
			self.value_str = value_str_or_tokens
			self.value_tok_list = None
		elif isinstance(value_str_or_tokens, list):
			self.value_str = None
			self.value_tok_list = value_str_or_tokens

	def GetDefinitionToken(self):
		return self.source_token

	def GetValueAsString(self):
		if self.value_str == None:
			self.value_str = _pc_utils.TokListJoinValue(self.value_tok_list)
		return self.value_str

	def GetValueAsTokens(self):
		if self.value_tok_list == None:
			if self.value_str != "":
				inherited_loc = _pc_utils.TokSource(self.source_token)
				self.value_tok_list = self.preprocessor.file_interface.RetokenizeContent(self.value_str,inherited_loc)
			else:
				self.value_tok_list = []

		return self.value_tok_list

	def ClearValue(self):
		self.value_tok_list = None
		self.value_str = ""

	def AppendStringToValue(self,str_value):
		if self.value_str == None:
			self.value_str = _pc_utils.TokListJoinValue(self.value_tok_list)
		self.value_str += str_value
		self.value_tok_list = None

	def ApeendTokenToValue(self,tok_tuple):
		self.GetValueAsTokens().append(tok_tuple);
		if self.value_str != None:
			self.value_str = None

	def RequiresArguments(self):
		if self.arguments_list != None:
			return True
		return False

	def CwStrip(self):
		tokens = self.GetValueAsTokens()
		new_tokens = [t for t in tokens if t[1] != _pc_utils.primitive_tokens.kComment and t[1] != _pc_utils.primitive_tokens.kWhitespace]
		self.value_tok_list = new_tokens

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