
import precompiler._utils.pc_utils as _pc_utils


###########################################################################################################

class PreprocessorAssemblerStack(_pc_utils.SourceAssemblerStack):
	def __init__(self):
		_pc_utils.SourceAssemblerStack.__init__(self,None)

	def NextAssembler(self):
		return self.parent_writer

	def SetNextAssembler(self,asmb):
		self.parent_writer = asmb
		return self


class VarDefineValueAssembler(PreprocessorAssemblerStack):
	def __init__(self,target_define):
		PreprocessorAssemblerStack.__init__(self)
		self.target = target_define

	def Write(self,tok_tuple):
		self.target.ApeendTokenToValue(tok_tuple)

	def GetName(self):
		return self.target.name

	def Close(self):
		pass


###########################################################################################################

class CommentRemoval(PreprocessorAssemblerStack):
	def __init__(self, parent_assembler):
		PreprocessorAssemblerStack.__init__(self)
		self.parent_writer = parent_assembler

	def Write(self,tok_tuple):
		tok_type = tok_tuple[1]

		if (_pc_utils.isComment(tok_type) == True):
			_tok_value = tok_tuple[2]
			value_str = _tok_value[0]

			start = value_str.find("\n")
			if start != -1:
				end = value_str.rfind("\n")
				count = value_str.count("\n")
				self.parent_writer.Write( (0, _pc_utils.primitive_tokens.kWhitespace,["\n" * count + " " * (len(value_str) - end)]) )
			else:
				self.parent_writer.Write( (0, _pc_utils.primitive_tokens.kWhitespace,[" " * len(value_str)]) )
		else:
			self.parent_writer.Write(tok_tuple)