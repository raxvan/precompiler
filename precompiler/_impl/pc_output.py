
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
		#print(self.target.GetValueAsTokens());
		pass


###########################################################################################################

class CommentRemoval(PreprocessorAssemblerStack):
	def __init__(self, parent_assembler):
		PreprocessorAssemblerStack.__init__(self)
		self.parent_writer = parent_assembler



	def Write(self,tok_tuple):
		tok_type = tok_tuple[0]
		if (_pc_utils.isComment(tok_type) == True):
			start = value_str.find("\n")
			if start != -1:
				end = value_str.rfind("\n")
				self.parent_writer.Write(_pc_utils.primitive_tokens.kWhitespace,"\n" * (end - start + 1) + " " * (len(value_str) - end))
			else:
				self.parent_writer.Write(_pc_utils.primitive_tokens.kWhitespace," " * len(value_str))
		else:
			self.parent_writer.Write(tok_type,value_str)