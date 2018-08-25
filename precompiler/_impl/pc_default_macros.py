

import precompiler._impl.pc_define as _impl_pc_define
import precompiler._utils.pc_utils as _pc_utils
import os

_PCVER_HIGH_ = 0
_PCVER_LOW0_ = 1
_PCVER_LOW1_ = 0

##############################################################################################################
class _builtin_macro(_impl_pc_define.MacroBase):
	def __init__(self, name, source_tok, preprocessor):
		_impl_pc_define.MacroBase.__init__(self,name,source_tok,preprocessor)

	def IsBuiltin(self):
		return True

	def GetValueAsTokens(self,tok):
		pass


##############################################################################################################
class macro__STRINGS__(_builtin_macro):
	def __init__(self, name, preprocessor):
		source_tok = ( 0, _pc_utils.primitive_tokens.kIdentifier, [name], ["<internal>",-1] )
		_builtin_macro.__init__(self,name,source_tok, preprocessor)

	def GetValueAsTokens(self,expand_tok):
		exp_location = _pc_utils.TokSource(expand_tok)
		value = '"' + _pc_utils.BoxStringHigh(self._GetStringValue()) + '"'
		result_token = ( _pc_utils.token_flags.k_trivial_flag, _pc_utils.primitive_tokens.kString, [value], exp_location )

		return [result_token]

class macro__NUMBER__(_builtin_macro):
	def __init__(self, name, preprocessor):
		source_tok = ( 0, _pc_utils.primitive_tokens.kIdentifier, [name], ["<internal>",-1] )
		_builtin_macro.__init__(self,name, source_tok,preprocessor)

	def GetValueAsTokens(self,expand_tok):
		exp_location = _pc_utils.TokSource(expand_tok)
		value = str(self._GetNumberValue(exp_location)) #TODO: make lexer number tokens actual numbers not string
		result_token = ( _pc_utils.token_flags.k_trivial_flag, _pc_utils.primitive_tokens.kNumber, [value], exp_location )

		return [result_token]

##############################################################################################################
class macro__FILE__(macro__STRINGS__):
	def __init__(self, preprocessor):
		macro__STRINGS__.__init__(self,"__FILE__",preprocessor)

	def _GetStringValue(self):
		return self.preprocessor.input_state.GetActiveSourceFile()

class macro__FILENAME__(macro__STRINGS__):
	def __init__(self, preprocessor):
		macro__STRINGS__.__init__(self,"__FILENAME__",preprocessor)

	def _GetStringValue(self):
		path = self.preprocessor.input_state.GetActiveSourceFile()
		(head, tail) = os.path.split(path)
		return tail

class macro__FILEROOT__(macro__STRINGS__):
	def __init__(self, preprocessor):
		macro__STRINGS__.__init__(self,"__FILEROOT__",preprocessor)

	def _GetStringValue(self):
		path = self.preprocessor.input_state.GetActiveSourceFile()
		(head, tail) = os.path.split(path)
		return head

class macro__PCVER__(macro__STRINGS__):
	def __init__(self, preprocessor):
		macro__STRINGS__.__init__(self,"__PCVER__",preprocessor)

	def _GetStringValue(self):
		return str(_PCVER_HIGH_) + "." + str(_PCVER_LOW0_) + "." + str(_PCVER_LOW1_)

class macro__PCVER_HIGH__(macro__NUMBER__):
	def __init__(self, preprocessor):
		macro__NUMBER__.__init__(self,"__PCVER_HIGH__",preprocessor)

	def _GetNumberValue(self,_):
		return _PCVER_HIGH_

class macro__PCVER_LOW__(macro__NUMBER__):
	def __init__(self, preprocessor):
		macro__NUMBER__.__init__(self,"__PCVER_LOW__",preprocessor)

	def _GetNumberValue(self,_):
		return _PCVER_LOW0_ + _PCVER_LOW1_ / 10.0;

class macro__LINE__(macro__NUMBER__):
	def __init__(self, preprocessor):
		macro__NUMBER__.__init__(self,"__LINE__",preprocessor)

	def _GetNumberValue(self,location):
		return location[1] + 1 #+1 because lines are 0 based from lexer

